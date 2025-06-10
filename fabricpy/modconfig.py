# fabricpy/modconfig.py
"""
Generates a ready-to-build Fabric mod project on disk.

* clones (or re-uses) the Fabric example-mod template repository
* rewrites fabric.mod.json with your metadata
* generates Java for:
      – items & food items
      – **custom ItemGroups** (creative-inventory tabs)
      – blocks (with BlockItems)
* patches ExampleMod.java so those registries run at game-init
* copies textures & writes model / blockstate JSON files
* writes / merges language (en_us.json) entries for items, blocks & tabs
* **NEW:** writes any Recipe JSON attached to an Item, FoodItem or Block
* **NEW:** supports `build()` to produce the mod JAR, and `run()` to launch
            a development client via Gradle.

Tested against **Minecraft 1.21.5 + Fabric-API 0.119.5**.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from collections import defaultdict
from typing import Dict, List, Set

from .fooditem import FoodItem
from .itemgroup import ItemGroup
from .recipejson import RecipeJson


# --------------------------------------------------------------------- #
#                             ModConfig                                 #
# --------------------------------------------------------------------- #
class ModConfig:
    # ------------------------------------------------------------------ #
    # construction / registration                                        #
    # ------------------------------------------------------------------ #

    def __init__(
        self,
        mod_id: str,
        name: str,
        description: str,
        version: str,
        authors: List[str] | tuple[str, ...],
        project_dir: str = "my-fabric-mod",
        template_repo: str = "https://github.com/FabricMC/fabric-example-mod.git",
    ):
        self.mod_id = mod_id
        self.name = name
        self.description = description
        self.version = version
        self.authors = list(authors)
        self.project_dir = project_dir
        self.template_repo = template_repo

        self.registered_items: List = []  # Item or FoodItem
        self.registered_blocks: List = []  # Block

    # public helpers --------------------------------------------------- #

    def registerItem(self, item):  # noqa: N802
        self.registered_items.append(item)

    def registerFoodItem(self, food_item: FoodItem):  # noqa: N802
        self.registered_items.append(food_item)

    def registerBlock(self, block):  # noqa: N802
        self.registered_blocks.append(block)

    # ------------------------------------------------------------------ #
    # helper for creating valid Java identifiers                        #
    # ------------------------------------------------------------------ #

    def _to_java_constant(self, id_string: str) -> str:
        """Convert an item/block/group ID to a valid Java constant name.
        
        Replaces invalid characters (like : - .) with underscores and converts to uppercase.
        """
        # Replace common invalid characters with underscores
        valid_name = re.sub(r'[:\-\.\s]+', '_', id_string)
        # Remove any remaining non-alphanumeric characters except underscores
        valid_name = re.sub(r'[^a-zA-Z0-9_]', '', valid_name)
        # Ensure it doesn't start with a digit
        if valid_name and valid_name[0].isdigit():
            valid_name = '_' + valid_name
        return valid_name.upper()

    # ------------------------------------------------------------------ #
    # main compile routine                                               #
    # ------------------------------------------------------------------ #

    def compile(self):
        # 1) clone example-mod template ---------------------------------
        if not os.path.exists(self.project_dir):
            self.clone_repository(self.template_repo, self.project_dir)
        else:
            print(f"Directory `{self.project_dir}` already exists – skipping clone.")

        # 2) patch fabric.mod.json --------------------------------------
        meta_path = os.path.join(
            self.project_dir, "src", "main", "resources", "fabric.mod.json"
        )
        self.update_mod_metadata(
            meta_path,
            {
                "id": self.mod_id,
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "authors": self.authors,
            },
        )

        # 3) items / tabs ------------------------------------------------
        item_pkg = f"com.example.{self.mod_id}.items"
        self.create_item_files(self.project_dir, item_pkg)
        self.create_item_group_files(self.project_dir, item_pkg)
        self.update_mod_initializer(self.project_dir, item_pkg)
        self.update_mod_initializer_itemgroups(self.project_dir, item_pkg)
        self.copy_texture_and_generate_models(self.project_dir, self.mod_id)
        self.update_item_lang_file(self.project_dir, self.mod_id)
        self.update_item_group_lang_entries(self.project_dir, self.mod_id)

        # 3b) recipe JSONs ----------------------------------------------
        self.write_recipe_files(self.project_dir, self.mod_id)

        # 4) blocks ------------------------------------------------------
        if self.registered_blocks:
            blk_pkg = f"com.example.{self.mod_id}.blocks"
            self.create_block_files(self.project_dir, blk_pkg)
            self.update_mod_initializer_blocks(self.project_dir, blk_pkg)
            self.copy_block_textures_and_generate_models(self.project_dir, self.mod_id)
            self.update_block_lang_file(self.project_dir, self.mod_id)

        print("\n🎉  Mod project compilation complete.")

    # ------------------------------------------------------------------ #
    # git helper                                                         #
    # ------------------------------------------------------------------ #

    def clone_repository(self, repo_url, dst):
        print(f"Cloning template into `{dst}` …")
        subprocess.check_call(["git", "clone", repo_url, dst])
        print("Template cloned.\n")

    # ------------------------------------------------------------------ #
    # fabric.mod.json helper                                             #
    # ------------------------------------------------------------------ #

    def update_mod_metadata(self, path, data):
        if not os.path.exists(path):
            raise FileNotFoundError("fabric.mod.json not found")

        with open(path, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
        meta.update(data)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)
        print("Updated fabric.mod.json\n")

    # ------------------------------------------------------------------ #
    #                       NEW  –  RECIPE FILES                         #
    # ------------------------------------------------------------------ #

    def write_recipe_files(self, project_dir: str, mod_id: str) -> None:
        """
        Write each RecipeJson attached to any registered object into

            data/<mod>/recipe/<filename>.json   (singular folder since 1.21)

        The file-name must NOT contain a namespace; if the result id is
        namespaced (e.g. "testmod:poison_apple"), only the path part is used.
        """
        objs = [
            *[i for i in self.registered_items if getattr(i, "recipe", None)],
            *[b for b in self.registered_blocks if getattr(b, "recipe", None)],
        ]
        if not objs:
            return

        base = os.path.join(
            project_dir, "src", "main", "resources", "data", mod_id, "recipe"
        )
        os.makedirs(base, exist_ok=True)

        for obj in objs:
            r: RecipeJson = obj.recipe  # type: ignore[attr-defined]
            identifier = r.result_id or obj.id
            filename = identifier.split(":", 1)[-1] + ".json"
            path = os.path.join(base, filename)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(r.text)
            print(f"  ✔ wrote recipe → {os.path.relpath(path, project_dir)}")

    # ================================================================== #
    #                          ITEMS  &  FOOD                            #
    # ================================================================== #

    # ---------- Java source generation -------------------------------- #

    def create_item_files(self, project_dir, package_path):
        java_src = os.path.join(project_dir, "src", "main", "java")
        pkg_dir = os.path.join(java_src, *package_path.split("."))
        os.makedirs(pkg_dir, exist_ok=True)

        with open(
            os.path.join(pkg_dir, "TutorialItems.java"), "w", encoding="utf-8"
        ) as fh:
            fh.write(self._tutorial_items_src(package_path))

        with open(
            os.path.join(pkg_dir, "CustomItem.java"), "w", encoding="utf-8"
        ) as fh:
            fh.write(self._custom_item_src(package_path))

    def _tutorial_items_src(self, pkg: str) -> str:
        has_food = any(isinstance(i, FoodItem) for i in self.registered_items)
        has_vanila = any(
            isinstance(getattr(i, "item_group", None), str)
            for i in self.registered_items
        )

        L: List[str] = []
        L.append(f"package {pkg};\n")
        L.append("import net.minecraft.item.Item;")
        if has_food:
            L.append("import net.minecraft.component.type.FoodComponent;")
        L.append("import net.minecraft.util.Identifier;")
        L.append("import net.minecraft.registry.Registry;")
        L.append("import net.minecraft.registry.RegistryKey;")
        L.append("import net.minecraft.registry.RegistryKeys;")
        L.append("import net.minecraft.registry.Registries;")
        if has_vanila:
            L.append("import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;")
            L.append("import net.minecraft.item.ItemGroups;")
        L.append("import java.util.function.Function;\n")
        L.append("public final class TutorialItems {")
        L.append("    private TutorialItems() {}\n")

        for itm in self.registered_items:
            const = self._to_java_constant(itm.id)
            if isinstance(itm, FoodItem):
                b = [
                    f".nutrition({itm.nutrition})",
                    f".saturationModifier({itm.saturation}f)",
                ]
                if itm.always_edible:
                    b.append(".alwaysEdible()")
                settings = (
                    "new Item.Settings()"
                    f".food(new FoodComponent.Builder(){''.join(b)}.build())"
                    f".maxCount({itm.max_stack_size})"
                )
                factory = "Item::new"
            else:
                settings = f"new Item.Settings().maxCount({itm.max_stack_size})"
                factory = "CustomItem::new"
            
            # Extract just the path part if the ID is namespaced
            item_path = itm.id.split(":", 1)[-1]
            L.append(
                f'    public static final Item {const} = register("{item_path}", '
                f"{factory}, {settings});"
            )
        L.append("")
        L.append(
            "    private static Item register(String path, "
            "Function<Item.Settings, Item> factory, Item.Settings settings) {"
        )
        L.append(
            f'        RegistryKey<Item> key = RegistryKey.of(RegistryKeys.ITEM, Identifier.of("{self.mod_id}", path));'
        )
        L.append("        settings = settings.registryKey(key);")
        L.append(
            f'        return Registry.register(Registries.ITEM, Identifier.of("{self.mod_id}", path), factory.apply(settings));'
        )
        L.append("    }\n")
        L.append("    public static void initialize() {")
        if has_vanila:
            groups: Dict[str, List[str]] = defaultdict(list)
            for itm in self.registered_items:
                if isinstance(itm.item_group, str):
                    groups[itm.item_group].append(self._to_java_constant(itm.id))
            for g, consts in groups.items():
                L.append(
                    f"        ItemGroupEvents.modifyEntriesEvent(ItemGroups.{g}).register(e -> {{"
                )
                for c in consts:
                    L.append(f"            e.add({c});")
                L.append("        });")
        L.append("    }")
        L.append("}")
        return "\n".join(L)

    def _custom_item_src(self, pkg: str) -> str:
        return f"""package {pkg};

import net.minecraft.item.Item;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.sound.SoundEvents;
import net.minecraft.sound.SoundCategory;
import net.minecraft.world.World;

public class CustomItem extends Item {{
    public CustomItem(Settings settings) {{ super(settings); }}

    @Override
    public ActionResult use(World world, PlayerEntity user, Hand hand) {{
        if (!world.isClient()) {{
            world.playSound(null, user.getBlockPos(),
                    SoundEvents.BLOCK_WOOL_BREAK, SoundCategory.PLAYERS, 1F, 1F);
        }}
        return ActionResult.SUCCESS;
    }}
}}
"""

    # ================================================================== #
    #                      CUSTOM   ITEM   GROUPS                        #
    # ================================================================== #

    @property
    def _custom_groups(self) -> Set[ItemGroup]:
        groups: Set[ItemGroup] = set()
        for itm in self.registered_items:
            if isinstance(itm.item_group, ItemGroup):
                groups.add(itm.item_group)
        for blk in self.registered_blocks:
            if isinstance(blk.item_group, ItemGroup):
                groups.add(blk.item_group)
        return groups

    def create_item_group_files(self, project_dir, package_path):
        if not self._custom_groups:
            return
        java_src = os.path.join(project_dir, "src", "main", "java")
        pkg_dir = os.path.join(java_src, *package_path.split("."))
        os.makedirs(pkg_dir, exist_ok=True)
        with open(
            os.path.join(pkg_dir, "TutorialItemGroups.java"), "w", encoding="utf-8"
        ) as fh:
            fh.write(self._tutorial_itemgroups_src(package_path))

    def _tutorial_itemgroups_src(self, pkg: str) -> str:
        blocks_referenced = any(
            isinstance(blk.item_group, ItemGroup) for blk in self.registered_blocks
        )

        L: List[str] = []
        L.append(f"package {pkg};\n")
        L.append("import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;")
        L.append("import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;")
        L.append("import net.minecraft.item.ItemGroup;")
        L.append("import net.minecraft.item.ItemStack;")
        L.append("import net.minecraft.registry.Registry;")
        L.append("import net.minecraft.registry.RegistryKey;")
        L.append("import net.minecraft.registry.RegistryKeys;")
        L.append("import net.minecraft.registry.Registries;")
        L.append("import net.minecraft.util.Identifier;")
        L.append("import net.minecraft.text.Text;")
        if blocks_referenced:
            L.append(f"import com.example.{self.mod_id}.blocks.TutorialBlocks;")
        L.append("\npublic final class TutorialItemGroups {")
        L.append("    private TutorialItemGroups() {}\n")

        group_entries: Dict[ItemGroup, List[str]] = defaultdict(list)
        for itm in self.registered_items:
            if isinstance(itm.item_group, ItemGroup):
                group_entries[itm.item_group].append(f"TutorialItems.{self._to_java_constant(itm.id)}")
        for blk in self.registered_blocks:
            if isinstance(blk.item_group, ItemGroup):
                group_entries[blk.item_group].append(
                    f"TutorialBlocks.{self._to_java_constant(blk.id)}.asItem()"
                )

        for grp in self._custom_groups:
            const = self._to_java_constant(grp.id)
            L.append(
                f"    public static final RegistryKey<ItemGroup> {const}_KEY = "
                f'RegistryKey.of(RegistryKeys.ITEM_GROUP, Identifier.of("{self.mod_id}", "{grp.id}"));'
            )
            icon_expr = (
                f"TutorialItems.{self._to_java_constant(grp.icon_item_id)}"
                if grp.icon_item_id
                else group_entries[grp][0]
            )
            L.append(
                f"    public static final ItemGroup {const} = FabricItemGroup.builder()\n"
                f"        .icon(() -> new ItemStack({icon_expr}))\n"
                f'        .displayName(Text.translatable("itemGroup.{self.mod_id}.{grp.id}"))\n'
                "        .build();\n"
            )

        L.append("    public static void initialize() {")
        for grp in self._custom_groups:
            const = self._to_java_constant(grp.id)
            L.append(
                f"        Registry.register(Registries.ITEM_GROUP, {const}_KEY, {const});"
            )
            L.append(
                f"        ItemGroupEvents.modifyEntriesEvent({const}_KEY).register(e -> {{"
            )
            for expr in group_entries[grp]:
                L.append(f"            e.add({expr});")
            L.append("        });")
        L.append("    }\n}")
        return "\n".join(L)

    # ================================================================== #
    #        INITIALIZER PATCHES                                         #
    # ================================================================== #

    def update_mod_initializer(self, project_dir, pkg):
        self._patch_initializer(project_dir, f"{pkg}.TutorialItems.initialize();")

    def update_mod_initializer_itemgroups(self, project_dir, pkg):
        if self._custom_groups:
            self._patch_initializer(
                project_dir, f"{pkg}.TutorialItemGroups.initialize();"
            )

    def update_mod_initializer_blocks(self, project_dir, pkg):
        self._patch_initializer(project_dir, f"{pkg}.TutorialBlocks.initialize();")

    def _patch_initializer(self, project_dir, line: str):
        paths = [
            os.path.join(
                project_dir, "src", "main", "java", "com", "example", "ExampleMod.java"
            ),
            os.path.join(
                project_dir,
                "src",
                "main",
                "resources",
                "java",
                "com",
                "example",
                "ExampleMod.java",
            ),
        ]
        init = next((p for p in paths if os.path.exists(p)), None)
        if not init:
            print("WARNING: ExampleMod.java not found – cannot patch initializer.")
            return
        with open(init, "r", encoding="utf-8") as fh:
            txt = fh.read()
        if line in txt:
            return
        patched, n = re.subn(
            r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)",
            r"\1\n        " + line,
            txt,
            1,
        )
        if n:
            with open(init, "w", encoding="utf-8") as fh:
                fh.write(patched)
            print(f"Patched ExampleMod.java – added `{line.strip()}`.")

    # ================================================================== #
    #     COPY TEXTURES / MODELS / LANG (ITEMS & GROUP TRANSLATIONS)     #
    # ================================================================== #

    def copy_texture_and_generate_models(self, project_dir, mod_id):
        assets = os.path.join(project_dir, "src", "main", "resources", "assets", mod_id)
        tex_dir = os.path.join(assets, "textures", "item")
        mdl_dir = os.path.join(assets, "models", "item")
        idef_dir = os.path.join(assets, "items")
        for d in (tex_dir, mdl_dir, idef_dir):
            os.makedirs(d, exist_ok=True)

        for itm in self.registered_items:
            if not itm.texture_path or not os.path.exists(itm.texture_path):
                print(f"SKIP texture for `{itm.id}`")
                continue
            
            # Extract just the path part if the ID is namespaced
            item_path = itm.id.split(":", 1)[-1]
            
            shutil.copy(itm.texture_path, os.path.join(tex_dir, f"{item_path}.png"))
            with open(
                os.path.join(mdl_dir, f"{item_path}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "parent": "minecraft:item/generated",
                        "textures": {"layer0": f"{mod_id}:item/{item_path}"},
                    },
                    fh,
                    indent=2,
                )
            with open(
                os.path.join(idef_dir, f"{item_path}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "model": {
                            "type": "minecraft:model",
                            "model": f"{mod_id}:item/{item_path}",
                        }
                    },
                    fh,
                    indent=2,
                )

    def update_item_lang_file(self, project_dir, mod_id):
        lang_dir = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id, "lang"
        )
        os.makedirs(lang_dir, exist_ok=True)
        path = os.path.join(lang_dir, "en_us.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = {}
        for itm in self.registered_items:
            # Extract just the path part if the ID is namespaced
            item_path = itm.id.split(":", 1)[-1]
            data[f"item.{mod_id}.{item_path}"] = itm.name
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def update_item_group_lang_entries(self, project_dir, mod_id):
        if not self._custom_groups:
            return
        lang_dir = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id, "lang"
        )
        os.makedirs(lang_dir, exist_ok=True)
        path = os.path.join(lang_dir, "en_us.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = {}
        for grp in self._custom_groups:
            data[f"itemGroup.{mod_id}.{grp.id}"] = grp.name
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    # ================================================================== #
    #                                BLOCKS                              #
    # ================================================================== #

    # ---------- Java source generation -------------------------------- #

    def create_block_files(self, project_dir, package_path):
        java_src = os.path.join(project_dir, "src", "main", "java")
        pkg_dir = os.path.join(java_src, *package_path.split("."))
        os.makedirs(pkg_dir, exist_ok=True)
        with open(
            os.path.join(pkg_dir, "TutorialBlocks.java"), "w", encoding="utf-8"
        ) as fh:
            fh.write(self._tutorial_blocks_src(package_path))
        with open(
            os.path.join(pkg_dir, "CustomBlock.java"), "w", encoding="utf-8"
        ) as fh:
            fh.write(self._custom_block_src(package_path))

    def _tutorial_blocks_src(self, pkg: str) -> str:
        has_vanila = any(
            isinstance(getattr(b, "item_group", None), str)
            for b in self.registered_blocks
        )
        L: List[str] = []
        L.append(f"package {pkg};\n")
        L.append("import net.minecraft.block.Block;")
        L.append("import net.minecraft.block.AbstractBlock;")
        L.append("import net.minecraft.block.Blocks;")
        L.append("import net.minecraft.item.BlockItem;")
        L.append("import net.minecraft.item.Item;")
        L.append("import net.minecraft.util.Identifier;")
        L.append("import net.minecraft.registry.Registry;")
        L.append("import net.minecraft.registry.RegistryKey;")
        L.append("import net.minecraft.registry.RegistryKeys;")
        L.append("import net.minecraft.registry.Registries;")
        if has_vanila:
            L.append("import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;")
            L.append("import net.minecraft.item.ItemGroups;")
        L.append("import java.util.function.Function;\n")
        L.append("public final class TutorialBlocks {")
        L.append("    private TutorialBlocks() {}\n")
        for blk in self.registered_blocks:
            const = self._to_java_constant(blk.id)
            # Extract just the path part if the ID is namespaced
            block_path = blk.id.split(":", 1)[-1]
            L.append(
                f'    public static final Block {const} = register("{block_path}", '
                f"CustomBlock::new, AbstractBlock.Settings.copy(Blocks.STONE).requiresTool(), true);"
            )
        L.append("")
        L.append(
            "    private static Block register(String p, Function<AbstractBlock.Settings, Block> f, "
            "AbstractBlock.Settings s, boolean makeItem) {"
        )
        L.append(
            f'        RegistryKey<Block> bKey = RegistryKey.of(RegistryKeys.BLOCK, Identifier.of("{self.mod_id}", p));'
        )
        L.append("        s = s.registryKey(bKey);")
        L.append(
            f'        Block b = Registry.register(Registries.BLOCK, Identifier.of("{self.mod_id}", p), f.apply(s));'
        )
        L.append("        if (makeItem) {")
        L.append(
            f'            Registry.register(Registries.ITEM, Identifier.of("{self.mod_id}", p), '
            "new BlockItem(b, new Item.Settings().registryKey("
            "RegistryKey.of(RegistryKeys.ITEM, Identifier.of("
            f'"{self.mod_id}", p)))));'
        )
        L.append("        }")
        L.append("        return b;")
        L.append("    }\n")
        L.append("    public static void initialize() {")
        if has_vanila:
            groups: Dict[str, List[str]] = defaultdict(list)
            for blk in self.registered_blocks:
                if isinstance(blk.item_group, str):
                    groups[blk.item_group].append(self._to_java_constant(blk.id))
            for g, consts in groups.items():
                L.append(
                    f"        ItemGroupEvents.modifyEntriesEvent(ItemGroups.{g}).register(e -> {{"
                )
                for c in consts:
                    L.append(f"            e.add({c}.asItem());")
                L.append("        });")
        L.append("    }")
        L.append("}")
        return "\n".join(L)

    def _custom_block_src(self, pkg: str) -> str:
        return f"""package {pkg};

import net.minecraft.block.Block;
import net.minecraft.block.AbstractBlock;

public class CustomBlock extends Block {{
    public CustomBlock(AbstractBlock.Settings s) {{ super(s); }}
}}
"""

    # ---------- textures / model JSON / lang (blocks) ------------------ #

    def copy_block_textures_and_generate_models(self, project_dir, mod_id):
        assets = os.path.join(project_dir, "src", "main", "resources", "assets", mod_id)
        blk_tex_dir = os.path.join(assets, "textures", "block")
        blk_mdl_dir = os.path.join(assets, "models", "block")
        blkstate_dir = os.path.join(assets, "blockstates")
        itm_tex_dir = os.path.join(assets, "textures", "item")
        itm_mdl_dir = os.path.join(assets, "models", "item")
        itm_def_dir = os.path.join(assets, "items")

        for d in (
            blk_tex_dir,
            blk_mdl_dir,
            blkstate_dir,
            itm_tex_dir,
            itm_mdl_dir,
            itm_def_dir,
        ):
            os.makedirs(d, exist_ok=True)

        for blk in self.registered_blocks:
            if not blk.block_texture_path or not os.path.exists(blk.block_texture_path):
                print(f"SKIP block `{blk.id}` – missing texture")
                continue

            # Extract just the path part if the ID is namespaced
            block_path = blk.id.split(":", 1)[-1]

            shutil.copy(
                blk.block_texture_path, os.path.join(blk_tex_dir, f"{block_path}.png")
            )

            with open(
                os.path.join(blk_mdl_dir, f"{block_path}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "parent": "minecraft:block/cube_all",
                        "textures": {"all": f"{mod_id}:block/{block_path}"},
                    },
                    fh,
                    indent=2,
                )

            with open(
                os.path.join(blkstate_dir, f"{block_path}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {"variants": {"": {"model": f"{mod_id}:block/{block_path}"}}},
                    fh,
                    indent=2,
                )

            inv_src = (
                blk.inventory_texture_path
                if blk.inventory_texture_path
                and os.path.exists(blk.inventory_texture_path)
                else blk.block_texture_path
            )
            shutil.copy(inv_src, os.path.join(itm_tex_dir, f"{block_path}.png"))

            with open(
                os.path.join(itm_mdl_dir, f"{block_path}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "parent": "minecraft:item/generated",
                        "textures": {"layer0": f"{mod_id}:item/{block_path}"},
                    },
                    fh,
                    indent=2,
                )

            with open(
                os.path.join(itm_def_dir, f"{block_path}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "model": {
                            "type": "minecraft:model",
                            "model": f"{mod_id}:item/{block_path}",
                        }
                    },
                    fh,
                    indent=2,
                )

    def update_block_lang_file(self, project_dir, mod_id):
        lang_dir = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id, "lang"
        )
        os.makedirs(lang_dir, exist_ok=True)
        path = os.path.join(lang_dir, "en_us.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = {}
        for blk in self.registered_blocks:
            # Extract just the path part if the ID is namespaced
            block_path = blk.id.split(":", 1)[-1]
            data[f"block.{mod_id}.{block_path}"] = blk.name
            data[f"item.{mod_id}.{block_path}"] = blk.name
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    # ------------------------------------------------------------------ #
    # new build / run helpers                                            #
    # ------------------------------------------------------------------ #

    def build(self):
        """
        Requires compile() to have been called first.
        Enters the mod project directory and runs `./gradlew build`
        to produce the distributable JAR.
        """
        if not os.path.isdir(self.project_dir):
            raise RuntimeError("Project directory not found – call compile() first.")
        print("🔨 Building mod JAR …")
        subprocess.check_call(["./gradlew", "build"], cwd=self.project_dir)
        print("✔ Build complete – JAR written to build/libs/")

    def run(self):
        """
        Requires compile() to have been called first.
        Enters the mod project directory and runs `./gradlew runClient`
        to launch a dev Minecraft instance with your mod.
        """
        if not os.path.isdir(self.project_dir):
            raise RuntimeError("Project directory not found – call compile() first.")
        print("🚀 Running mod in development client …")
        subprocess.check_call(["./gradlew", "runClient"], cwd=self.project_dir)
