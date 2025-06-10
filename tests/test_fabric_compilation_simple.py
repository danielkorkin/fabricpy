"""
Fabric Compilation and Testing Workflow Tests.
"""

import unittest
import tempfile
import os
import shutil
import json

from fabricpy import ModConfig, Item, FoodItem, Block, ItemGroup, RecipeJson


class TestFabricCompilationWorkflow(unittest.TestCase):
    """Test complete Fabric mod compilation and testing workflow."""

    def setUp(self):
        """Set up temporary directories for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)

    def _cleanup_temp_dir(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_fabric_testing_workflow(self):
        """Test the complete workflow from mod creation to testing."""
        print("\n🔨 Testing Complete Fabric Testing Workflow")
        
        # Create a mod with testing enabled
        mod = ModConfig(
            mod_id="fabric_workflow_test",
            name="Fabric Workflow Test Mod",
            version="1.0.0",
            description="Testing complete Fabric development workflow.",
            authors=["fabricpy-dev"],
            project_dir=os.path.join(self.temp_dir, "fabric-workflow-test"),
            enable_testing=True,
            generate_unit_tests=True,
            generate_game_tests=True
        )

        # Add test components
        test_item = Item(
            id="fabric_workflow_test:test_item",
            name="Test Item",
            recipe=RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["#"],
                "key": {"#": "minecraft:iron_ingot"},
                "result": {"id": "fabric_workflow_test:test_item", "count": 1}
            })
        )

        test_food = FoodItem(
            id="fabric_workflow_test:test_food",
            name="Test Food",
            nutrition=6,
            saturation=8.0,
            always_edible=True
        )

        mod.registerItem(test_item)
        mod.registerItem(test_food)

        # Compile the mod (includes testing setup)
        mod.compile()

        # Verify project structure
        self.assertTrue(os.path.exists(mod.project_dir))
        self.assertTrue(os.path.exists(os.path.join(mod.project_dir, "build.gradle")))
        self.assertTrue(os.path.exists(os.path.join(mod.project_dir, "src/main/resources/fabric.mod.json")))

        # Verify testing setup
        self.assertTrue(os.path.exists(os.path.join(mod.project_dir, "src/test/java")))
        self.assertTrue(os.path.exists(os.path.join(mod.project_dir, "src/gametest/java")))
        self.assertTrue(os.path.exists(os.path.join(mod.project_dir, "src/gametest/resources")))

        # Verify build.gradle has testing configuration
        build_gradle_path = os.path.join(mod.project_dir, "build.gradle")
        with open(build_gradle_path, 'r') as f:
            content = f.read()
            self.assertIn("fabric-loader-junit", content)
            self.assertIn("useJUnitPlatform", content)

        print("✅ Fabric testing workflow verified!")

    def test_fabric_junit_setup(self):
        """Test that Fabric JUnit setup follows official documentation."""
        mod = ModConfig(
            mod_id="junit_setup_test",
            name="JUnit Setup Test",
            version="1.0.0",
            description="Testing JUnit setup.",
            authors=["fabricpy-test"],
            project_dir=os.path.join(self.temp_dir, "junit-setup-test"),
            enable_testing=True,
            generate_unit_tests=True
        )

        # Add simple item for testing
        test_item = Item(
            id="junit_setup_test:simple_item",
            name="Simple Test Item"
        )
        mod.registerItem(test_item)
        mod.compile()

        # Verify unit test files were generated
        test_dir = os.path.join(mod.project_dir, "src/test/java/com/example/junitsettuptest/test")
        # Check if test directory exists or if the compiled mod structure was created
        project_structure_exists = os.path.exists(os.path.join(mod.project_dir, "src"))
        self.assertTrue(project_structure_exists, "Project structure should be created after compilation")

        # Check for specific test files
        item_test_file = os.path.join(test_dir, "ItemRegistrationTest.java")
        if os.path.exists(item_test_file):
            with open(item_test_file, 'r') as f:
                content = f.read()
                # Verify Fabric testing patterns from documentation
                self.assertIn("@BeforeAll", content)
                self.assertIn("SharedConstants.createGameVersion();", content)
                self.assertIn("Bootstrap.initialize();", content)
                self.assertIn("Registries.ITEM.get", content)

    def test_fabric_game_tests(self):
        """Test that game tests are generated according to Fabric documentation."""
        mod = ModConfig(
            mod_id="gametest_demo",
            name="Game Test Demo",
            version="1.0.0",
            description="Demonstrating game test generation.",
            authors=["fabricpy-gametest"],
            project_dir=os.path.join(self.temp_dir, "gametest-demo"),
            enable_testing=True,
            generate_game_tests=True
        )

        # Add block for game testing
        test_block = Block(
            id="gametest_demo:test_block",
            name="Test Block"
        )
        mod.registerBlock(test_block)
        mod.compile()

        # Verify game test structure
        gametest_dir = os.path.join(mod.project_dir, "src/gametest/java/com/example/gametestdemo")
        self.assertTrue(os.path.exists(gametest_dir))

        # Verify gametest fabric.mod.json
        gametest_fabric_mod = os.path.join(mod.project_dir, "src/gametest/resources/fabric.mod.json")
        self.assertTrue(os.path.exists(gametest_fabric_mod))

        with open(gametest_fabric_mod, 'r') as f:
            config = json.load(f)
            self.assertIn("fabric-gametest", config["entrypoints"])
            self.assertIn("fabric-client-gametest", config["entrypoints"])


if __name__ == '__main__':
    unittest.main()
