#!/usr/bin/env python3
"""
This script initializes a Fabric mod project for Minecraft v1.21.5 with a custom block.
It performs the following steps:
1. Clones the Fabric example mod repository.
2. Updates the mod metadata in fabric.mod.json.
3. Creates two Java source files to add a basic custom block:
   - CustomBlock.java: A custom block class (extending Block).
   - TutorialBlocks.java: A registry helper class that registers the custom block and its BlockItem.
4. Patches the mod initializer (ExampleMod.java) to call TutorialBlocks.initialize().
5. Optionally, copies a texture (PNG) from a specified directory into the mod’s assets and generates default model JSON and blockstate JSON files for the block.
The custom block is registered with the mod ID "mycustommod" under the identifier "custom_block".
In-game you can use the command:
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
      - TutorialBlocks.java: A helper class that registers the block and its BlockItem.
    """
    java_src_dir = os.path.join(project_dir, "src", "main", "java")
    full_package_dir = os.path.join(java_src_dir, *package_path.split("."))
    os.makedirs(full_package_dir, exist_ok=True)
    print(f"Created/verified Java package directory for blocks: {full_package_dir}\n")

    # Create TutorialBlocks.java.
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
    // For example, we'll make a custom block that copies the properties of dirt.
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

    # Create CustomBlock.java.
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
    Updates the mod initializer so that it calls TutorialBlocks.initialize() within onInitialize().
    Assumes that the main mod class is located at:
         src/main/java/com/example/ExampleMod.java
    """
    mod_init_path = os.path.join(
        project_dir, "src", "main", "java", "com", "example", "ExampleMod.java"
    )
    if not os.path.exists(mod_init_path):
        print(
            f"Mod initializer file not found at {mod_init_path}, skipping update of mod initializer for blocks."
        )
        return
    print(f"Updating mod initializer at {mod_init_path} to register custom blocks...")
    with open(mod_init_path, "r", encoding="utf-8") as file:
        content = file.read()

    # If the call already exists, do nothing.
    if "TutorialBlocks.initialize()" in content:
        print(
            "Mod initializer already contains call to TutorialBlocks.initialize(). Skipping update.\n"
        )
        return

    # Insert the call after the onInitialize() method's opening brace.
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
            "Could not locate onInitialize() method properly in mod initializer; skipping block update.\n"
        )


def copy_block_texture_and_generate_models(project_dir, mod_id, texture_source):
    """
    Copies the texture file from texture_source into the mod's assets directory,
    and generates default block model JSON and blockstate JSON files so that the custom block uses the texture.
    The texture is copied to:
       src/main/resources/assets/<mod_id>/textures/block/custom_block.png
    The block model JSON is generated at:
       src/main/resources/assets/<mod_id>/models/block/custom_block.json
    The blockstate definition is generated at:
       src/main/resources/assets/<mod_id>/blockstates/custom_block.json
    :param project_dir: The root directory of the mod project.
    :param mod_id: The mod identifier (e.g. "mycustommod")
    :param texture_source: Full path to the texture PNG file for the block.
    """
    assets_dir = os.path.join(project_dir, "src", "main", "resources", "assets", mod_id)
    texture_dir = os.path.join(assets_dir, "textures", "block")
    model_dir = os.path.join(assets_dir, "models", "block")
    blockstate_dir = os.path.join(assets_dir, "blockstates")
    for d in (texture_dir, model_dir, blockstate_dir):
        os.makedirs(d, exist_ok=True)

    target_texture_path = os.path.join(texture_dir, "custom_block.png")
    shutil.copy(texture_source, target_texture_path)
    print(f"Copied block texture from {texture_source} to {target_texture_path}")

    # Create block model JSON.
    model_json = {
        "parent": "minecraft:block/cube_all",
        "textures": {"all": f"{mod_id}:block/custom_block"},
    }
    target_model_path = os.path.join(model_dir, "custom_block.json")
    with open(target_model_path, "w", encoding="utf-8") as file:
        json.dump(model_json, file, indent=2)
    print(f"Created block model JSON at {target_model_path}")

    # Create blockstate JSON.
    blockstate_json = {"variants": {"": {"model": f"{mod_id}:block/custom_block"}}}
    target_blockstate_path = os.path.join(blockstate_dir, "custom_block.json")
    with open(target_blockstate_path, "w", encoding="utf-8") as file:
        json.dump(blockstate_json, file, indent=2)
    print(f"Created blockstate JSON at {target_blockstate_path}\n")


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

    # Step 5: Optionally, copy a texture file and generate block model and blockstate JSON files.
    block_texture_path = input(
        "Enter the full path to the texture PNG file for the custom block (or press Enter to skip): "
    ).strip()
    if block_texture_path:
        if os.path.exists(block_texture_path):
            copy_block_texture_and_generate_models(
                target_dir, "mycustommod", block_texture_path
            )
        else:
            print(
                f"Texture file not found at {block_texture_path}. Skipping texture copying for block."
            )
    else:
        print(
            "No block texture file provided, skipping texture and model generation for block."
        )

    print("Fabric mod project has been initialized with basic block creation code.\n")
    print(
        "In Minecraft, run the following command to receive your custom block (as a BlockItem):"
    )
    print("/give @s mycustommod:custom_block")


if __name__ == "__main__":
    main()
