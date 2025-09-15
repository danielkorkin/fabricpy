"""
Unit tests for the ModConfig class and compilation process.
"""

import unittest
import tempfile
import shutil
import os
import json
import subprocess
from unittest.mock import patch

from fabricpy.modconfig import ModConfig
from fabricpy.item import Item
from fabricpy.fooditem import FoodItem
from fabricpy.toolitem import ToolItem
from fabricpy.block import Block
from fabricpy.itemgroup import ItemGroup
from fabricpy.recipejson import RecipeJson
from fabricpy import item_group


class TestModConfig(unittest.TestCase):
    """Test the ModConfig class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "test_mod")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_mod_config_creation(self):
        """Test creating a ModConfig instance."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="A test mod for unit testing",
            authors=["Test Author"],
            project_dir=self.project_dir
        )
        
        self.assertEqual(mod_config.mod_id, "testmod")
        self.assertEqual(mod_config.name, "Test Mod")
        self.assertEqual(mod_config.version, "1.0.0")
        self.assertEqual(mod_config.description, "A test mod for unit testing")
        self.assertEqual(mod_config.authors, ["Test Author"])
        self.assertEqual(mod_config.project_dir, self.project_dir)
        self.assertEqual(len(mod_config.registered_items), 0)
        self.assertEqual(len(mod_config.registered_blocks), 0)

    def test_mod_config_multiple_authors(self):
        """Test ModConfig with multiple authors."""
        authors = ["Author 1", "Author 2", "Author 3"]
        mod_config = ModConfig(
            mod_id="multiauthor",
            name="Multi Author Mod",
            version="2.0.0",
            description="A mod with multiple authors",
            authors=authors
        )
        
        self.assertEqual(mod_config.authors, authors)

    def test_mod_config_tuple_authors(self):
        """Test ModConfig with authors as tuple."""
        authors = ("Author 1", "Author 2")
        mod_config = ModConfig(
            mod_id="tupleauthor",
            name="Tuple Author Mod",
            version="1.0.0",
            description="A mod with tuple authors",
            authors=authors
        )
        
        # Should convert tuple to list
        self.assertEqual(mod_config.authors, ["Author 1", "Author 2"])
        self.assertIsInstance(mod_config.authors, list)

    def test_register_item(self):
        """Test registering items."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        item = Item(id="testmod:test_item", name="Test Item")
        mod_config.registerItem(item)
        
        self.assertEqual(len(mod_config.registered_items), 1)
        self.assertEqual(mod_config.registered_items[0], item)

    def test_register_food_item(self):
        """Test registering food items."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        food_item = FoodItem(
            id="testmod:test_food",
            name="Test Food",
            nutrition=4,
            saturation=0.3
        )
        mod_config.registerFoodItem(food_item)
        
        self.assertEqual(len(mod_config.registered_items), 1)
        self.assertEqual(mod_config.registered_items[0], food_item)

    def test_register_block(self):
        """Test registering blocks."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        block = Block(id="testmod:test_block", name="Test Block")
        mod_config.registerBlock(block)
        
        self.assertEqual(len(mod_config.registered_blocks), 1)
        self.assertEqual(mod_config.registered_blocks[0], block)

    def test_to_java_constant_simple(self):
        """Test converting simple IDs to Java constants."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Simple ID without namespace
        self.assertEqual(mod_config._to_java_constant("test_item"), "TEST_ITEM")
        
        # ID with namespace
        self.assertEqual(mod_config._to_java_constant("testmod:example_item"), "TESTMOD_EXAMPLE_ITEM")

    def test_to_java_constant_special_chars(self):
        """Test converting IDs with special characters to Java constants."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # With colons and hyphens
        self.assertEqual(mod_config._to_java_constant("test-mod:my-item"), "TEST_MOD_MY_ITEM")
        
        # With dots
        self.assertEqual(mod_config._to_java_constant("test.mod.item"), "TEST_MOD_ITEM")
        
        # With spaces
        self.assertEqual(mod_config._to_java_constant("test mod item"), "TEST_MOD_ITEM")
        
        # Starting with digit
        self.assertEqual(mod_config._to_java_constant("1test_item"), "_1TEST_ITEM")

    def test_custom_groups_property_empty(self):
        """Test _custom_groups property with no custom groups."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Add items with vanilla groups
        item1 = Item(id="testmod:item1", name="Item 1", item_group=item_group.TOOLS)
        item2 = Item(id="testmod:item2", name="Item 2", item_group=item_group.COMBAT)
        mod_config.registerItem(item1)
        mod_config.registerItem(item2)
        
        custom_groups = mod_config._custom_groups
        self.assertEqual(len(custom_groups), 0)

    def test_custom_groups_property_with_custom_groups(self):
        """Test _custom_groups property with custom groups."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Create custom groups
        custom_group1 = ItemGroup(id="custom1", name="Custom Group 1")
        custom_group2 = ItemGroup(id="custom2", name="Custom Group 2")
        
        # Add items with custom groups
        item1 = Item(id="testmod:item1", name="Item 1", item_group=custom_group1)
        item2 = Item(id="testmod:item2", name="Item 2", item_group=custom_group2)
        item3 = Item(id="testmod:item3", name="Item 3", item_group=custom_group1)  # Same group
        mod_config.registerItem(item1)
        mod_config.registerItem(item2)
        mod_config.registerItem(item3)
        
        # Add block with custom group
        block1 = Block(id="testmod:block1", name="Block 1", item_group=custom_group1)
        mod_config.registerBlock(block1)
        
        custom_groups = mod_config._custom_groups
        self.assertEqual(len(custom_groups), 2)
        self.assertIn(custom_group1, custom_groups)
        self.assertIn(custom_group2, custom_groups)

    @patch('subprocess.check_call')
    def test_clone_repository(self, mock_subprocess):
        """Test cloning repository."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Mock successful git clone
        mock_subprocess.return_value = None
        
        mod_config.clone_repository("https://github.com/test/repo.git", self.project_dir)
        
        mock_subprocess.assert_called_once_with(
            ["git", "clone", "https://github.com/test/repo.git", self.project_dir]
        )

    def test_update_mod_metadata(self):
        """Test updating fabric.mod.json metadata."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Create a sample fabric.mod.json
        fabric_mod_json = {
            "schemaVersion": 1,
            "id": "example",
            "version": "0.1.0",
            "name": "Example Mod",
            "description": "Example description",
            "authors": ["Original Author"]
        }
        
        fabric_json_path = os.path.join(self.temp_dir, "fabric.mod.json")
        with open(fabric_json_path, 'w') as f:
            json.dump(fabric_mod_json, f, indent=2)
        
        # Update metadata
        mod_config.update_mod_metadata(fabric_json_path, {
            "id": "testmod",
            "name": "Test Mod",
            "version": "1.0.0",
            "description": "A test mod",
            "authors": ["Test Author"]
        })
        
        # Read back and verify
        with open(fabric_json_path, 'r') as f:
            updated_json = json.load(f)
        
        self.assertEqual(updated_json["id"], "testmod")
        self.assertEqual(updated_json["name"], "Test Mod")
        self.assertEqual(updated_json["version"], "1.0.0")
        self.assertEqual(updated_json["description"], "A test mod")
        self.assertEqual(updated_json["authors"], ["Test Author"])
        # Original fields should be preserved
        self.assertEqual(updated_json["schemaVersion"], 1)

    def test_update_mod_metadata_missing_file(self):
        """Test updating metadata when file doesn't exist."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.json")
        
        with self.assertRaises(FileNotFoundError):
            mod_config.update_mod_metadata(nonexistent_path, {})

    def test_write_recipe_files_no_recipes(self):
        """Test writing recipe files when no recipes exist."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Add items without recipes
        item = Item(id="testmod:no_recipe", name="No Recipe Item")
        mod_config.registerItem(item)
        
        # Should not create any files
        mod_config.write_recipe_files(self.project_dir, "testmod")
        
        recipe_dir = os.path.join(self.project_dir, "src", "main", "resources", "data", "testmod", "recipe")
        self.assertFalse(os.path.exists(recipe_dir))

    def test_write_recipe_files_with_recipes(self):
        """Test writing recipe files when recipes exist."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Create recipe
        recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "testmod:stone_item", "count": 1}
        })
        
        # Add item with recipe
        item = Item(
            id="testmod:stone_item",
            name="Stone Item",
            recipe=recipe
        )
        mod_config.registerItem(item)
        
        # Write recipe files
        mod_config.write_recipe_files(self.project_dir, "testmod")
        
        # Check that file was created
        recipe_dir = os.path.join(self.project_dir, "src", "main", "resources", "data", "testmod", "recipe")
        recipe_file = os.path.join(recipe_dir, "stone_item.json")
        
        self.assertTrue(os.path.exists(recipe_file))
        
        # Verify content
        with open(recipe_file, 'r') as f:
            content = f.read()
        
        # Should contain the recipe JSON
        self.assertIn("minecraft:crafting_shaped", content)
        self.assertIn("testmod:stone_item", content)

    @patch('subprocess.check_call')
    def test_build_method(self, mock_subprocess):
        """Test build method."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Create project directory
        os.makedirs(self.project_dir)
        
        mod_config.build()
        
        mock_subprocess.assert_called_once_with(
            ["./gradlew", "build"],
            cwd=self.project_dir
        )

    def test_build_method_no_project_dir(self):
        """Test build method when project directory doesn't exist."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Don't create project directory
        
        with self.assertRaises(RuntimeError) as context:
            mod_config.build()
        
        self.assertIn("Project directory not found", str(context.exception))

    @patch('fabricpy.modconfig.subprocess.check_call')
    @patch('fabricpy.modconfig.os.chdir')
    @patch('fabricpy.modconfig.os.getcwd')
    def test_run_method(self, mock_getcwd, mock_chdir, mock_subprocess):
        """Test run method."""
        mock_getcwd.return_value = "/original/cwd"
        
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Create project directory
        os.makedirs(self.project_dir)
        
        mod_config.run()
        
        # Check that we changed to the project directory
        mock_chdir.assert_any_call(self.project_dir)
        # Check that we changed back to original directory
        mock_chdir.assert_any_call("/original/cwd")
        # Check that subprocess was called without cwd (since we use os.chdir)
        mock_subprocess.assert_called_once_with(["./gradlew", "runClient"])

    def test_run_method_no_project_dir(self):
        """Test run method when project directory doesn't exist."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Don't create project directory
        
        with self.assertRaises(FileNotFoundError) as context:
            mod_config.run()
        
        self.assertIn("does not exist", str(context.exception))

    @patch('subprocess.check_call')
    def test_build_method_with_gradle_properties(self, mock_subprocess):
        """Test build method ensures gradle.properties has required properties."""
        mod_config = ModConfig(
            mod_id="test-mod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Create project directory
        os.makedirs(self.project_dir)
        
        # Call _ensure_gradle_properties to create gradle.properties
        mod_config._ensure_gradle_properties(self.project_dir)
        
        # Verify gradle.properties has required properties in proper format
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        with open(gradle_props_path, 'r') as f:
            content = f.read()
        
        # Check for proper Fabric format
        self.assertIn("# Done to increase the memory available to gradle.", content)
        self.assertIn("org.gradle.jvmargs=-Xmx1G", content)
        self.assertIn("org.gradle.parallel=true", content)
        self.assertIn("# Fabric Properties", content)
        self.assertIn("minecraft_version=1.21.5", content)
        self.assertIn("yarn_mappings=1.21.5+build.1", content)
        self.assertIn("loader_version=0.16.10", content)
        self.assertIn("loom_version=1.11-SNAPSHOT", content)
        self.assertIn("# Mod Properties", content)
        self.assertIn("mod_version=1.0.0", content)
        self.assertIn("maven_group=com.example", content)
        self.assertIn("archives_base_name=test-mod", content)
        self.assertIn("mod_id=test-mod", content)
        self.assertIn("# Dependencies", content)
        self.assertIn("fabric_version=0.119.5+1.21.5", content)
        
        mod_config.build()
        
        mock_subprocess.assert_called_once_with(
            ["./gradlew", "build"],
            cwd=self.project_dir
        )

    @patch('subprocess.check_call')
    def test_build_method_gradle_failure(self, mock_subprocess):
        """Test build method handles Gradle build failures."""
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Create project directory
        os.makedirs(self.project_dir)
        
        # Mock gradle build failure
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, ["./gradlew", "build"])
        
        with self.assertRaises(subprocess.CalledProcessError):
            mod_config.build()

    @patch('subprocess.check_call')
    def test_build_method_with_complex_project(self, mock_subprocess):
        """Test build method with a complex project structure."""
        mod_config = ModConfig(
            mod_id="complex_mod",
            name="Complex Mod",
            version="2.1.0",
            description="Complex test mod",
            authors=["Dev1", "Dev2"],
            project_dir=self.project_dir
        )
        
        # Create complex project structure
        os.makedirs(self.project_dir)
        os.makedirs(os.path.join(self.project_dir, "src", "main", "java"))
        os.makedirs(os.path.join(self.project_dir, "src", "main", "resources"))
        
        # Create build.gradle file
        build_gradle = os.path.join(self.project_dir, "build.gradle")
        with open(build_gradle, 'w') as f:
            f.write("// Complex build.gradle\napply plugin: 'fabric-loom'\n")
        
        mod_config.build()
        
        mock_subprocess.assert_called_once_with(
            ["./gradlew", "build"],
            cwd=self.project_dir
        )

    @patch('fabricpy.modconfig.subprocess.check_call')
    @patch('fabricpy.modconfig.os.chdir')
    @patch('fabricpy.modconfig.os.getcwd')
    def test_run_method_with_gradle_properties(self, mock_getcwd, mock_chdir, mock_subprocess):
        """Test run method with gradle.properties management."""
        mock_getcwd.return_value = "/original/cwd"
        
        mod_config = ModConfig(
            mod_id="run-test-mod",
            name="Run Test Mod",
            version="1.5.0",
            description="Test mod for run method",
            authors=["RunTester"],
            project_dir=self.project_dir
        )
        
        # Create project directory and gradle.properties
        os.makedirs(self.project_dir)
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        with open(gradle_props_path, 'w') as f:
            f.write("# Test gradle.properties\n")
        
        # Ensure gradle.properties has required properties
        mod_config._ensure_gradle_properties(self.project_dir)
        
        # Verify gradle.properties was completely regenerated with proper format
        with open(gradle_props_path, 'r') as f:
            content = f.read()
        
        # Should have the standard Fabric format (overwrites any existing content)
        self.assertIn("# Done to increase the memory available to gradle.", content)
        self.assertIn("org.gradle.jvmargs=-Xmx1G", content)
        self.assertIn("org.gradle.parallel=true", content)
        self.assertIn("# Fabric Properties", content)
        self.assertIn("minecraft_version=1.21.5", content)
        self.assertIn("yarn_mappings=1.21.5+build.1", content)
        self.assertIn("loader_version=0.16.10", content)
        self.assertIn("loom_version=1.11-SNAPSHOT", content)
        self.assertIn("# Mod Properties", content)
        self.assertIn("mod_version=1.5.0", content)  # Uses the ModConfig version
        self.assertIn("maven_group=com.example", content)
        self.assertIn("archives_base_name=run-test-mod", content)
        self.assertIn("mod_id=run-test-mod", content)
        self.assertIn("# Dependencies", content)
        self.assertIn("fabric_version=0.119.5+1.21.5", content)
        
        mod_config.run()
        
        # Verify directory changes and command execution
        mock_chdir.assert_any_call(self.project_dir)
        mock_chdir.assert_any_call("/original/cwd")
        mock_subprocess.assert_called_once_with(["./gradlew", "runClient"])

    @patch('fabricpy.modconfig.subprocess.check_call')
    @patch('fabricpy.modconfig.os.chdir')
    @patch('fabricpy.modconfig.os.getcwd')
    def test_run_method_gradle_failure(self, mock_getcwd, mock_chdir, mock_subprocess):
        """Test run method handles Gradle runClient failures."""
        mock_getcwd.return_value = "/original/cwd"
        
        mod_config = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Create project directory
        os.makedirs(self.project_dir)
        
        # Mock gradle runClient failure
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, ["./gradlew", "runClient"])
        
        with self.assertRaises(subprocess.CalledProcessError):
            mod_config.run()
        
        # Verify we still restore the original directory
        mock_chdir.assert_any_call("/original/cwd")

    @patch('fabricpy.modconfig.subprocess.check_call')
    @patch('fabricpy.modconfig.os.chdir')
    @patch('fabricpy.modconfig.os.getcwd')
    def test_run_method_with_special_characters_in_mod_id(self, mock_getcwd, mock_chdir, mock_subprocess):
        """Test run method with special characters in mod_id."""
        mock_getcwd.return_value = "/original/cwd"
        
        mod_config = ModConfig(
            mod_id="test-mod_with.special-chars",
            name="Test Mod with Special Chars",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.project_dir
        )
        
        # Create project directory and gradle.properties
        os.makedirs(self.project_dir)
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        with open(gradle_props_path, 'w') as f:
            f.write("# Test gradle.properties\n")
        
        # Ensure gradle.properties has required properties
        mod_config._ensure_gradle_properties(self.project_dir)
        
        # Verify gradle.properties handles special characters correctly in standard format
        with open(gradle_props_path, 'r') as f:
            content = f.read()
        
        # Should have standard Fabric format with special characters preserved
        self.assertIn("# Done to increase the memory available to gradle.", content)
        self.assertIn("archives_base_name=test-mod_with.special-chars", content)
        self.assertIn("mod_id=test-mod_with.special-chars", content)
        self.assertIn("mod_version=1.0.0", content)
        self.assertIn("maven_group=com.example", content)
        
        mod_config.run()
        
        mock_subprocess.assert_called_once_with(["./gradlew", "runClient"])

    def test_ensure_gradle_properties_existing_properties(self):
        """Test _ensure_gradle_properties creates standard format regardless of existing content."""
        mod_config = ModConfig(
            mod_id="existing-props",
            name="Existing Props Test",
            version="2.1.0",
            description="Test",
            authors=["Test"]
        )
        
        # Create project directory and gradle.properties with existing properties
        os.makedirs(self.project_dir)
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        original_content = """# Existing gradle.properties
archives_base_name=existing-props
mod_id=existing-props
org.gradle.jvmargs=-Xmx1G
org.gradle.parallel=false
"""
        with open(gradle_props_path, 'w') as f:
            f.write(original_content)
        
        mod_config._ensure_gradle_properties(self.project_dir)
        
        # Read the file after processing
        with open(gradle_props_path, 'r') as f:
            final_content = f.read()

        # Should have standard Fabric format (overwrites existing content)
        self.assertIn("# Done to increase the memory available to gradle.", final_content)
        self.assertIn("org.gradle.jvmargs=-Xmx1G", final_content)
        self.assertIn("org.gradle.parallel=true", final_content)
        self.assertIn("# Fabric Properties", final_content)
        self.assertIn("minecraft_version=1.21.5", final_content)
        self.assertIn("yarn_mappings=1.21.5+build.1", final_content)
        self.assertIn("loader_version=0.16.10", final_content)
        self.assertIn("loom_version=1.11-SNAPSHOT", final_content)
        self.assertIn("# Mod Properties", final_content)
        self.assertIn("mod_version=2.1.0", final_content)  # Uses ModConfig version
        self.assertIn("maven_group=com.example", final_content)
        self.assertIn("archives_base_name=existing-props", final_content)
        self.assertIn("mod_id=existing-props", final_content)
        self.assertIn("# Dependencies", final_content)
        self.assertIn("fabric_version=0.119.5+1.21.5", final_content)

    def test_ensure_gradle_properties_no_file(self):
        """Test _ensure_gradle_properties creates file when it doesn't exist."""
        mod_config = ModConfig(
            mod_id="no-file-test",
            name="No File Test",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Create project directory but no gradle.properties
        os.makedirs(self.project_dir)
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        
        # File shouldn't exist initially
        self.assertFalse(os.path.exists(gradle_props_path))
        
        # Call _ensure_gradle_properties
        mod_config._ensure_gradle_properties(self.project_dir)
        
        # File should now exist with standard format
        self.assertTrue(os.path.exists(gradle_props_path))
        
        with open(gradle_props_path, 'r') as f:
            content = f.read()
        
        # Should have standard Fabric format
        self.assertIn("# Done to increase the memory available to gradle.", content)
        self.assertIn("archives_base_name=no-file-test", content)
        self.assertIn("mod_id=no-file-test", content)
        self.assertIn("mod_version=1.0.0", content)
        self.assertIn("loom_version=1.11-SNAPSHOT", content)

    def test_ensure_gradle_properties_empty_file(self):
        """Test _ensure_gradle_properties with empty gradle.properties."""
        mod_config = ModConfig(
            mod_id="empty-file-test",
            name="Empty File Test",
            version="1.0.0",
            description="Test",
            authors=["Test"]
        )
        
        # Create project directory and empty gradle.properties
        os.makedirs(self.project_dir)
        gradle_props_path = os.path.join(self.project_dir, "gradle.properties")
        with open(gradle_props_path, 'w') as f:
            f.write("")  # Empty file
        
        mod_config._ensure_gradle_properties(self.project_dir)
        
        # Read the file after processing
        with open(gradle_props_path, 'r') as f:
            content = f.read()
        
        # Should create standard Fabric format (overwrites empty file)
        self.assertIn("# Done to increase the memory available to gradle.", content)
        self.assertIn("archives_base_name=empty-file-test", content)
        self.assertIn("mod_id=empty-file-test", content)
        self.assertIn("org.gradle.jvmargs=-Xmx1G", content)
        self.assertIn("org.gradle.parallel=true", content)
        self.assertIn("mod_version=1.0.0", content)
        self.assertIn("maven_group=com.example", content)
        self.assertIn("minecraft_version=1.21.5", content)
        self.assertIn("loom_version=1.11-SNAPSHOT", content)


class TestModConfigIntegration(unittest.TestCase):
    """Integration tests for ModConfig with all components."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "test_mod")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_comprehensive_mod_setup(self):
        """Test setting up a mod with all types of components."""
        mod_config = ModConfig(
            mod_id="comprehensive",
            name="Comprehensive Test Mod",
            version="2.0.0",
            description="A comprehensive test mod with all features",
            authors=["Test Author 1", "Test Author 2"],
            project_dir=self.project_dir
        )
        
        # Create custom item group
        custom_group = ItemGroup(id="test_materials", name="Test Materials")
        
        # Create items
        basic_item = Item(
            id="comprehensive:basic_item",
            name="Basic Item",
            item_group=item_group.INGREDIENTS
        )
        
        recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["##", "##"],
            "key": {"#": "minecraft:iron_ingot"},
            "result": {"id": "comprehensive:iron_block", "count": 1}
        })
        
        crafted_item = Item(
            id="comprehensive:iron_block",
            name="Iron Block",
            recipe=recipe,
            item_group=custom_group
        )
        
        # Create food item
        food_item = FoodItem(
            id="comprehensive:golden_apple",
            name="Golden Apple",
            nutrition=4,
            saturation=9.6,
            always_edible=True,
            item_group=item_group.FOOD_AND_DRINK
        )
        
        # Create block
        block = Block(
            id="comprehensive:test_block",
            name="Test Block",
            item_group=item_group.BUILDING_BLOCKS
        )
        
        # Register all components
        mod_config.registerItem(basic_item)
        mod_config.registerItem(crafted_item)
        mod_config.registerFoodItem(food_item)
        mod_config.registerBlock(block)
        
        # Verify registration
        self.assertEqual(len(mod_config.registered_items), 3)
        self.assertEqual(len(mod_config.registered_blocks), 1)
        
        # Verify custom groups are detected
        custom_groups = mod_config._custom_groups
        self.assertEqual(len(custom_groups), 1)
        self.assertIn(custom_group, custom_groups)

    def test_tool_item_properties_applied(self):
        """ToolItem settings are emitted into generated Java source."""
        mod_config = ModConfig(
            mod_id="tools",
            name="Tools Mod",
            version="1.0.0",
            description="Test mod for tools",
            authors=["Tester"],
            project_dir=self.project_dir,
        )

        tool = ToolItem(
            id="tools:ruby_pickaxe",
            name="Ruby Pickaxe",
            durability=500,
            mining_speed_multiplier=8.0,
            attack_damage=3.0,
            mining_level=2,
            enchantability=22,
            repair_ingredient="minecraft:ruby",
        )

        mod_config.registerItem(tool)
        mod_config.create_item_files(self.project_dir, "com.example.tools.items")

        tut_path = os.path.join(
            self.project_dir,
            "src",
            "main",
            "java",
            "com",
            "example",
            "tools",
            "items",
            "TutorialItems.java",
        )

        with open(tut_path, "r", encoding="utf-8") as fh:
            content = fh.read()

        self.assertIn(
            "new CustomToolItem(500, 8.0f, 3.0f, 2, 22, \"minecraft:ruby\", 1, s)",
            content,
        )

        custom_path = os.path.join(
            self.project_dir,
            "src",
            "main",
            "java",
            "com",
            "example",
            "tools",
            "items",
            "CustomToolItem.java",
        )
        self.assertTrue(os.path.exists(custom_path))

        with open(custom_path, "r", encoding="utf-8") as fh:
            custom_content = fh.read()

        self.assertIn("settings.repairable(Registries.ITEM.get(Identifier.of(repairIngredientId)))", custom_content)
        self.assertIn("EntityAttributes.ATTACK_DAMAGE", custom_content)
        self.assertIn("Operation.ADD_VALUE", custom_content)
        self.assertIn("AttributeModifierSlot.MAINHAND", custom_content)

    def test_multiple_items_same_group(self):
        """Test multiple items in the same custom group."""
        mod_config = ModConfig(
            mod_id="grouped",
            name="Grouped Test Mod",
            version="1.0.0",
            description="Test mod for grouping",
            authors=["Test Author"]
        )
        
        # Create custom group
        weapons_group = ItemGroup(id="test_weapons", name="Test Weapons")
        
        # Create multiple items in same group
        sword = ToolItem(
            id="grouped:test_sword",
            name="Test Sword",
            item_group=weapons_group,
            durability=250,
        )
        
        bow = Item(
            id="grouped:test_bow",
            name="Test Bow",
            item_group=weapons_group
        )
        
        shield = Item(
            id="grouped:test_shield",
            name="Test Shield",
            item_group=weapons_group
        )
        
        mod_config.registerItem(sword)
        mod_config.registerItem(bow)
        mod_config.registerItem(shield)
        
        # Should only have one custom group
        custom_groups = mod_config._custom_groups
        self.assertEqual(len(custom_groups), 1)
        self.assertIn(weapons_group, custom_groups)

    def test_mixed_vanilla_and_custom_groups(self):
        """Test items with both vanilla and custom groups."""
        mod_config = ModConfig(
            mod_id="mixed",
            name="Mixed Groups Mod",
            version="1.0.0",
            description="Test mod with mixed groups",
            authors=["Test Author"]
        )
        
        # Create custom group
        custom_group = ItemGroup(id="special_items", name="Special Items")
        
        # Items with vanilla groups
        vanilla_item1 = Item(
            id="mixed:tool",
            name="Tool",
            item_group=item_group.TOOLS
        )
        
        vanilla_item2 = Item(
            id="mixed:food",
            name="Food",
            item_group=item_group.FOOD_AND_DRINK
        )
        
        # Items with custom group
        custom_item1 = Item(
            id="mixed:special1",
            name="Special Item 1",
            item_group=custom_group
        )
        
        custom_item2 = Item(
            id="mixed:special2",
            name="Special Item 2",
            item_group=custom_group
        )
        
        mod_config.registerItem(vanilla_item1)
        mod_config.registerItem(vanilla_item2)
        mod_config.registerItem(custom_item1)
        mod_config.registerItem(custom_item2)
        
        # Should only detect custom groups
        custom_groups = mod_config._custom_groups
        self.assertEqual(len(custom_groups), 1)
        self.assertIn(custom_group, custom_groups)


if __name__ == '__main__':
    unittest.main()
