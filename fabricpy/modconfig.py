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

    def registerItem(self, item):
        """
        Registers a custom item into the mod.
        :param item: An instance of fabricpy.Item (or subclass) representing a custom item.
        """
        self.registered_items.append(item)

    def compile(self):
        """
        Creates/updates the Fabric mod project files:
          1. Clones the example repository if the target directory does not exist.
          2. Updates the fabric.mod.json file dynamically.
          3. Creates Java source files with custom item registration.
          4. Patches the mod initializer to call the item registry initializer.
          5. Iterates over registered items; if an item provides a valid texture_path,
             automatically copies the texture file (renaming it to match the item’s id) and generates the model JSON files.
          6. Updates (or creates) the language file for friendly item names.
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
        # Default package path is: com.example.<mod_id>.items
        package_path = f"com.example.{self.mod_id}.items"
        self.create_item_files(self.project_dir, package_path)

        # 4. Update mod initializer to call the custom items initializer.
        self.update_mod_initializer(self.project_dir, package_path)

        # 5. Process each registered item's texture.
        self.copy_texture_and_generate_models(self.project_dir, self.mod_id)

        # 6. Update the language file for custom item display names.
        self.update_item_lang_file(self.project_dir, self.mod_id)

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

    def create_item_files(self, project_dir, package_path):
        # Create the Java package directory based on the package path.
        java_src_dir = os.path.join(project_dir, "src", "main", "java")
        full_package_dir = os.path.join(java_src_dir, *package_path.split("."))
        os.makedirs(full_package_dir, exist_ok=True)
        print(f"Created/verifying Java package directory: {full_package_dir}\n")

        # Generate the TutorialItems.java file with dynamic registration.
        tutorial_items_content = self.generate_tutorial_items_content(package_path)
        tutorial_items_path = os.path.join(full_package_dir, "TutorialItems.java")
        with open(tutorial_items_path, "w", encoding="utf-8") as file:
            file.write(tutorial_items_content)
        print(f"Created file: {tutorial_items_path}\n")

        # Create a default CustomItem.java file as a template.
        custom_item_content = self.generate_custom_item_content(package_path)
        custom_item_path = os.path.join(full_package_dir, "CustomItem.java")
        with open(custom_item_path, "w", encoding="utf-8") as file:
            file.write(custom_item_content)
        print(f"Created file: {custom_item_path}\n")

    def generate_tutorial_items_content(self, package_path):
        """
        Generates the content for the Java file that registers all custom items.
        Each registered item produces a registration line using its id and max stack size.
        """
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
        lines.append("import java.util.function.Function;")
        lines.append("")
        lines.append("public final class TutorialItems {")
        lines.append("    private TutorialItems() {}")
        lines.append("")
        # Dynamically generate a registration line for each registered item.
        for item in self.registered_items:
            constant_name = (
                item.id.upper()
            )  # A simple conversion; you might add further sanitization.
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
        lines.append("    public static void initialize() {}")
        lines.append("}")
        return "\n".join(lines)

    def generate_custom_item_content(self, package_path):
        """
        Generates a basic custom item Java class template.
        """
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
        """
        Patches the mod initializer file (e.g. ExampleMod.java) so that it calls TutorialItems.initialize().
        """
        mod_init_path = os.path.join(
            project_dir, "src", "main", "java", "com", "example", "ExampleMod.java"
        )
        if not os.path.exists(mod_init_path):
            print(
                f"Mod initializer file not found at {mod_init_path}, skipping update."
            )
            return
        print(
            f"Updating mod initializer at {mod_init_path} to register custom items..."
        )
        with open(mod_init_path, "r", encoding="utf-8") as file:
            content = file.read()
        if f"{package_path}.TutorialItems.initialize()" in content:
            print(
                "Mod initializer already contains call to TutorialItems.initialize(). Skipping update.\n"
            )
            return
        pattern = r"(public\s+void\s+onInitialize\s*\(\s*\)\s*\{)"

        def replacer(match):
            return match.group(0) + f"\n    {package_path}.TutorialItems.initialize();"

        new_content, count = re.subn(pattern, replacer, content, count=1)
        if count > 0:
            with open(mod_init_path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print("Mod initializer updated successfully.\n")
        else:
            print("Could not locate onInitialize() method properly; skipping update.\n")

    def copy_texture_and_generate_models(self, project_dir, mod_id):
        """
        Iterates over registered items. For each item with a valid texture_path,
        it copies the texture to the calculated asset directory under textures/item (renaming it to match the item id),
        and generates corresponding model JSON files that use the item id.
        """
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
                # Rename the copied texture file to match the item.id.
                target_texture_filename = f"{item.id}.png"
                target_texture_path = os.path.join(texture_dir, target_texture_filename)
                shutil.copy(item.texture_path, target_texture_path)
                print(
                    f"Copied texture file from {item.texture_path} to {target_texture_path}"
                )

                # Generate model JSON using the item id for the texture reference.
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
                print(
                    f"No valid texture path for item '{item.id}'. Skipping texture copy."
                )

    def update_item_lang_file(self, project_dir, mod_id):
        """
        Creates or updates the language file so that each custom item shows its friendly name.
        Iterates over all registered items and sets a language key of the form:
            item.<mod_id>.<item.id> = <item.name>
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

        for item in self.registered_items:
            lang_data[f"item.{mod_id}.{item.id}"] = item.name

        with open(lang_file, "w", encoding="utf-8") as file:
            json.dump(lang_data, file, indent=2)
        print(f"Updated language file at {lang_file} with custom item translations.\n")
