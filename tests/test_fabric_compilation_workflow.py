"""
Comprehensive Fabric Compilation and Testing Workflow Tests.

Tests that demonstrate the complete mod development and testing workflow
using Fabric's official testing framework as documented in the Fabric docs.
"""

import unittest
import tempfile
import os
import shutil
import json
from pathlib import Path

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

    def test_complete_fabric_testing_workflow(self):
        """Test the complete workflow from mod creation to testing."""
        print("\n🔨 Testing Complete Fabric Testing Workflow")
        
        # 1. Create a comprehensive mod with testing enabled
        mod = ModConfig(
            mod_id="fabric_workflow_test",
            name="Fabric Workflow Test Mod",
            version="1.0.0",
            description="Testing complete Fabric development workflow with automated testing.",
            authors=["fabricpy-dev"],
            project_dir=os.path.join(self.temp_dir, "fabric-workflow-test"),
            enable_testing=True,
            generate_unit_tests=True,
            generate_game_tests=True
        )

        # 2. Create diverse mod components to test
        self._create_test_components(mod)

        # 3. Compile the mod (which includes testing setup)
        mod.compile()

        # 4. Verify project structure was created correctly
        self._verify_project_structure(mod.project_dir)

        # 5. Verify Fabric testing integration was set up
        self._verify_fabric_testing_setup(mod.project_dir)

        # 6. Verify unit tests were generated
        self._verify_unit_tests_generated(mod.project_dir, mod)

        # 7. Verify game tests were generated
        self._verify_game_tests_generated(mod.project_dir, mod)

        # 8. Verify build.gradle has proper testing configuration
        self._verify_build_gradle_testing_config(mod.project_dir)

        print("✅ Complete Fabric testing workflow verified!")

    def _create_test_components(self, mod: ModConfig):
        """Create diverse mod components for comprehensive testing."""
        # Custom item group
        custom_group = ItemGroup(
            id="fabric_workflow_test:workflow_group",
            name="Workflow Test Group"
        )

        # Basic item
        basic_item = Item(
            id="fabric_workflow_test:workflow_item",
            name="Workflow Test Item",
            max_stack_size=64,
            item_group=custom_group,
            recipe=RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["#"],
                "key": {"#": "minecraft:iron_ingot"},
                "result": {"id": "fabric_workflow_test:workflow_item", "count": 1}
            })
        )

        # Food item with complex properties
        food_item = FoodItem(
            id="fabric_workflow_test:workflow_food",
            name="Workflow Test Food",
            nutrition=6,
            saturation=8.0,
            always_edible=True,
            max_stack_size=16,
            item_group=custom_group,
            recipe=RecipeJson({
                "type": "minecraft:crafting_shapeless",
                "ingredients": ["minecraft:apple", "minecraft:sugar", "fabric_workflow_test:workflow_item"],
                "result": {"id": "fabric_workflow_test:workflow_food", "count": 1}
            })
        )

        # Block with recipe dependency
        test_block = Block(
            id="fabric_workflow_test:workflow_block",
            name="Workflow Test Block",
            item_group=custom_group,
            recipe=RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["##", "##"],
                "key": {"#": "fabric_workflow_test:workflow_item"},
                "result": {"id": "fabric_workflow_test:workflow_block", "count": 1}
            })
        )

        # Register components
        mod.registerItem(basic_item)
        mod.registerItem(food_item)
        mod.registerBlock(test_block)

    def _verify_project_structure(self, project_dir: str):
        """Verify basic project structure was created."""
        expected_files = [
            "build.gradle",
            "gradle.properties",
            "settings.gradle",
            "src/main/resources/fabric.mod.json",
            "src/main/java",
            "src/main/resources/assets",
            "src/main/resources/data"
        ]

        for file_path in expected_files:
            full_path = os.path.join(project_dir, file_path)
            self.assertTrue(
                os.path.exists(full_path),
                f"Expected project file/directory should exist: {file_path}"
            )

    def _verify_fabric_testing_setup(self, project_dir: str):
        """Verify Fabric testing framework was set up according to official docs."""
        # Verify test directories exist
        test_dirs = [
            "src/test/java",
            "src/gametest/java",
            "src/gametest/resources"
        ]

        for test_dir in test_dirs:
            full_path = os.path.join(project_dir, test_dir)
            self.assertTrue(
                os.path.exists(full_path),
                f"Test directory should exist: {test_dir}"
            )

        # Verify gametest fabric.mod.json exists
        gametest_fabric_mod = os.path.join(project_dir, "src/gametest/resources/fabric.mod.json")
        self.assertTrue(os.path.exists(gametest_fabric_mod), "Gametest fabric.mod.json should exist")

        # Verify gametest fabric.mod.json content
        with open(gametest_fabric_mod, 'r') as f:
            gametest_config = json.load(f)
            self.assertIn("fabric-gametest", gametest_config["entrypoints"])
            self.assertIn("fabric-client-gametest", gametest_config["entrypoints"])

    def _verify_unit_tests_generated(self, project_dir: str, mod: ModConfig):
        """Verify unit tests were generated according to Fabric docs standards."""
        test_base_dir = os.path.join(project_dir, "src/test/java/com/example", 
                                    mod.mod_id.replace("-", "").replace("_", ""), "test")
        
        # Expected test files based on Fabric documentation patterns
        expected_test_files = [
            "ItemRegistrationTest.java",
            "RecipeValidationTest.java", 
            "ModIntegrationTest.java"
        ]

        for test_file in expected_test_files:
            test_path = os.path.join(test_base_dir, test_file)
            self.assertTrue(os.path.exists(test_path), f"Unit test should exist: {test_file}")

        # Verify test content follows Fabric patterns
        self._verify_unit_test_content(test_base_dir)

    def _verify_unit_test_content(self, test_dir: str):
        """Verify unit test content follows official Fabric testing patterns."""
        item_test_path = os.path.join(test_dir, "ItemRegistrationTest.java")
        
        if os.path.exists(item_test_path):
            with open(item_test_path, 'r') as f:
                content = f.read()
                
                # Verify follows Fabric docs patterns
                self.assertIn("@BeforeAll", content, "Should use @BeforeAll for setup")
                self.assertIn("SharedConstants.createGameVersion();", content, 
                            "Should initialize SharedConstants as per Fabric docs")
                self.assertIn("Bootstrap.initialize();", content,
                            "Should initialize Bootstrap as per Fabric docs")
                self.assertIn("Registries.ITEM.get", content,
                            "Should test item registry access")
                self.assertIn("@Test", content, "Should have test methods")
                self.assertIn("Assertions.", content, "Should use JUnit assertions")

    def _verify_game_tests_generated(self, project_dir: str, mod: ModConfig):
        """Verify game tests were generated according to Fabric docs."""
        gametest_dir = os.path.join(project_dir, "src/gametest/java/com/example",
                                   mod.mod_id.replace("-", "").replace("_", ""))
        
        # Expected gametest files
        expected_files = [
            f"{mod.mod_id.replace('-', '').replace('_', '').title()}ServerTest.java",
            f"{mod.mod_id.replace('-', '').replace('_', '').title()}ClientTest.java"
        ]

        for test_file in expected_files:
            test_path = os.path.join(gametest_dir, test_file)
            self.assertTrue(os.path.exists(test_path), f"Game test should exist: {test_file}")

        # Verify server test content
        self._verify_server_gametest_content(gametest_dir, mod)

    def _verify_server_gametest_content(self, gametest_dir: str, mod: ModConfig):
        """Verify server game test follows Fabric docs patterns."""
        server_test_file = f"{mod.mod_id.replace('-', '').replace('_', '').title()}ServerTest.java"
        server_test_path = os.path.join(gametest_dir, server_test_file)
        
        if os.path.exists(server_test_path):
            with open(server_test_path, 'r') as f:
                content = f.read()
                
                # Verify follows Fabric gametest patterns
                self.assertIn("FabricGameTest", content, "Should implement FabricGameTest")
                self.assertIn("@GameTest", content, "Should use @GameTest annotation")
                self.assertIn("TestContext", content, "Should use TestContext parameter")
                self.assertIn("EMPTY_STRUCTURE", content, "Should use EMPTY_STRUCTURE template")
                self.assertIn("context.complete()", content, "Should call context.complete()")

    def _verify_build_gradle_testing_config(self, project_dir: str):
        """Verify build.gradle has proper testing configuration per Fabric docs."""
        build_gradle_path = os.path.join(project_dir, "build.gradle")
        self.assertTrue(os.path.exists(build_gradle_path), "build.gradle should exist")

        with open(build_gradle_path, 'r') as f:
            content = f.read()

        # Verify Fabric testing dependencies as per docs
        expected_testing_config = [
            "fabric-loader-junit",  # Fabric Loader JUnit dependency
            "useJUnitPlatform",     # JUnit Platform configuration
            "testImplementation",   # Test dependencies block
            "configureTests"        # Fabric API game test configuration
        ]

        for config in expected_testing_config:
            self.assertIn(config, content, 
                         f"build.gradle should contain Fabric testing config: {config}")

    def test_fabric_testing_gradle_tasks(self):
        """Test that proper Gradle tasks are available for testing."""
        mod = ModConfig(
            mod_id="gradle_task_test",
            name="Gradle Task Test",
            version="1.0.0",
            description="Testing Gradle task generation.",
            authors=["fabricpy-test"],
            project_dir=os.path.join(self.temp_dir, "gradle-task-test"),
            enable_testing=True,
            generate_game_tests=True  # Explicitly enable game tests for this test
        )

        # Add simple components
        test_item = Item(
            id="gradle_task_test:test_item",
            name="Test Item"
        )
        mod.registerItem(test_item)
        mod.compile()

        # Verify build.gradle contains appropriate test tasks
        build_gradle_path = os.path.join(mod.project_dir, "build.gradle")
        with open(build_gradle_path, 'r') as f:
            content = f.read()

        # Should have unit test configuration
        self.assertIn("test {", content, "Should have test task configuration")
        
        # Should have game test configuration via Fabric API
        self.assertIn("fabricApi {", content, "Should have Fabric API configuration")
        self.assertIn("configureTests", content, "Should configure game tests")

    def test_comprehensive_testing_features(self):
        """Test all comprehensive testing features are properly integrated."""
        mod = ModConfig(
            mod_id="comprehensive_features_test",
            name="Comprehensive Features Test",
            version="1.0.0",
            description="Testing all comprehensive testing features.",
            authors=["fabricpy-comprehensive"],
            project_dir=os.path.join(self.temp_dir, "comprehensive-features-test"),
            enable_testing=True,
            generate_unit_tests=True,
            generate_game_tests=True
        )

        # Create components that test edge cases
        edge_case_item = FoodItem(
            id="comprehensive_features_test:edge_case_food",
            name="Edge Case Food",
            nutrition=0,  # Edge case: zero nutrition
            saturation=20.0,  # Edge case: high saturation
            always_edible=True,
            max_stack_size=1  # Edge case: non-stackable food
        )

        complex_recipe_item = Item(
            id="comprehensive_features_test:complex_item",
            name="Complex Recipe Item",
            recipe=RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["ABC", "DEF", "GHI"],
                "key": {
                    "A": "minecraft:diamond",
                    "B": "minecraft:emerald", 
                    "C": "minecraft:gold_ingot",
                    "D": "minecraft:iron_ingot",
                    "E": "minecraft:redstone",
                    "F": "minecraft:lapis_lazuli",
                    "G": "minecraft:coal",
                    "H": "minecraft:quartz",
                    "I": "minecraft:glowstone_dust"
                },
                "result": {"id": "comprehensive_features_test:complex_item", "count": 1}
            })
        )

        mod.registerItem(edge_case_item)
        mod.registerItem(complex_recipe_item)
        mod.compile()

        # Verify comprehensive testing was set up
        self.assertTrue(os.path.exists(mod.project_dir), "Project directory should exist")
        
        # Verify test files contain edge case handling
        test_dir = os.path.join(mod.project_dir, "src/test/java/com/example",
                               mod.mod_id.replace("-", "").replace("_", ""), "test")
        
        if os.path.exists(test_dir):
            # Check that tests were generated for our edge case components
            item_test_path = os.path.join(test_dir, "ItemRegistrationTest.java")
            if os.path.exists(item_test_path):
                with open(item_test_path, 'r') as f:
                    content = f.read()
                    # Should test our specific items
                    self.assertIn("edge_case_food", content, "Should test edge case food item")
                    self.assertIn("complex_item", content, "Should test complex recipe item")

    def test_fabric_testing_documentation_compliance(self):
        """Test that generated tests comply with official Fabric testing documentation."""
        mod = ModConfig(
            mod_id="docs_compliance_test",
            name="Docs Compliance Test",
            version="1.0.0",
            description="Testing compliance with Fabric testing documentation.",
            authors=["fabricpy-docs-test"],
            project_dir=os.path.join(self.temp_dir, "docs-compliance-test"),
            enable_testing=True,
            generate_unit_tests=True,
            generate_game_tests=True
        )

        # Add test item
        test_item = Item(
            id="docs_compliance_test:docs_item",
            name="Docs Test Item"
        )
        mod.registerItem(test_item)
        mod.compile()

        # Verify compliance with Fabric docs requirements
        self._verify_docs_compliance(mod.project_dir)

    def _verify_docs_compliance(self, project_dir: str):
        """Verify the generated code complies with official Fabric testing docs."""
        
        # 1. Verify unit test setup matches docs exactly
        test_files = Path(project_dir).rglob("*Test.java")
        unit_tests = [f for f in test_files if "/test/java/" in str(f)]
        
        for test_file in unit_tests:
            with open(test_file, 'r') as f:
                content = f.read()
                
                # Must have @BeforeAll with exact docs setup
                self.assertIn("@BeforeAll", content)
                self.assertIn("static void beforeAll()", content)
                self.assertIn("SharedConstants.createGameVersion();", content)
                self.assertIn("Bootstrap.initialize();", content)
                
                # Must use proper imports from docs
                self.assertIn("import net.minecraft.SharedConstants;", content)
                self.assertIn("import net.minecraft.Bootstrap;", content)
                self.assertIn("import org.junit.jupiter.api.BeforeAll;", content)
                self.assertIn("import org.junit.jupiter.api.Test;", content)

        # 2. Verify game test setup matches docs
        game_test_files = [f for f in test_files if "/gametest/java/" in str(f)]
        
        for test_file in game_test_files:
            with open(test_file, 'r') as f:
                content = f.read()
                
                if "ServerTest" in str(test_file):
                    # Server tests must implement FabricGameTest
                    self.assertIn("implements FabricGameTest", content)
                    self.assertIn("@GameTest(templateName = EMPTY_STRUCTURE", content)
                    self.assertIn("public void", content)
                    self.assertIn("TestContext context", content)
                    
                if "ClientTest" in str(test_file):
                    # Client tests must implement FabricClientGameTest  
                    self.assertIn("implements FabricClientGameTest", content)
                    self.assertIn("ClientGameTestContext", content)

        # 3. Verify build.gradle setup matches docs requirements
        build_gradle = os.path.join(project_dir, "build.gradle")
        with open(build_gradle, 'r') as f:
            gradle_content = f.read()
            
            # Must have fabric-loader-junit dependency
            self.assertIn("fabric-loader-junit", gradle_content)
            # Must use JUnit platform
            self.assertIn("useJUnitPlatform()", gradle_content)
            # Must have fabricApi test configuration
            self.assertIn("fabricApi", gradle_content)
            self.assertIn("configureTests", gradle_content)


if __name__ == '__main__':
    unittest.main()
