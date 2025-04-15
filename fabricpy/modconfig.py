import os
import json
import subprocess
import re
import shutil


class ModConfig:
    def __init__(
        self,
        mod_id,
        name,
        description,
        version,
        authors,
        project_dir="my-fabric-mod",
        template_repo="https://github.com/FabricMC/fabric-example-mod.git",
    ):
        """
        Initializes a mod configuration.
        :param mod_id: The mod namespace (used in game commands and asset paths).
        :param name: The display name of the mod.
        :param description: A short description of the mod.
        :param version: The mod version.
        :param authors: A list of author names.
        :param project_dir: The local directory where the mod project will be created.
        :param template_repo: The git URL for a Fabric example mod repository.
        """
        self.mod_id = mod_id
        self.name = name
        self.description = description
        self.version = version
        self.authors = authors
        self.project_dir = project_dir
        self.template_repo = template_repo
        self.registered_items = []
        self.registered_blocks = []

    def registerItem(self, item):
        """
        Registers a custom item into the mod.
        :param item: An instance of fabricpy.Item (or subclass) representing a custom item.
        """
        self.registered_items.append(item)

    def registerBlock(self, block):
        """
        Registers a custom block (and its BlockItem) into the mod.
        :param block: An instance of fabricpy.Block (or subclass) representing a custom block.
        """
        self.registered_blocks.append(block)

    def compile(self):
        """
        Creates/updates the Fabric mod project files:
          1. Clones the example repository if the target directory does not exist.
          2. Updates the fabric.mod.json file dynamically.
          3. Creates Java source files for item registration.
          4. Patches the mod initializer to load item registrations.
          5. Processes each registered item's texture: copies and generates model JSON files.
          6. Updates the language file for item names.
          7. [If any blocks are registered] Creates Java source files for block registration.
          8. Patches the mod initializer to load block registrations.
          9. Processes each registered block’s textures: copies textures and generates block model,
             blockstate, and item (inventory) JSON files (including an item model definition).
         10. Updates the language file with block names.
        """
        # 1. Clone the repository if necessary.
        if not os.path.exists(self.project_dir):
            self.clone_repository(self.template_repo, self.project_dir)
        else:
            print(
                f"Directory {self.project_dir} already exists; skipping repository clone."
            )

        # 2. Update mod metadata in fabric.mod.json.
        mod_json_path = os.path.join(
            self.project_dir, "src", "main", "resources", "fabric.mod.json"
        )
        new_metadata = {
            "id": self.mod_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "authors": self.authors,
        }
        self.update_mod_metadata(mod_json_path, new_metadata)

        # 3. Create/update Java source files for item registration.
        item_package = f"com.example.{self.mod_id}.items"
        self.create_item_files(self.project_dir, item_package)

        # 4. Update mod initializer for items.
        self.update_mod_initializer(self.project_dir, item_package)

        # 5. Process registered items: copy textures and generate JSON files.
        self.copy_texture_and_generate_models(self.project_dir, self.mod_id)

        # 6. Update language file for items.
        self.update_item_lang_file(self.project_dir, self.mod_id)

        # 7. If any blocks are registered, process blocks.
        if self.registered_blocks:
            block_package = f"com.example.{self.mod_id}.blocks"
            self.create_block_files(self.project_dir, block_package)
            self.update_mod_initializer_blocks(self.project_dir, block_package)
            self.copy_block_textures_and_generate_models(self.project_dir, self.mod_id)
            self.update_block_lang_file(self.project_dir, self.mod_id)

        print("Mod project compilation complete.")

    def clone_repository(self, repo_url, target_dir):
        print(f"Cloning repository from {repo_url} into {target_dir} ...")
        subprocess.check_call(["git", "clone", repo_url, target_dir])
        print("Repository cloned successfully.\n")

    def update_mod_metadata(self, mod_json_path, new_metadata):
        if not os.path.exists(mod_json_path):
            raise FileNotFoundError(f"fabric.mod.json not found at {mod_json_path}")
        print(f"Updating mod metadata in {mod_json_path} ...")
        with open(mod_json_path, "r", encoding="utf-8") as file:
            mod_data = json.load(file)
        mod_data.update(new_metadata)
        with open(mod_json_path, "w", encoding="utf-8") as file:
            json.dump(mod_data, file, indent=2)
        print("Mod metadata updated successfully.\n")

    # === Item Java Files Generation ===
    def create_item_files(self, project_dir, package_path):
        java_src_dir = os.path.join(project_dir, "src", "main", "java")
        full_package_dir = os.path.join(java_src_dir, *package_path.split("."))
        os.makedirs(full_package_dir, exist_ok=True)
        print(
            f"Created/verifying Java package directory for items: {full_package_dir}\n"
        )

        tutorial_items_content = self.generate_tutorial_items_content(package_path)
        tutorial_items_path = os.path.join(full_package_dir, "TutorialItems.java")
        with open(tutorial_items_path, "w", encoding="utf-8") as file:
            file.write(tutorial_items_content)
        print(f"Created item registration file: {tutorial_items_path}\n")

        custom_item_content = self.generate_custom_item_content(package_path)
        custom_item_path = os.path.join(full_package_dir, "CustomItem.java")
        with open(custom_item_path, "w", encoding="utf-8") as file:
            file.write(custom_item_content)
        print(f"Created default CustomItem Java file: {custom_item_path}\n")

    def generate_tutorial_items_content(self, package_path):
        # Begin with package and necessary imports.
        lines = []
        lines.append(f"package {package_path};")
        lines.append("")
        lines.append("import net.minecraft.item.Item;")
        lines.append("import net.minecraft.util.Identifier;")
        lines.append("import net.minecraft.registry.Registry;")
        lines.append("import net.minecraft.registry.RegistryKey;")
        lines.append("import net.minecraft.registry.RegistryKeys;")
        lines.append("import net.minecraft.registry.Registries;")
        lines.append("import net.minecraft.item.Item.Settings;")
        # If any item has an item group, add the following imports.
        if any(
            hasattr(item, "item_group") and item.item_group
            for item in self.registered_items
        ):
            lines.append("import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;")
            lines.append("import net.minecraft.item.ItemGroups;")
        lines.append("import java.util.function.Function;")
        lines.append("")
        lines.append("public final class TutorialItems {")
        lines.append("    private TutorialItems() {}")
        lines.append("")
        # Registration lines
        for item in self.registered_items:
            constant_name = item.id.upper()
            lines.append(
                f'    public static final Item {constant_name} = register("{item.id}", CustomItem::new, new Item.Settings().maxCount({item.max_stack_size}));'
            )
        lines.append("")
        lines.append(
            f"    public static Item register(String path, Function<Item.Settings, Item> factory, Item.Settings settings) {{"
        )
        lines.append(
            f'        final RegistryKey<Item> registryKey = RegistryKey.of(RegistryKeys.ITEM, Identifier.of("{self.mod_id}", path));'
        )
        lines.append("        settings = settings.registryKey(registryKey);")
        lines.append(
            f'        return Registry.register(Registries.ITEM, Identifier.of("{self.mod_id}", path), factory.apply(settings));'
        )
        lines.append("    }")
        lines.append("")
        # Build a dictionary of group -> list of item constant names.
        group_dict = {}
        for item in self.registered_items:
            if hasattr(item, "item_group") and item.item_group:
                group = item.item_group  # e.g. "BUILDING_BLOCKS"
                group_dict.setdefault(group, []).append(item.id.upper())
        # Generate the initialize method with item group events.
        lines.append("    public static void initialize() {")
        if group_dict:
            for group, consts in group_dict.items():
                lines.append(
                    f"        ItemGroupEvents.modifyEntriesEvent(ItemGroups.{group}).register(entries -> {{"
                )
                for const in consts:
                    lines.append(f"            entries.add({const});")
                lines.append("        });")
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines)

    def generate_custom_item_content(self, package_path):
        content = f"""\
package {package_path};

import net.minecraft.item.Item;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.sound.SoundEvents;
import net.minecraft.sound.SoundCategory;
import net.minecraft.world.World;

public class CustomItem extends Item {{
    public CustomItem(Settings settings) {{
        super(settings);
    }}

    @Override
    public ActionResult use(World world, PlayerEntity user, Hand hand) {{
        if (!world.isClient()) {{
            world.playSound(null, user.getBlockPos(), SoundEvents.BLOCK_WOOL_BREAK, SoundCategory.PLAYERS, 1.0F, 1.0F);
        }}
        return ActionResult.SUCCESS;
    }}
}}
"""
        return content

    def update_mod_initializer(self, project_dir, package_path):
        mod_init_path = os.path.join(
            project_dir, "src", "main", "java", "com", "example", "ExampleMod.java"
        )
        if not os.path.exists(mod_init_path):
            print(
                f"Mod initializer file not found at {mod_init_path}, skipping update for items."
            )
            return
        print(f"Updating mod initializer for items at {mod_init_path}...")
        with open(mod_init_path, "r", encoding="utf-8") as file:
            content = file.read()
        if f"{package_path}.TutorialItems.initialize()" in content:
            print("Item initializer already present; skipping update.\n")
            return
        pattern = r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)"

        def replacer(match):
            return match.group(0) + f"\n    {package_path}.TutorialItems.initialize();"

        new_content, count = re.subn(pattern, replacer, content, count=1)
        if count > 0:
            with open(mod_init_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print("Item initializer updated successfully.\n")
        else:
            print(
                "Could not locate onInitialize() method; skipping item initializer update.\n"
            )

    def copy_texture_and_generate_models(self, project_dir, mod_id):
        assets_dir = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id
        )
        texture_dir = os.path.join(assets_dir, "textures", "item")
        model_dir = os.path.join(assets_dir, "models", "item")
        itemdef_dir = os.path.join(assets_dir, "items")
        for d in (texture_dir, model_dir, itemdef_dir):
            os.makedirs(d, exist_ok=True)
        for item in self.registered_items:
            if item.texture_path and os.path.exists(item.texture_path):
                target_texture_filename = f"{item.id}.png"
                target_texture_path = os.path.join(texture_dir, target_texture_filename)
                shutil.copy(item.texture_path, target_texture_path)
                print(
                    f"Copied item texture from {item.texture_path} to {target_texture_path}"
                )
                model_json_content = {
                    "parent": "minecraft:item/generated",
                    "textures": {"layer0": f"{mod_id}:item/{item.id}"},
                }
                target_model_path = os.path.join(model_dir, f"{item.id}.json")
                with open(target_model_path, "w", encoding="utf-8") as file:
                    json.dump(model_json_content, file, indent=2)
                print(f"Created item model JSON at {target_model_path}")
                item_model_def_content = {
                    "model": {
                        "type": "minecraft:model",
                        "model": f"{mod_id}:item/{item.id}",
                    }
                }
                target_itemdef_path = os.path.join(itemdef_dir, f"{item.id}.json")
                with open(target_itemdef_path, "w", encoding="utf-8") as file:
                    json.dump(item_model_def_content, file, indent=2)
                print(f"Created item model definition JSON at {target_itemdef_path}\n")
            else:
                print(f"No valid texture for item '{item.id}'; skipping texture copy.")

    def update_item_lang_file(self, project_dir, mod_id):
        lang_dir = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id, "lang"
        )
        os.makedirs(lang_dir, exist_ok=True)
        lang_file = os.path.join(lang_dir, "en_us.json")
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as file:
                try:
                    lang_data = json.load(file)
                except json.JSONDecodeError:
                    lang_data = {}
        else:
            lang_data = {}
        for item in self.registered_items:
            lang_data[f"item.{mod_id}.{item.id}"] = item.name
        with open(lang_file, "w", encoding="utf-8") as file:
            json.dump(lang_data, file, indent=2)
        print(f"Updated language file for items at {lang_file}.\n")

    # === Block Java Files and Assets Generation ===
    def create_block_files(self, project_dir, package_path):
        java_src_dir = os.path.join(project_dir, "src", "main", "java")
        full_package_dir = os.path.join(java_src_dir, *package_path.split("."))
        os.makedirs(full_package_dir, exist_ok=True)
        print(
            f"Created/verifying Java package directory for blocks: {full_package_dir}\n"
        )
        tutorial_blocks_content = self.generate_tutorial_blocks_content(package_path)
        tutorial_blocks_path = os.path.join(full_package_dir, "TutorialBlocks.java")
        with open(tutorial_blocks_path, "w", encoding="utf-8") as file:
            file.write(tutorial_blocks_content)
        print(f"Created block registration file: {tutorial_blocks_path}\n")
        custom_block_content = self.generate_custom_block_content(package_path)
        custom_block_path = os.path.join(full_package_dir, "CustomBlock.java")
        with open(custom_block_path, "w", encoding="utf-8") as file:
            file.write(custom_block_content)
        print(f"Created default CustomBlock Java file: {custom_block_path}\n")

    def generate_tutorial_blocks_content(self, package_path):
        lines = []
        lines.append(f"package {package_path};")
        lines.append("")
        lines.append("import net.minecraft.block.Block;")
        lines.append("import net.minecraft.block.AbstractBlock;")
        lines.append("import net.minecraft.block.Blocks;")
        lines.append("import net.minecraft.item.BlockItem;")
        lines.append("import net.minecraft.item.Item;")
        lines.append("import net.minecraft.util.Identifier;")
        lines.append("import net.minecraft.registry.Registry;")
        lines.append("import net.minecraft.registry.RegistryKey;")
        lines.append("import net.minecraft.registry.RegistryKeys;")
        lines.append("import net.minecraft.registry.Registries;")
        # If any block has an item group, add these imports.
        if any(
            hasattr(block, "item_group") and block.item_group
            for block in self.registered_blocks
        ):
            lines.append("import net.fabricmc.fabric.api.itemgroup.v1.ItemGroupEvents;")
            lines.append("import net.minecraft.item.ItemGroups;")
        lines.append("import java.util.function.Function;")
        lines.append("")
        lines.append("public final class TutorialBlocks {")
        lines.append("    private TutorialBlocks() {}")
        lines.append("")
        for block in self.registered_blocks:
            constant_name = block.id.upper()
            lines.append(
                f'    public static final Block {constant_name} = register("{block.id}", CustomBlock::new, AbstractBlock.Settings.copy(Blocks.STONE).requiresTool(), true);'
            )
        lines.append("")
        lines.append(
            f"    public static Block register(String path, Function<AbstractBlock.Settings, Block> factory, AbstractBlock.Settings settings, boolean registerItem) {{"
        )
        lines.append(
            f'        final RegistryKey<Block> blockKey = RegistryKey.of(RegistryKeys.BLOCK, Identifier.of("{self.mod_id}", path));'
        )
        lines.append("        settings = settings.registryKey(blockKey);")
        lines.append(
            f'        Block block = Registry.register(Registries.BLOCK, Identifier.of("{self.mod_id}", path), factory.apply(settings));'
        )
        lines.append("        if (registerItem) {")
        lines.append(
            f'            final RegistryKey<Item> itemKey = RegistryKey.of(RegistryKeys.ITEM, Identifier.of("{self.mod_id}", path));'
        )
        lines.append(
            "            Item.Settings itemSettings = new Item.Settings().maxCount(64).registryKey(itemKey);"
        )
        lines.append(
            f'            Registry.register(Registries.ITEM, Identifier.of("{self.mod_id}", path), new BlockItem(block, itemSettings));'
        )
        lines.append("        }")
        lines.append("        return block;")
        lines.append("    }")
        lines.append("")
        # Group block items that specify an item group.
        group_dict = {}
        for block in self.registered_blocks:
            if hasattr(block, "item_group") and block.item_group:
                group = block.item_group
                group_dict.setdefault(group, []).append(block.id.upper())
        lines.append("    public static void initialize() {")
        if group_dict:
            for group, consts in group_dict.items():
                lines.append(
                    f"        ItemGroupEvents.modifyEntriesEvent(ItemGroups.{group}).register(entries -> {{"
                )
                for const in consts:
                    lines.append(f"            entries.add({const}.asItem());")
                lines.append("        });")
        lines.append("    }")
        lines.append("}")
        return "\n".join(lines)

    def generate_custom_block_content(self, package_path):
        content = f"""\
package {package_path};

import net.minecraft.block.Block;
import net.minecraft.block.AbstractBlock;

public class CustomBlock extends Block {{
    public CustomBlock(AbstractBlock.Settings settings) {{
        super(settings);
    }}
}}
"""
        return content

    def update_mod_initializer_blocks(self, project_dir, package_path):
        mod_init_path = os.path.join(
            project_dir,
            "src",
            "main",
            "resources",
            "java",
            "com",
            "example",
            "ExampleMod.java",
        )
        # Fallback: try com/example/ExampleMod.java in src/main/java
        if not os.path.exists(mod_init_path):
            mod_init_path = os.path.join(
                project_dir, "src", "main", "java", "com", "example", "ExampleMod.java"
            )
        if not os.path.exists(mod_init_path):
            print(
                f"Mod initializer file not found at {mod_init_path}, skipping block initializer update."
            )
            return
        print(f"Updating mod initializer for blocks at {mod_init_path}...")
        with open(mod_init_path, "r", encoding="utf-8") as file:
            content = file.read()
        if f"{package_path}.TutorialBlocks.initialize()" in content:
            print("Block initializer already present; skipping update.\n")
            return
        pattern = r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)"

        def replacer(match):
            return match.group(0) + f"\n    {package_path}.TutorialBlocks.initialize();"

        new_content, count = re.subn(pattern, replacer, content, count=1)
        if count > 0:
            with open(mod_init_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print("Block initializer updated successfully.\n")
        else:
            print(
                "Could not locate onInitialize() method; skipping block initializer update.\n"
            )

    def copy_block_textures_and_generate_models(self, project_dir, mod_id):
        assets_dir = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id
        )
        block_tex_dir = os.path.join(assets_dir, "textures", "block")
        block_model_dir = os.path.join(assets_dir, "models", "block")
        blockstate_dir = os.path.join(assets_dir, "blockstates")
        item_tex_dir = os.path.join(assets_dir, "textures", "item")
        item_model_dir = os.path.join(assets_dir, "models", "item")
        for d in (
            block_tex_dir,
            block_model_dir,
            blockstate_dir,
            item_tex_dir,
            item_model_dir,
        ):
            os.makedirs(d, exist_ok=True)
        for block in self.registered_blocks:
            if block.block_texture_path and os.path.exists(block.block_texture_path):
                target_block_texture = os.path.join(block_tex_dir, f"{block.id}.png")
                shutil.copy(block.block_texture_path, target_block_texture)
                print(
                    f"Copied block texture from {block.block_texture_path} to {target_block_texture}"
                )
                block_model_json = {
                    "parent": "minecraft:block/cube_all",
                    "textures": {"all": f"{mod_id}:block/{block.id}"},
                }
                target_block_model = os.path.join(block_model_dir, f"{block.id}.json")
                with open(target_block_model, "w", encoding="utf-8") as file:
                    json.dump(block_model_json, file, indent=2)
                print(f"Created block model JSON at {target_block_model}")
                blockstate_json = {
                    "variants": {"": {"model": f"{mod_id}:block/{block.id}"}}
                }
                target_blockstate = os.path.join(blockstate_dir, f"{block.id}.json")
                with open(target_blockstate, "w", encoding="utf-8") as file:
                    json.dump(blockstate_json, file, indent=2)
                print(f"Created blockstate JSON at {target_blockstate}")
                if block.inventory_texture_path and os.path.exists(
                    block.inventory_texture_path
                ):
                    target_item_texture = os.path.join(item_tex_dir, f"{block.id}.png")
                    shutil.copy(block.inventory_texture_path, target_item_texture)
                    print(
                        f"Copied inventory texture from {block.inventory_texture_path} to {target_item_texture}"
                    )
                else:
                    print(
                        "No valid inventory texture provided; using block texture as default."
                    )
                    target_item_texture = os.path.join(item_tex_dir, f"{block.id}.png")
                    shutil.copy(block.block_texture_path, target_item_texture)
                item_model_json = {
                    "parent": "minecraft:item/generated",
                    "textures": {"layer0": f"{mod_id}:item/{block.id}"},
                }
                target_item_model = os.path.join(item_model_dir, f"{block.id}.json")
                with open(target_item_model, "w", encoding="utf-8") as file:
                    json.dump(item_model_json, file, indent=2)
                print(f"Created block item model JSON at {target_item_model}\n")
                item_def_dir = os.path.join(assets_dir, "items")
                os.makedirs(item_def_dir, exist_ok=True)
                item_def_json = {
                    "model": {"type": "model", "model": f"{mod_id}:item/{block.id}"}
                }
                target_item_def = os.path.join(item_def_dir, f"{block.id}.json")
                with open(target_item_def, "w", encoding="utf-8") as file:
                    json.dump(item_def_json, file, indent=2)
                print(
                    f"Created block item model definition JSON at {target_item_def}\n"
                )
            else:
                print(
                    f"No valid block texture for block '{block.id}'; skipping texture copy."
                )

    def update_block_lang_file(self, project_dir, mod_id):
        lang_dir = os.path.join(
            project_dir, "src", "main", "resources", "assets", mod_id, "lang"
        )
        os.makedirs(lang_dir, exist_ok=True)
        lang_file = os.path.join(lang_dir, "en_us.json")
        if os.path.exists(lang_file):
            with open(lang_file, "r", encoding="utf-8") as file:
                try:
                    lang_data = json.load(file)
                except json.JSONDecodeError:
                    lang_data = {}
        else:
            lang_data = {}
        for block in self.registered_blocks:
            lang_data[f"block.{mod_id}.{block.id}"] = block.name
            lang_data[f"item.{mod_id}.{block.id}"] = block.name
        with open(lang_file, "w", encoding="utf-8") as file:
            json.dump(lang_data, file, indent=2)
        print(f"Updated language file for blocks at {lang_file}.\n")
