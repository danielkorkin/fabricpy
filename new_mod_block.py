#!/usr/bin/env python3
"""
This script initializes a Fabric mod project for Minecraft v1.21.5 with a custom block.
It performs the following steps:
1. Clones the Fabric example mod repository.
2. Updates the mod metadata in fabric.mod.json.
3. Creates two Java source files to add a basic custom block:
   - CustomBlock.java: A simple custom block class.
   - TutorialBlocks.java: A helper class that registers the custom block and its BlockItem.
4. Patches the mod initializer (ExampleMod.java) to call TutorialBlocks.initialize().
5. Optionally, copies a texture file for the block and generates default model JSON and blockstate JSON files.
   Then prompts for an optional separate inventory icon texture for the block.
6. Updates/creates a language file so that the block and its item have friendly names.
The custom block is registered with the mod ID "mycustommod" under the identifier "custom_block".
In-game, use:
    /give @s mycustommod:custom_block
to obtain its BlockItem.
"""

import os
import json
import subprocess
import re
import shutil


def clone_repository(repo_url, target_dir):
    print(f"Cloning repository from {repo_url} into {target_dir} ...")
    subprocess.check_call(["git", "clone", repo_url, target_dir])
    print("Repository cloned successfully.\n")


def update_mod_metadata(mod_json_path, new_metadata):
    if not os.path.exists(mod_json_path):
        raise FileNotFoundError(f"Could not find mod descriptor: {mod_json_path}")
    print(f"Updating mod metadata in {mod_json_path} ...")
    with open(mod_json_path, "r", encoding="utf-8") as file:
        mod_data = json.load(file)
    mod_data.update(new_metadata)
    with open(mod_json_path, "w", encoding="utf-8") as file:
        json.dump(mod_data, file, indent=2)
    print("Mod metadata updated successfully.\n")


def create_block_files(project_dir, package_path):
    """
    Creates Java source files for a custom block.
    Two files are created in the given package (e.g. 'com.example.mycustommod.blocks'):
      - CustomBlock.java: A simple custom block class.
      - TutorialBlocks.java: A helper class that registers the custom block and its BlockItem.
    """
    java_src_dir = os.path.join(project_dir, "src", "main", "java")
    full_package_dir = os.path.join(java_src_dir, *package_path.split("."))
    os.makedirs(full_package_dir, exist_ok=True)
    print(f"Created/verified Java package directory for blocks: {full_package_dir}\n")

    tutorial_blocks_content = f"""\
package {package_path};

import net.minecraft.block.Block;
import net.minecraft.block.AbstractBlock;
import net.minecraft.block.Blocks;
import net.minecraft.item.BlockItem;
import net.minecraft.item.Item;
import net.minecraft.util.Identifier;
import net.minecraft.registry.Registry;
import net.minecraft.registry.RegistryKey;
import net.minecraft.registry.RegistryKeys;
import net.minecraft.registry.Registries;
import java.util.function.Function;

public final class TutorialBlocks {{
    private TutorialBlocks() {{}}

    // Registers a custom block with a BlockItem.
    public static final Block CUSTOM_BLOCK = register("custom_block", CustomBlock::new,
            AbstractBlock.Settings.copy(Blocks.DIRT).requiresTool(), true);

    public static Block register(String path, Function<AbstractBlock.Settings, Block> factory,
                                 AbstractBlock.Settings settings, boolean registerItem) {{
        final RegistryKey<Block> blockKey = RegistryKey.of(RegistryKeys.BLOCK, Identifier.of("mycustommod", path));
        settings = settings.registryKey(blockKey);
        Block block = Registry.register(Registries.BLOCK, Identifier.of("mycustommod", path), factory.apply(settings));
        if (registerItem) {{
            final RegistryKey<Item> itemKey = RegistryKey.of(RegistryKeys.ITEM, Identifier.of("mycustommod", path));
            Item.Settings itemSettings = new Item.Settings().maxCount(64).registryKey(itemKey);
            Registry.register(Registries.ITEM, Identifier.of("mycustommod", path), new BlockItem(block, itemSettings));
        }}
        return block;
    }}

    public static void initialize() {{}}
}}
"""
    tutorial_blocks_path = os.path.join(full_package_dir, "TutorialBlocks.java")
    with open(tutorial_blocks_path, "w", encoding="utf-8") as file:
        file.write(tutorial_blocks_content)
    print(f"Created file: {tutorial_blocks_path}\n")

    custom_block_content = f"""\
package {package_path};

import net.minecraft.block.Block;
import net.minecraft.block.AbstractBlock;

public class CustomBlock extends Block {{
    public CustomBlock(AbstractBlock.Settings settings) {{
        super(settings);
    }}
}}
"""
    custom_block_path = os.path.join(full_package_dir, "CustomBlock.java")
    with open(custom_block_path, "w", encoding="utf-8") as file:
        file.write(custom_block_content)
    print(f"Created file: {custom_block_path}\n")


def update_mod_initializer_with_blocks(project_dir):
    """
    Updates the mod initializer file so that it calls TutorialBlocks.initialize() within onInitialize().
    Assumes that the main mod class is located at:
         src/main/java/com/example/ExampleMod.java
    """
    mod_init_path = os.path.join(
        project_dir, "src", "main", "java", "com", "example", "ExampleMod.java"
    )
    if not os.path.exists(mod_init_path):
        print(
            f"Mod initializer file not found at {mod_init_path}, skipping update for blocks."
        )
        return
    print(f"Updating mod initializer at {mod_init_path} to register custom blocks...")
    with open(mod_init_path, "r", encoding="utf-8") as file:
        content = file.read()
    if "TutorialBlocks.initialize()" in content:
        print("Mod initializer already updated for blocks. Skipping.\n")
        return
    pattern = r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)"

    def replacer(match):
        return (
            match.group(0)
            + "\n    com.example.mycustommod.blocks.TutorialBlocks.initialize();"
        )

    new_content, count = re.subn(pattern, replacer, content, count=1)
    if count > 0:
        with open(mod_init_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print("Mod initializer updated successfully for blocks.\n")
    else:
        print(
            "Could not locate onInitialize() method properly; skipping block update.\n"
        )


def copy_block_textures_and_generate_models(project_dir, mod_id, block_texture_source):
    """
    Copies the block texture file from block_texture_source into the assets directory,
    and generates default block model and blockstate JSON files.
    Also generates an item model JSON for the block's BlockItem.
    - The block texture is copied to:
         assets/<mod_id>/textures/block/custom_block.png
    - The block model JSON is generated at:
         assets/<mod_id>/models/block/custom_block.json
    - The blockstate JSON is generated at:
         assets/<mod_id>/blockstates/custom_block.json
    - The block item's model JSON is generated at:
         assets/<mod_id>/models/item/custom_block.json
      When generating the item model JSON, the script prompts for an optional separate inventory icon texture.
      If provided, that texture is used; otherwise, the block texture is copied into the item textures as default.
    Additionally, an item model definition JSON is generated in:
         assets/<mod_id>/items/custom_block.json
    :param project_dir: The root directory of the mod project.
    :param mod_id: The mod id (e.g. "mycustommod").
    :param block_texture_source: Full path to the block texture PNG file.
    """
    assets_dir = os.path.join(project_dir, "src", "main", "resources", "assets", mod_id)
    # Directories for block assets.
    block_texture_dir = os.path.join(assets_dir, "textures", "block")
    block_model_dir = os.path.join(assets_dir, "models", "block")
    blockstate_dir = os.path.join(assets_dir, "blockstates")
    # Directories for item assets.
    item_texture_dir = os.path.join(assets_dir, "textures", "item")
    item_model_dir = os.path.join(assets_dir, "models", "item")
    for d in (
        block_texture_dir,
        block_model_dir,
        blockstate_dir,
        item_texture_dir,
        item_model_dir,
    ):
        os.makedirs(d, exist_ok=True)

    # Copy the block texture.
    target_block_texture = os.path.join(block_texture_dir, "custom_block.png")
    shutil.copy(block_texture_source, target_block_texture)
    print(f"Copied block texture from {block_texture_source} to {target_block_texture}")

    # Generate block model JSON.
    block_model_json = {
        "parent": "minecraft:block/cube_all",
        "textures": {"all": f"{mod_id}:block/custom_block"},
    }
    target_block_model = os.path.join(block_model_dir, "custom_block.json")
    with open(target_block_model, "w", encoding="utf-8") as file:
        json.dump(block_model_json, file, indent=2)
    print(f"Created block model JSON at {target_block_model}")

    # Generate blockstate JSON.
    blockstate_json = {"variants": {"": {"model": f"{mod_id}:block/custom_block"}}}
    target_blockstate = os.path.join(blockstate_dir, "custom_block.json")
    with open(target_blockstate, "w", encoding="utf-8") as file:
        json.dump(blockstate_json, file, indent=2)
    print(f"Created blockstate JSON at {target_blockstate}")

    # Generate the block item's model JSON.
    # Prompt for a separate inventory icon texture.
    inv_texture = input(
        "Enter the full path to a separate block inventory texture PNG file (or press Enter to use block texture): "
    ).strip()
    if inv_texture and os.path.exists(inv_texture):
        target_item_texture = os.path.join(item_texture_dir, "custom_block_icon.png")
        shutil.copy(inv_texture, target_item_texture)
        print(
            f"Copied separate inventory icon texture from {inv_texture} to {target_item_texture}"
        )
        item_model_json = {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"{mod_id}:item/custom_block_icon"},
        }
    else:
        print(
            "No separate inventory icon provided; using block texture as default for inventory icon."
        )
        target_item_texture = os.path.join(item_texture_dir, "custom_block_icon.png")
        shutil.copy(block_texture_source, target_item_texture)
        item_model_json = {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"{mod_id}:item/custom_block_icon"},
        }
    target_item_model = os.path.join(item_model_dir, "custom_block.json")
    with open(target_item_model, "w", encoding="utf-8") as file:
        json.dump(item_model_json, file, indent=2)
    print(f"Created block item model JSON at {target_item_model}\n")

    # IMPORTANT: For Minecraft 1.21.4+ an item model definition file is required.
    item_def_dir = os.path.join(assets_dir, "items")
    os.makedirs(item_def_dir, exist_ok=True)
    item_def_json = {"model": {"type": "model", "model": f"{mod_id}:item/custom_block"}}
    target_item_def = os.path.join(item_def_dir, "custom_block.json")
    with open(target_item_def, "w", encoding="utf-8") as file:
        json.dump(item_def_json, file, indent=2)
    print(f"Created block item model definition JSON at {target_item_def}\n")


def update_lang_file(project_dir, mod_id):
    """
    Creates or updates the language file so that the custom block has a friendly name.
    The file is placed at:
         src/main/resources/assets/<mod_id>/lang/en_us.json
    and sets keys for both the block and the block item.
    """
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

    lang_data[f"block.{mod_id}.custom_block"] = "Custom Block"
    lang_data[f"item.{mod_id}.custom_block"] = "Custom Block"

    with open(lang_file, "w", encoding="utf-8") as file:
        json.dump(lang_data, file, indent=2)
    print(f"Updated language file at {lang_file} with block/item translations.\n")


def main():
    # Step 1: Clone the Fabric example mod repository.
    repo_url = "https://github.com/FabricMC/fabric-example-mod.git"
    target_dir = "my-fabric-mod"
    clone_repository(repo_url, target_dir)

    # Step 2: Update mod metadata in fabric.mod.json.
    mod_json_path = os.path.join(
        target_dir, "src", "main", "resources", "fabric.mod.json"
    )
    new_metadata = {
        "id": "mycustommod",
        "name": "My Custom Mod",
        "version": "1.0.0",
        "description": "A Fabric mod for Minecraft v1.21.5 that creates a custom block via Python-generated code.",
        "authors": ["Your Name"],
    }
    update_mod_metadata(mod_json_path, new_metadata)

    # Step 3: Create Java source files for the custom block.
    block_package = "com.example.mycustommod.blocks"
    create_block_files(target_dir, block_package)

    # Step 4: Update the mod initializer to load custom blocks.
    update_mod_initializer_with_blocks(target_dir)

    # Step 5: Optionally, copy a block texture and generate asset JSON files.
    block_texture_path = input(
        "Enter the full path to the texture PNG file for the custom block (or press Enter to skip): "
    ).strip()
    if block_texture_path and os.path.exists(block_texture_path):
        copy_block_textures_and_generate_models(
            target_dir, "mycustommod", block_texture_path
        )
    else:
        print(
            "No block texture provided, skipping texture and model generation for block."
        )

    # Step 6: Update the language file for proper naming.
    update_lang_file(target_dir, "mycustommod")

    print("Fabric mod project has been initialized with basic block creation code.\n")
    print(
        "In Minecraft, run the following command to receive your custom block (as a BlockItem):"
    )
    print("/give @s mycustommod:custom_block")


if __name__ == "__main__":
    main()
