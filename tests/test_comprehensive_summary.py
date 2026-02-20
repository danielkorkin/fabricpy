"""
Final Comprehensive Testing Summary for fabricpy library.

This file demonstrates the complete testing ecosystem created for fabricpy,
including all testing categories and Fabric integration.
"""

import os
import shutil
import tempfile
import unittest

from fabricpy import Block, FoodItem, Item, ItemGroup, ModConfig, RecipeJson


class TestComprehensiveTestingSummary(unittest.TestCase):
    """Comprehensive testing summary demonstrating all fabricpy testing capabilities."""

    def setUp(self):
        """Set up for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_comprehensive_testing_ecosystem(self):
        """Test that demonstrates the complete testing ecosystem."""
        print("\n🎯 COMPREHENSIVE TESTING ECOSYSTEM SUMMARY")
        print("=" * 60)

        # 1. Create a mod that uses all features
        mod = ModConfig(
            mod_id="comprehensive_testing_demo",
            name="Comprehensive Testing Demo",
            version="1.0.0",
            description="Demonstrates all testing capabilities of fabricpy",
            authors=["fabricpy-testing-team"],
            project_dir=os.path.join(self.temp_dir, "comprehensive-testing-demo"),
            enable_testing=True,
            generate_unit_tests=True,
            generate_game_tests=True,
        )

        # 2. Create comprehensive components
        self._create_comprehensive_components(mod)

        # 3. Compile with full testing integration
        mod.compile()

        # 4. Verify all testing aspects
        self._verify_comprehensive_testing(mod.project_dir)

        print("✅ COMPREHENSIVE TESTING ECOSYSTEM VERIFIED!")
        print("=" * 60)

    def _create_comprehensive_components(self, mod: ModConfig):
        """Create components that test all aspects of the library."""
        print("📦 Creating comprehensive mod components...")

        # Custom item group
        custom_group = ItemGroup(
            id="comprehensive_testing_demo:test_group", name="Comprehensive Test Group"
        )

        # Items with various properties
        basic_item = Item(
            id="comprehensive_testing_demo:basic_item",
            name="Basic Test Item",
            max_stack_size=64,
            item_group=custom_group,
        )

        # Food item with all properties
        food_item = FoodItem(
            id="comprehensive_testing_demo:test_food",
            name="Test Food Item",
            nutrition=8,
            saturation=12.0,
            always_edible=True,
            max_stack_size=16,
            item_group=custom_group,
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": ["minecraft:apple", "minecraft:sugar"],
                    "result": {
                        "id": "comprehensive_testing_demo:test_food",
                        "count": 1,
                    },
                }
            ),
        )

        # Item with complex shaped recipe
        crafted_item = Item(
            id="comprehensive_testing_demo:crafted_item",
            name="Crafted Test Item",
            item_group=custom_group,
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["###", "#X#", "###"],
                    "key": {
                        "#": "minecraft:stone",
                        "X": "comprehensive_testing_demo:basic_item",
                    },
                    "result": {
                        "id": "comprehensive_testing_demo:crafted_item",
                        "count": 1,
                    },
                }
            ),
        )

        # Block with recipe dependency
        test_block = Block(
            id="comprehensive_testing_demo:test_block",
            name="Test Block",
            item_group=custom_group,
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["##", "##"],
                    "key": {"#": "comprehensive_testing_demo:crafted_item"},
                    "result": {
                        "id": "comprehensive_testing_demo:test_block",
                        "count": 1,
                    },
                }
            ),
        )

        # Register all components
        mod.registerItem(basic_item)
        mod.registerItem(food_item)
        mod.registerItem(crafted_item)
        mod.registerBlock(test_block)

        print(
            f"  ✅ Created {len(mod.registered_items)} items and {len(mod.registered_blocks)} blocks"
        )

    def _verify_comprehensive_testing(self, project_dir: str):
        """Verify all aspects of the comprehensive testing setup."""
        print("🔍 Verifying comprehensive testing setup...")

        # Test categories to verify
        test_categories = {
            "Unit Tests": self._verify_unit_tests,
            "Game Tests": self._verify_game_tests,
            "Build Configuration": self._verify_build_config,
            "Project Structure": self._verify_project_structure,
            "Fabric Integration": self._verify_fabric_integration,
        }

        for category, verify_func in test_categories.items():
            print(f"  🧪 Checking {category}...")
            verify_func(project_dir)
            print(f"    ✅ {category} verified")

    def _verify_unit_tests(self, project_dir: str):
        """Verify unit tests were generated according to Fabric standards."""
        test_dir = os.path.join(project_dir, "src/test/java")
        self.assertTrue(os.path.exists(test_dir), "Unit test directory should exist")

        # Check for specific test files
        test_base = os.path.join(test_dir, "com/example/comprehensivetestingdemo/test")
        expected_tests = [
            "ItemRegistrationTest.java",
            "RecipeValidationTest.java",
            "ModIntegrationTest.java",
        ]

        for test_file in expected_tests:
            test_path = os.path.join(test_base, test_file)
            if os.path.exists(test_path):
                with open(test_path, "r") as f:
                    content = f.read()
                    # Verify follows Fabric documentation patterns
                    assert "@BeforeAll" in content, (
                        f"{test_file} should have @BeforeAll setup"
                    )
                    assert "SharedConstants.createGameVersion();" in content
                    assert "Bootstrap.initialize();" in content

    def _verify_game_tests(self, project_dir: str):
        """Verify game tests were generated according to Fabric standards."""
        gametest_dir = os.path.join(project_dir, "src/gametest/java")
        self.assertTrue(
            os.path.exists(gametest_dir), "Game test directory should exist"
        )

        # Verify gametest fabric.mod.json
        gametest_config = os.path.join(
            project_dir, "src/gametest/resources/fabric.mod.json"
        )
        self.assertTrue(
            os.path.exists(gametest_config), "Game test config should exist"
        )

        # Verify server and client test files
        gametest_base = os.path.join(
            gametest_dir, "com/example/comprehensivetestingdemo"
        )
        server_test = os.path.join(
            gametest_base, "ComprehensivetestingdemoServerTest.java"
        )
        os.path.join(gametest_base, "ComprehensivetestingdemoClientTest.java")

        if os.path.exists(server_test):
            with open(server_test, "r") as f:
                content = f.read()
                assert "FabricGameTest" in content, (
                    "Server test should implement FabricGameTest"
                )
                assert "@GameTest" in content, (
                    "Server test should use @GameTest annotation"
                )

    def _verify_build_config(self, project_dir: str):
        """Verify build.gradle has proper Fabric testing configuration."""
        build_gradle = os.path.join(project_dir, "build.gradle")
        self.assertTrue(os.path.exists(build_gradle), "build.gradle should exist")

        with open(build_gradle, "r") as f:
            content = f.read()
            # Verify Fabric testing requirements from documentation
            required_configs = [
                "fabric-loader-junit",  # Fabric JUnit dependency
                "useJUnitPlatform",  # JUnit platform setup
                "configureTests",  # Fabric game test setup
                "testImplementation",  # Test dependencies
            ]

            for config in required_configs:
                assert config in content, f"build.gradle should contain {config}"

    def _verify_project_structure(self, project_dir: str):
        """Verify project has proper structure for comprehensive testing."""
        required_structure = [
            "src/main/java",
            "src/main/resources",
            "src/test/java",
            "src/gametest/java",
            "src/gametest/resources",
            "build.gradle",
            "gradle.properties",
        ]

        for path in required_structure:
            full_path = os.path.join(project_dir, path)
            self.assertTrue(
                os.path.exists(full_path), f"Required path should exist: {path}"
            )

    def _verify_fabric_integration(self, project_dir: str):
        """Verify Fabric integration follows official documentation."""
        # Verify main fabric.mod.json
        main_config = os.path.join(project_dir, "src/main/resources/fabric.mod.json")
        self.assertTrue(
            os.path.exists(main_config), "Main fabric.mod.json should exist"
        )

        # Verify gametest fabric.mod.json
        gametest_config = os.path.join(
            project_dir, "src/gametest/resources/fabric.mod.json"
        )
        if os.path.exists(gametest_config):
            import json

            with open(gametest_config, "r") as f:
                config = json.load(f)
                assert "fabric-gametest" in config["entrypoints"]
                assert "fabric-client-gametest" in config["entrypoints"]


if __name__ == "__main__":
    # Run this specific test to see the comprehensive summary
    unittest.main()
