# fabricpy/modconfig.py
"""
Generates a ready‑to‑build Fabric mod project.

* clones / re‑uses a template repo
* rewrites fabric.mod.json
* generates Java for items, food items, and blocks
* patches ExampleMod.java to call the generated registries
* copies textures & writes model/blockstate JSON
* updates language files
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess

from .fooditem import FoodItem


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
        authors: list[str] | tuple[str, ...],
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

        self.registered_items: list = []  # Item or FoodItem
        self.registered_blocks: list = []  # Block

    # public helpers ----------------------------------------------------- #

    def registerItem(self, item):
        self.registered_items.append(item)

    def registerFoodItem(self, food_item: FoodItem):
        self.registered_items.append(food_item)

    def registerBlock(self, block):
        self.registered_blocks.append(block)

    # ------------------------------------------------------------------ #
    # main compile routine                                               #
    # ------------------------------------------------------------------ #

    def compile(self):
        if not os.path.exists(self.project_dir):
            self.clone_repository(self.template_repo, self.project_dir)
        else:
            print(f"Directory `{self.project_dir}` already exists – skipping clone.")

        # fabric.mod.json --------------------------------------------------
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

        # items / food -----------------------------------------------------
        item_pkg = f"com.example.{self.mod_id}.items"
        self.create_item_files(self.project_dir, item_pkg)
        self.update_mod_initializer(self.project_dir, item_pkg)
        self.copy_texture_and_generate_models(self.project_dir, self.mod_id)
        self.update_item_lang_file(self.project_dir, self.mod_id)

        # blocks -----------------------------------------------------------
        if self.registered_blocks:
            blk_pkg = f"com.example.{self.mod_id}.blocks"
            self.create_block_files(self.project_dir, blk_pkg)
            self.update_mod_initializer_blocks(self.project_dir, blk_pkg)
            self.copy_block_textures_and_generate_models(self.project_dir, self.mod_id)
            self.update_block_lang_file(self.project_dir, self.mod_id)

        print("\n🎉  Mod project compilation complete.")

    # ------------------------------------------------------------------ #
    # low‑level helpers                                                  #
    # ------------------------------------------------------------------ #

    def clone_repository(self, repo_url, dst):
        print(f"Cloning template into `{dst}` …")
        subprocess.check_call(["git", "clone", repo_url, dst])
        print("Template cloned.\n")

    def update_mod_metadata(self, path, data):
        if not os.path.exists(path):
            raise FileNotFoundError("fabric.mod.json not found")

        with open(path, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
        meta.update(data)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2)
        print("Updated fabric.mod.json\n")

    # =============================== ITEMS ============================= #

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

    # ------------------------------------------------------------------ #

    def _tutorial_items_src(self, pkg: str) -> str:
        has_food = any(isinstance(i, FoodItem) for i in self.registered_items)
        has_groups = any(getattr(i, "item_group", None) for i in self.registered_items)

        l = []
        l.append(f"package {pkg};\n")
        l.append("import net.minecraft.item.Item;")
        if has_food:
            l.append("import net.minecraft.component.type.FoodComponent;")
        l.append("import net.minecraft.util.Identifier;")
        l.append("import net.minecraft.registry.Registry;")
        l.append("import net.minecraft.registry.RegistryKey;")
        l.append("import net.minecraft.registry.RegistryKeys;")
        l.append("import net.minecraft.registry.Registries;")
        if has_groups:
            l.append("import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;")
            l.append("import net.minecraft.item.ItemGroups;")
        l.append("import java.util.function.Function;\n")
        l.append("public final class TutorialItems {")
        l.append("    private TutorialItems() {}\n")

        for itm in self.registered_items:
            const = itm.id.upper()
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
                factory = "Item::new"  # vanilla Item for food items
            else:
                settings = f"new Item.Settings().maxCount({itm.max_stack_size})"
                factory = "CustomItem::new"

            l.append(
                f'    public static final Item {const} = register("{itm.id}", '
                f"{factory}, {settings});"
            )
        l.append("")
        l.append(
            "    private static Item register(String path, "
            "Function<Item.Settings, Item> factory, Item.Settings settings) {"
        )
        l.append(
            f"        RegistryKey<Item> key = RegistryKey.of(RegistryKeys.ITEM, "
            f'Identifier.of("{self.mod_id}", path));'
        )
        l.append("        settings = settings.registryKey(key);")
        l.append(
            f"        return Registry.register(Registries.ITEM, "
            f'Identifier.of("{self.mod_id}", path), factory.apply(settings));'
        )
        l.append("    }\n")
        l.append("    public static void initialize() {")
        if has_groups:
            groups: dict[str, list[str]] = {}
            for itm in self.registered_items:
                if getattr(itm, "item_group", None):
                    groups.setdefault(itm.item_group, []).append(itm.id.upper())
            for g, consts in groups.items():
                l.append(
                    f"        ItemGroupEvents.modifyEntriesEvent(ItemGroups.{g})"
                    ".register(e -> {"
                )
                for c in consts:
                    l.append(f"            e.add({c});")
                l.append("        });")
        l.append("    }")
        l.append("}")
        return "\n".join(l)

    # ------------------------------------------------------------------ #

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

    # ---------------- ExampleMod.java patch ---------------------------- #

    def update_mod_initializer(self, project_dir, pkg):
        self._patch_initializer(
            project_dir, f"{pkg}.TutorialItems.initialize();", "items"
        )

    def update_mod_initializer_blocks(self, project_dir, pkg):
        self._patch_initializer(
            project_dir, f"{pkg}.TutorialBlocks.initialize();", "blocks"
        )

    def _patch_initializer(self, project_dir, line, kind):
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
            print(f"WARNING: ExampleMod.java not found – cannot patch {kind}.")
            return
        with open(init, "r", encoding="utf-8") as fh:
            txt = fh.read()
        if line in txt:
            return
        new, n = re.subn(
            r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)",
            r"\1\n        " + line,
            txt,
            1,
        )
        if n:
            with open(init, "w", encoding="utf-8") as fh:
                fh.write(new)
            print(f"Patched ExampleMod.java for {kind}.")
        else:
            print(f"WARNING: could not patch ExampleMod.java for {kind}.")

    # ---------- copy textures, model JSON, lang (items) ---------------- #

    def copy_texture_and_generate_models(self, project_dir, mod_id):
        assets = os.path.join(project_dir, "src", "main", "resources", "assets", mod_id)
        tex = os.path.join(assets, "textures", "item")
        mdl = os.path.join(assets, "models", "item")
        idef = os.path.join(assets, "items")
        for d in (tex, mdl, idef):
            os.makedirs(d, exist_ok=True)

        for itm in self.registered_items:
            if not itm.texture_path or not os.path.exists(itm.texture_path):
                print(f"SKIP texture for `{itm.id}`")
                continue
            shutil.copy(itm.texture_path, os.path.join(tex, f"{itm.id}.png"))
            with open(os.path.join(mdl, f"{itm.id}.json"), "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "parent": "minecraft:item/generated",
                        "textures": {"layer0": f"{mod_id}:item/{itm.id}"},
                    },
                    fh,
                    indent=2,
                )
            with open(
                os.path.join(idef, f"{itm.id}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "model": {
                            "type": "minecraft:model",
                            "model": f"{mod_id}:item/{itm.id}",
                        }
                    },
                    fh,
                    indent=2,
                )

    def update_item_lang_file(self, project_dir, mod_id):
        lang = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id, "lang"
        )
        os.makedirs(lang, exist_ok=True)
        path = os.path.join(lang, "en_us.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = {}
        for itm in self.registered_items:
            data[f"item.{mod_id}.{itm.id}"] = itm.name
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    # =============================== BLOCKS ============================ #

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
        has_groups = any(getattr(b, "item_group", None) for b in self.registered_blocks)
        l = []
        l.append(f"package {pkg};\n")
        l.append("import net.minecraft.block.Block;")
        l.append("import net.minecraft.block.AbstractBlock;")
        l.append("import net.minecraft.block.Blocks;")
        l.append("import net.minecraft.item.BlockItem;")
        l.append("import net.minecraft.item.Item;")
        l.append("import net.minecraft.util.Identifier;")
        l.append("import net.minecraft.registry.Registry;")
        l.append("import net.minecraft.registry.RegistryKey;")
        l.append("import net.minecraft.registry.RegistryKeys;")
        l.append("import net.minecraft.registry.Registries;")
        if has_groups:
            l.append("import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;")
            l.append("import net.minecraft.item.ItemGroups;")
        l.append("import java.util.function.Function;\n")
        l.append("public final class TutorialBlocks {")
        l.append("    private TutorialBlocks() {}\n")
        for b in self.registered_blocks:
            const = b.id.upper()
            l.append(
                f'    public static final Block {const} = register("{b.id}", '
                f"CustomBlock::new, AbstractBlock.Settings.copy(Blocks.STONE)"
                ".requiresTool(), true);"
            )
        l.append("")
        l.append(
            "    private static Block register(String p, "
            "Function<AbstractBlock.Settings, Block> f, "
            "AbstractBlock.Settings s, boolean item) {"
        )
        l.append(
            f"        RegistryKey<Block> bk = RegistryKey.of(RegistryKeys.BLOCK, "
            f'Identifier.of("{self.mod_id}", p));'
        )
        l.append("        s = s.registryKey(bk);")
        l.append(
            f"        Block b = Registry.register(Registries.BLOCK, "
            f'Identifier.of("{self.mod_id}", p), f.apply(s));'
        )
        l.append("        if (item) {")
        l.append(
            f'            Registry.register(Registries.ITEM, Identifier.of("{self.mod_id}", p), '
            "new BlockItem(b, new Item.Settings().registryKey("
            "RegistryKey.of(RegistryKeys.ITEM, Identifier.of("
            f'"{self.mod_id}", p)))));'
        )
        l.append("        }")
        l.append("        return b;")
        l.append("    }\n")
        l.append("    public static void initialize() {")
        if has_groups:
            groups: dict[str, list[str]] = {}
            for b in self.registered_blocks:
                if getattr(b, "item_group", None):
                    groups.setdefault(b.item_group, []).append(b.id.upper())
            for g, consts in groups.items():
                l.append(
                    f"        ItemGroupEvents.modifyEntriesEvent(ItemGroups.{g})"
                    ".register(e -> {"
                )
                for c in consts:
                    l.append(f"            e.add({c}.asItem());")
                l.append("        });")
        l.append("    }")
        l.append("}")
        return "\n".join(l)

    def _custom_block_src(self, pkg: str) -> str:
        return f"""package {pkg};

import net.minecraft.block.Block;
import net.minecraft.block.AbstractBlock;

public class CustomBlock extends Block {{
    public CustomBlock(AbstractBlock.Settings s) {{ super(s); }}
}}
"""

    # ---------- inject initialize() call into ExampleMod.java ----------- #

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
            if not (blk.block_texture_path and os.path.exists(blk.block_texture_path)):
                print(f"SKIP block `{blk.id}` – missing texture")
                continue

            # block texture
            shutil.copy(
                blk.block_texture_path, os.path.join(blk_tex_dir, f"{blk.id}.png")
            )

            # block model
            with open(
                os.path.join(blk_mdl_dir, f"{blk.id}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "parent": "minecraft:block/cube_all",
                        "textures": {"all": f"{mod_id}:block/{blk.id}"},
                    },
                    fh,
                    indent=2,
                )

            # blockstate
            with open(
                os.path.join(blkstate_dir, f"{blk.id}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {"variants": {"": {"model": f"{mod_id}:block/{blk.id}"}}},
                    fh,
                    indent=2,
                )

            # inventory texture
            inv_src = (
                blk.inventory_texture_path
                if blk.inventory_texture_path
                and os.path.exists(blk.inventory_texture_path)
                else blk.block_texture_path
            )
            shutil.copy(inv_src, os.path.join(itm_tex_dir, f"{blk.id}.png"))

            # item model
            with open(
                os.path.join(itm_mdl_dir, f"{blk.id}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "parent": "minecraft:item/generated",
                        "textures": {"layer0": f"{mod_id}:item/{blk.id}"},
                    },
                    fh,
                    indent=2,
                )

            # item definition
            with open(
                os.path.join(itm_def_dir, f"{blk.id}.json"), "w", encoding="utf-8"
            ) as fh:
                json.dump(
                    {
                        "model": {
                            "type": "minecraft:model",
                            "model": f"{mod_id}:item/{blk.id}",
                        }
                    },
                    fh,
                    indent=2,
                )

    def update_block_lang_file(self, project_dir, mod_id):
        lang = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id, "lang"
        )
        os.makedirs(lang, exist_ok=True)
        path = os.path.join(lang, "en_us.json")
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = {}
        for blk in self.registered_blocks:
            data[f"block.{mod_id}.{blk.id}"] = blk.name
            data[f"item.{mod_id}.{blk.id}"] = blk.name
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
