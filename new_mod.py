#!/usr/bin/env python3
"""
This script initializes a Fabric mod project for Minecraft v1.21.5 by doing the following:
1. Clones the Fabric example mod repository.
2. Updates the mod metadata in the fabric.mod.json file.
3. Creates two Java source files to add a basic custom item:
   - CustomItem.java: A custom item class that plays a sound when used.
   - TutorialItems.java: A registry helper class that registers the custom item using the new 1.21.2+ method.
4. Patches the mod initializer (ExampleMod.java) to force the registration of the custom item.
Note: This updated code uses Identifier.of(...) instead of new Identifier(...),
and uses Registries.ITEM instead of Registry.ITEM.
The custom item is registered with the mod ID "mycustommod", so the in-game /give command is:
    /give @s mycustommod:custom_item
"""

import os
import json
import subprocess
import re


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
    # Note: We now attach the registry key to the settings.
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
        // Create a registry key for the item using the new method (since 1.21.2)
        final RegistryKey<Item> registryKey = RegistryKey.of(RegistryKeys.ITEM, Identifier.of("mycustommod", path));
        // Attach the registry key to the settings so the item id is set.
        settings = settings.registryKey(registryKey);
        // Register the item in the registry and return it.
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
    Updates the mod initializer file so that it calls TutorialItems.initialize() within the onInitialize() method.
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

    # If the call is already there, do nothing.
    if "TutorialItems.initialize()" in content:
        print(
            "Mod initializer already contains call to TutorialItems.initialize(). Skipping update.\n"
        )
        return

    # Insert the call after the opening brace of onInitialize().
    pattern = r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)"

    def replacer(match):
        indent = "    "  # Standard indent (4 spaces)
        return (
            match.group(0)
            + "\n"
            + indent
            + "com.example.mycustommod.items.TutorialItems.initialize();"
        )

    new_content, count = re.subn(pattern, replacer, content, count=1)
    if count > 0:
        with open(mod_init_path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print("Mod initializer updated successfully.\n")
    else:
        print("Could not locate onInitialize() method properly; skipping update.\n")


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

    print("Fabric mod project has been initialized with basic item creation code.\n")
    print("In Minecraft, run the following command to receive your custom item:")
    print("/give @s mycustommod:custom_item")


if __name__ == "__main__":
    main()
