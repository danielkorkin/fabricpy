#!/usr/bin/env python3
"""
This script initializes a Fabric mod project for Minecraft v1.21.5 by doing the following:
1. Clones the Fabric example mod repository.
2. Updates the mod metadata in the fabric.mod.json file.
3. Creates two Java source files to add a basic custom item:
   - CustomItem.java: A custom item class that plays a sound when used.
   - TutorialItems.java: A registry helper class that registers the custom item using the new 1.21.2+ method.
4. Patches the mod initializer (ExampleMod.java) to force the registration of the custom item.
5. Optionally copies a texture file (PNG) from a specified location into the mod’s assets and creates default model JSON files.
Note: This updated code uses Identifier.of(...) instead of new Identifier(...),
and uses Registries.ITEM instead of Registry.ITEM.
The custom item is registered with the mod ID "mycustommod", so the in-game /give command is:
    /give @s mycustommod:custom_item
"""

import os
import json
import subprocess
import re
import shutil


def clone_repository(repo_url, target_dir):
    """
    Clones a Git repository.
    :param repo_url: URL of the Git repository.
    :param target_dir: Directory where the repository will be cloned.
    """
    print(f"Cloning repository from {repo_url} into {target_dir} ...")
    subprocess.check_call(["git", "clone", repo_url, target_dir])
    print("Repository cloned successfully.\n")


def update_mod_metadata(mod_json_path, new_metadata):
    """
    Updates metadata fields in the fabric.mod.json file.
    :param mod_json_path: Path to the fabric.mod.json file.
    :param new_metadata: Dictionary with new metadata values.
    """
    if not os.path.exists(mod_json_path):
        raise FileNotFoundError(f"Could not find mod descriptor: {mod_json_path}")
    print(f"Updating mod metadata in {mod_json_path} ...")
    with open(mod_json_path, "r", encoding="utf-8") as file:
        mod_data = json.load(file)
    mod_data.update(new_metadata)
    with open(mod_json_path, "w", encoding="utf-8") as file:
        json.dump(mod_data, file, indent=2)
    print("Mod metadata updated successfully.\n")


def create_item_files(project_dir, package_path):
    """
    Creates Java source files for basic item registration.
    This function creates a directory corresponding to the package (e.g.
    'com.example.mycustommod.items') under src/main/java and writes out:
       - CustomItem.java: A custom item class.
       - TutorialItems.java: A registry helper class that registers the custom item.
    :param project_dir: The root directory of the mod project.
    :param package_path: The Java package (dot-separated) where to place the files.
    """
    # Construct the path to the Java source directory.
    java_src_dir = os.path.join(project_dir, "src", "main", "java")
    # Convert package path into folder structure.
    full_package_dir = os.path.join(java_src_dir, *package_path.split("."))
    os.makedirs(full_package_dir, exist_ok=True)
    print(f"Created/verified Java package directory: {full_package_dir}\n")

    # Create TutorialItems.java using "mycustommod" as the mod id.
    # Attach the registry key to the settings.
    tutorial_items_content = f"""\
package {package_path};

import net.minecraft.item.Item;
import net.minecraft.util.Identifier;
import net.minecraft.registry.Registry;
import net.minecraft.registry.RegistryKey;
import net.minecraft.registry.RegistryKeys;
import net.minecraft.registry.Registries;
import net.minecraft.item.Item.Settings;
import java.util.function.Function;

public final class TutorialItems {{
    private TutorialItems() {{}}

    // Registers a custom item with a maximum stack count of 16.
    public static final Item CUSTOM_ITEM = register("custom_item", CustomItem::new, new Item.Settings().maxCount(16));

    public static Item register(String path, Function<Item.Settings, Item> factory, Item.Settings settings) {{
        final RegistryKey<Item> registryKey = RegistryKey.of(RegistryKeys.ITEM, Identifier.of("mycustommod", path));
        settings = settings.registryKey(registryKey);
        return Registry.register(Registries.ITEM, Identifier.of("mycustommod", path), factory.apply(settings));
    }}

    public static void initialize() {{}}
}}
"""
    tutorial_items_path = os.path.join(full_package_dir, "TutorialItems.java")
    with open(tutorial_items_path, "w", encoding="utf-8") as file:
        file.write(tutorial_items_content)
    print(f"Created file: {tutorial_items_path}\n")

    # Create CustomItem.java.
    custom_item_content = f"""\
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
    custom_item_path = os.path.join(full_package_dir, "CustomItem.java")
    with open(custom_item_path, "w", encoding="utf-8") as file:
        file.write(custom_item_content)
    print(f"Created file: {custom_item_path}\n")


def update_mod_initializer(project_dir):
    """
    Updates the mod initializer file so that it calls TutorialItems.initialize() within onInitialize().
    Assumes that the main mod class is located at:
         src/main/java/com/example/ExampleMod.java
    """
    mod_init_path = os.path.join(
        project_dir, "src", "main", "java", "com", "example", "ExampleMod.java"
    )
    if not os.path.exists(mod_init_path):
        print(
            f"Mod initializer file not found at {mod_init_path}, skipping update of mod initializer."
        )
        return
    print(f"Updating mod initializer at {mod_init_path} to register custom items...")
    with open(mod_init_path, "r", encoding="utf-8") as file:
        content = file.read()

    if "TutorialItems.initialize()" in content:
        print(
            "Mod initializer already contains call to TutorialItems.initialize(). Skipping update.\n"
        )
        return

    pattern = r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)"

    def replacer(match):
        return (
            match.group(0)
            + "\n    com.example.mycustommod.items.TutorialItems.initialize();"
        )

    new_content, count = re.subn(pattern, replacer, content, count=1)
    if count > 0:
        with open(mod_init_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print("Mod initializer updated successfully.\n")
    else:
        print("Could not locate onInitialize() method properly; skipping update.\n")


def copy_texture_and_generate_models(project_dir, mod_id, texture_source):
    """
    Copies the texture file from texture_source into the mod's assets directory,
    and generates default model JSON files so that the custom item uses the texture.
    The texture is copied to:
       src/main/resources/assets/<mod_id>/textures/item/custom_item.png
    The item model JSON is created at:
       src/main/resources/assets/<mod_id>/models/item/custom_item.json
    The item model definition (for 1.21.4+) is created at:
       src/main/resources/assets/<mod_id>/items/custom_item.json
    :param project_dir: The root directory of the mod project.
    :param mod_id: The mod identifier (e.g. "mycustommod")
    :param texture_source: Path to the texture file on the local filesystem.
    """
    # Define target directories.
    assets_dir = os.path.join(project_dir, "src", "main", "resources", "assets", mod_id)
    texture_dir = os.path.join(assets_dir, "textures", "item")
    model_dir = os.path.join(assets_dir, "models", "item")
    itemdef_dir = os.path.join(assets_dir, "items")

    for d in (texture_dir, model_dir, itemdef_dir):
        os.makedirs(d, exist_ok=True)

    # Copy texture file.
    target_texture_path = os.path.join(texture_dir, "custom_item.png")
    shutil.copy(texture_source, target_texture_path)
    print(f"Copied texture file from {texture_source} to {target_texture_path}")

    # Generate the item model JSON.
    model_json_content = {
        "parent": "minecraft:item/generated",
        "textures": {"layer0": f"{mod_id}:item/custom_item"},
    }
    target_model_path = os.path.join(model_dir, "custom_item.json")
    with open(target_model_path, "w", encoding="utf-8") as file:
        json.dump(model_json_content, file, indent=2)
    print(f"Created model JSON at {target_model_path}")

    # Generate the item model definition JSON (for 1.21.4+).
    item_model_def_content = {
        "model": {"type": "minecraft:model", "model": f"{mod_id}:item/custom_item"}
    }
    target_itemdef_path = os.path.join(itemdef_dir, "custom_item.json")
    with open(target_itemdef_path, "w", encoding="utf-8") as file:
        json.dump(item_model_def_content, file, indent=2)
    print(f"Created item model definition JSON at {target_itemdef_path}\n")


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
        "description": "A Fabric mod for Minecraft v1.21.5 that creates a basic item via Python-generated code.",
        "authors": ["Your Name"],
    }
    update_mod_metadata(mod_json_path, new_metadata)

    # Step 3: Create Java source files for basic items.
    package_path = "com.example.mycustommod.items"
    create_item_files(target_dir, package_path)

    # Step 4: Update the mod initializer to load custom items.
    update_mod_initializer(target_dir)

    # Step 5: Optionally copy a texture file and generate model JSON files.
    texture_path = input(
        "Enter the full path to the texture PNG file for the custom item (or press Enter to skip): "
    ).strip()
    if texture_path:
        if os.path.exists(texture_path):
            copy_texture_and_generate_models(target_dir, "mycustommod", texture_path)
        else:
            print(
                f"Texture file not found at {texture_path}. Skipping texture copying."
            )
    else:
        print("No texture file provided, skipping texture and model generation.")

    print("Fabric mod project has been initialized with basic item creation code.\n")
    print("In Minecraft, run the following command to receive your custom item:")
    print("/give @s mycustommod:custom_item")


if __name__ == "__main__":
    main()
