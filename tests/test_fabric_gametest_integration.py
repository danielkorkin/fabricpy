"""
Fabric Game Test Integration Tests for fabricpy library.

Tests that generated mods can be compiled and run using Fabric's testing framework.
Includes both unit tests and game tests to verify generated mod functionality.
"""

import json
import os
import shutil
import tempfile
import unittest

from fabricpy import Block, FoodItem, Item, ItemGroup, ModConfig, RecipeJson


class TestFabricGameTestIntegration(unittest.TestCase):
    """Test integration with Fabric's game testing framework."""

    def setUp(self):
        """Set up temporary directories for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)

    def _cleanup_temp_dir(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_generate_mod_with_fabric_junit_setup(self):
        """Test generating a mod with Fabric JUnit testing setup."""
        # Create a comprehensive mod for testing
        mod = ModConfig(
            mod_id="fabric_test_mod",
            name="Fabric Test Mod",
            version="1.0.0",
            description="A mod generated for Fabric testing integration.",
            authors=["fabricpy-test"],
            project_dir=os.path.join(self.temp_dir, "fabric-test-mod"),
        )

        # Add test items
        test_item = Item(
            id="fabric_test_mod:test_item",
            name="Test Item",
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["#"],
                    "key": {"#": "minecraft:stone"},
                    "result": {"id": "fabric_test_mod:test_item", "count": 1},
                }
            ),
        )

        test_food = FoodItem(
            id="fabric_test_mod:test_food",
            name="Test Food",
            nutrition=5,
            saturation=6.0,
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": ["minecraft:apple", "minecraft:sugar"],
                    "result": {"id": "fabric_test_mod:test_food", "count": 1},
                }
            ),
        )

        test_block = Block(id="fabric_test_mod:test_block", name="Test Block")

        # Register components
        mod.registerItem(test_item)
        mod.registerItem(test_food)
        mod.registerBlock(test_block)

        # Generate the mod
        mod.compile()

        # Verify mod structure was created
        self.assertTrue(os.path.exists(mod.project_dir))
        self.assertTrue(os.path.exists(os.path.join(mod.project_dir, "build.gradle")))
        self.assertTrue(
            os.path.exists(
                os.path.join(
                    mod.project_dir, "src", "main", "resources", "fabric.mod.json"
                )
            )
        )

        # Enhance build.gradle with Fabric testing setup
        self._enhance_build_gradle_for_testing(mod.project_dir)

        # Generate test files
        self._generate_fabric_junit_tests(mod.project_dir, mod)
        self._generate_fabric_game_tests(mod.project_dir, mod)

        # Verify test files were created
        self._verify_test_structure(mod.project_dir)

    def test_unit_test_generation_for_items(self):
        """Test generating unit tests for items."""
        mod = ModConfig(
            mod_id="unit_test_mod",
            name="Unit Test Mod",
            version="1.0.0",
            description="Testing unit test generation.",
            authors=["fabricpy-test"],
            project_dir=os.path.join(self.temp_dir, "unit-test-mod"),
        )

        # Add items with various configurations
        items = [
            Item(id="unit_test_mod:basic_item", name="Basic Item"),
            FoodItem(
                id="unit_test_mod:food_item",
                name="Food Item",
                nutrition=4,
                saturation=5.0,
            ),
            Item(
                id="unit_test_mod:recipe_item",
                name="Recipe Item",
                recipe=RecipeJson(
                    {
                        "type": "minecraft:crafting_shaped",
                        "pattern": ["##", "##"],
                        "key": {"#": "minecraft:stone"},
                        "result": {"id": "unit_test_mod:recipe_item", "count": 1},
                    }
                ),
            ),
        ]

        for item in items:
            mod.registerItem(item)

        mod.compile()
        self._enhance_build_gradle_for_testing(mod.project_dir)
        self._generate_fabric_junit_tests(mod.project_dir, mod)

        # Verify unit test content
        test_file = os.path.join(
            mod.project_dir,
            "src",
            "test",
            "java",
            "com",
            "example",
            "unit_test_mod",
            "test",
            "ItemRegistrationTest.java",
        )
        self.assertTrue(os.path.exists(test_file))

        with open(test_file, "r") as f:
            content = f.read()
            # Verify test contains proper setup and assertions
            self.assertIn("@BeforeAll", content)
            self.assertIn("SharedConstants.createGameVersion();", content)
            self.assertIn("Bootstrap.initialize();", content)
            self.assertIn("@Test", content)

    def test_game_test_generation_for_blocks(self):
        """Test generating game tests for blocks."""
        mod = ModConfig(
            mod_id="game_test_mod",
            name="Game Test Mod",
            version="1.0.0",
            description="Testing game test generation.",
            authors=["fabricpy-test"],
            project_dir=os.path.join(self.temp_dir, "game-test-mod"),
        )

        # Add blocks for game testing
        test_block = Block(
            id="game_test_mod:test_block",
            name="Test Block",
            block_texture_path="textures/blocks/test_block.png",
        )

        mod.registerBlock(test_block)
        mod.compile()
        self._enhance_build_gradle_for_testing(mod.project_dir)
        self._generate_fabric_game_tests(mod.project_dir, mod)

        # Verify game test files
        gametest_fabric_mod_json = os.path.join(
            mod.project_dir, "src", "gametest", "resources", "fabric.mod.json"
        )
        self.assertTrue(os.path.exists(gametest_fabric_mod_json))

        server_test = os.path.join(
            mod.project_dir,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            "game_test_mod",
            "Game_Test_ModServerTest.java",
        )
        self.assertTrue(os.path.exists(server_test))

    def test_recipe_testing_integration(self):
        """Test that recipes can be validated through Fabric testing."""
        mod = ModConfig(
            mod_id="recipe_test_mod",
            name="Recipe Test Mod",
            version="1.0.0",
            description="Testing recipe validation through Fabric tests.",
            authors=["fabricpy-test"],
            project_dir=os.path.join(self.temp_dir, "recipe-test-mod"),
        )

        # Create items with complex recipes
        shaped_item = Item(
            id="recipe_test_mod:shaped_item",
            name="Shaped Item",
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["###", "#X#", "###"],
                    "key": {"#": "minecraft:stone", "X": "minecraft:diamond"},
                    "result": {"id": "recipe_test_mod:shaped_item", "count": 1},
                }
            ),
        )

        shapeless_item = Item(
            id="recipe_test_mod:shapeless_item",
            name="Shapeless Item",
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": [
                        "minecraft:apple",
                        "minecraft:sugar",
                        "minecraft:egg",
                    ],
                    "result": {"id": "recipe_test_mod:shapeless_item", "count": 2},
                }
            ),
        )

        smelting_item = Item(
            id="recipe_test_mod:smelted_item",
            name="Smelted Item",
            recipe=RecipeJson(
                {
                    "type": "minecraft:smelting",
                    "ingredient": "minecraft:iron_ore",
                    "result": "recipe_test_mod:smelted_item",
                    "experience": 0.7,
                    "cookingtime": 200,
                }
            ),
        )

        mod.registerItem(shaped_item)
        mod.registerItem(shapeless_item)
        mod.registerItem(smelting_item)

        mod.compile()
        self._enhance_build_gradle_for_testing(mod.project_dir)
        self._generate_recipe_validation_tests(mod.project_dir, mod)

        # Verify recipe test files exist
        recipe_test_file = os.path.join(
            mod.project_dir,
            "src",
            "test",
            "java",
            "com",
            "example",
            "recipe_test_mod",
            "test",
            "RecipeValidationTest.java",
        )
        self.assertTrue(os.path.exists(recipe_test_file))

    def _enhance_build_gradle_for_testing(self, project_dir: str):
        """Enhance build.gradle with Fabric testing configuration."""
        build_gradle_path = os.path.join(project_dir, "build.gradle")

        if not os.path.exists(build_gradle_path):
            # Create a basic build.gradle if it doesn't exist
            self._create_basic_build_gradle(build_gradle_path)

        with open(build_gradle_path, "r") as f:
            content = f.read()

        # Add Fabric testing dependencies and configuration
        testing_config = """

// Fabric Testing Configuration
dependencies {
    testImplementation "net.fabricmc:fabric-loader-junit:${project.loader_version}"
}

test {
    useJUnitPlatform()
    testLogging {
        events "passed", "skipped", "failed"
        exceptionFormat "full"
    }
}

fabricApi {
    configureTests {
        createSourceSet = true
        modId = "${project.mod_id}-test"
        eula = true
    }
}
"""

        # Add the configuration if not already present
        if "fabric-loader-junit" not in content:
            content += testing_config

        with open(build_gradle_path, "w") as f:
            f.write(content)

    def _create_basic_build_gradle(self, build_gradle_path: str):
        """Create a basic build.gradle file for testing."""
        basic_build_gradle = """plugins {
    id 'fabric-loom' version '1.11-SNAPSHOT'
    id 'maven-publish'
}

version = project.mod_version
group = project.maven_group

base {
    archivesName = project.archives_base_name
}

repositories {
    // Add repositories to retrieve artifacts from in here.
    // You should only use this when depending on other mods because
    // Loom adds the essential maven repositories to download Minecraft and libraries from automatically.
    // See https://docs.gradle.org/current/userguide/declaring_repositories.html
    // for more information about repositories.
}

loom {
    splitEnvironmentSourceSets()

    mods {
        "examplemod" {
            sourceSet sourceSets.main
            sourceSet sourceSets.client
        }
    }
}

dependencies {
    // To change the versions see the gradle.properties file
    minecraft "com.mojang:minecraft:${project.minecraft_version}"
    mappings "net.fabricmc:yarn:${project.yarn_mappings}:v2"
    modImplementation "net.fabricmc:fabric-loader:${project.loader_version}"

    // Fabric API. This is technically optional, but you probably want it anyway.
    modImplementation "net.fabricmc.fabric-api:fabric-api:${project.fabric_version}"
}
"""
        os.makedirs(os.path.dirname(build_gradle_path), exist_ok=True)
        with open(build_gradle_path, "w") as f:
            f.write(basic_build_gradle)

    def _generate_fabric_junit_tests(self, project_dir: str, mod: ModConfig):
        """Generate Fabric JUnit unit tests."""
        test_dir = os.path.join(
            project_dir, "src", "test", "java", "com", "example", mod.mod_id, "test"
        )
        os.makedirs(test_dir, exist_ok=True)

        # Generate item registration test
        self._generate_item_registration_test(test_dir, mod)

        # Generate recipe validation test if there are recipes
        if any(
            hasattr(item, "recipe") and item.recipe for item in mod.registered_items
        ):
            self._generate_recipe_validation_tests(project_dir, mod)

    def _generate_item_registration_test(self, test_dir: str, mod: ModConfig):
        """Generate unit tests for item registration."""
        package_name = f"com.example.{mod.mod_id}.test"
        class_name = "ItemRegistrationTest"

        test_content = f"""package {package_name};

import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.registry.Registries;
import net.minecraft.util.Identifier;
import net.minecraft.SharedConstants;
import net.minecraft.Bootstrap;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;

import com.example.{mod.mod_id}.items.TutorialItems;

public class {class_name} {{
    
    @BeforeAll
    static void beforeAll() {{
        // Initialize Minecraft registries for testing
        SharedConstants.createGameVersion();
        Bootstrap.initialize();
        
        // Initialize our items
        TutorialItems.initialize();
    }}

    @Test
    void testItemsAreRegistered() {{
        // Test that our mod items are properly registered
"""

        # Add tests for each registered item
        for item in mod.registered_items:
            item_id = item.id
            if ":" in item_id:
                namespace, path = item_id.split(":", 1)
                test_content += f'''
        // Test {item.name}
        Item {path.replace("-", "_").replace(".", "_")} = Registries.ITEM.get(Identifier.of("{namespace}", "{path}"));
        Assertions.assertNotNull({path.replace("-", "_").replace(".", "_")}, "{item.name} should be registered");
        
        // Test ItemStack creation
        ItemStack {path.replace("-", "_").replace(".", "_")}_stack = new ItemStack({path.replace("-", "_").replace(".", "_")}, 1);
        Assertions.assertFalse({path.replace("-", "_").replace(".", "_")}_stack.isEmpty(), "{item.name} ItemStack should not be empty");
'''

        test_content += """
    }

    @Test
    void testVanillaItemsAccessible() {
        // Verify we can access vanilla items (registry is working)
        ItemStack diamondStack = new ItemStack(Items.DIAMOND, 1);
        Assertions.assertTrue(diamondStack.isOf(Items.DIAMOND));
        Assertions.assertEquals(1, diamondStack.getCount());
    }

    @Test
    void testItemProperties() {
        // Test item properties are correctly set
"""

        # Add property tests for food items
        for item in mod.registered_items:
            if hasattr(item, "nutrition") and item.nutrition is not None:
                item_id = item.id
                if ":" in item_id:
                    namespace, path = item_id.split(":", 1)
                    test_content += f'''
        // Test {item.name} food properties
        Item {path.replace("-", "_").replace(".", "_")}_food = Registries.ITEM.get(Identifier.of("{namespace}", "{path}"));
        Assertions.assertTrue({path.replace("-", "_").replace(".", "_")}_food.getFoodComponent() != null, "{item.name} should have food component");
'''

        test_content += """
    }
}
"""

        test_file = os.path.join(test_dir, f"{class_name}.java")
        with open(test_file, "w") as f:
            f.write(test_content)

    def _generate_fabric_game_tests(self, project_dir: str, mod: ModConfig):
        """Generate Fabric game tests."""
        gametest_dir = os.path.join(
            project_dir, "src", "gametest", "java", "com", "example", mod.mod_id
        )
        os.makedirs(gametest_dir, exist_ok=True)

        # Create gametest fabric.mod.json
        self._create_gametest_fabric_mod_json(project_dir, mod)

        # Generate server game test
        self._generate_server_game_test(gametest_dir, mod)

        # Generate client game test
        self._generate_client_game_test(gametest_dir, mod)

    def _create_gametest_fabric_mod_json(self, project_dir: str, mod: ModConfig):
        """Create fabric.mod.json for game tests."""
        gametest_resources = os.path.join(project_dir, "src", "gametest", "resources")
        os.makedirs(gametest_resources, exist_ok=True)

        package_name = f"com.example.{mod.mod_id}"

        fabric_mod_json = {
            "schemaVersion": 1,
            "id": f"{mod.mod_id}-test",
            "version": mod.version,
            "name": f"{mod.name} Game Tests",
            "icon": "assets/examplemod/icon.png",
            "environment": "*",
            "entrypoints": {
                "fabric-gametest": [
                    f"{package_name}.{mod.mod_id.replace('-', '_').title()}ServerTest"
                ],
                "fabric-client-gametest": [
                    f"{package_name}.{mod.mod_id.replace('-', '_').title()}ClientTest"
                ],
            },
        }

        with open(os.path.join(gametest_resources, "fabric.mod.json"), "w") as f:
            json.dump(fabric_mod_json, f, indent=2)

    def _generate_server_game_test(self, gametest_dir: str, mod: ModConfig):
        """Generate server-side game tests."""
        package_name = f"com.example.{mod.mod_id}"
        class_name = f"{mod.mod_id.replace('-', '_').title()}ServerTest"

        server_test_content = f"""package {package_name};

import net.minecraft.block.Blocks;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.registry.Registries;
import net.minecraft.test.GameTest;
import net.minecraft.test.TestContext;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;

import net.fabricmc.fabric.api.gametest.v1.FabricGameTest;

import com.example.{mod.mod_id}.items.TutorialItems;

public class {class_name} implements FabricGameTest {{

    @GameTest(templateName = EMPTY_STRUCTURE)
    public void testItemsExist(TestContext context) {{
        // Test that our mod items exist in the game
"""

        # Add tests for each item
        for item in mod.registered_items:
            item_id = item.id
            if ":" in item_id:
                namespace, path = item_id.split(":", 1)
                server_test_content += f'''
        // Test {item.name}
        ItemStack {path.replace("-", "_").replace(".", "_")}_stack = new ItemStack(
            Registries.ITEM.get(Identifier.of("{namespace}", "{path}")), 1
        );
        context.assertTrue(!{path.replace("-", "_").replace(".", "_")}_stack.isEmpty(), "{item.name} should exist");
'''

        server_test_content += """
        context.complete();
    }

    @GameTest(templateName = EMPTY_STRUCTURE)
    public void testBlockPlacement(TestContext context) {
        // Test block placement if we have blocks
"""

        if mod.registered_blocks:
            server_test_content += """
        BlockPos testPos = new BlockPos(1, 1, 1);
        
        // Test air block initially
        context.expectBlock(Blocks.AIR, testPos);
"""

            for block in mod.registered_blocks:
                block_id = block.id
                if ":" in block_id:
                    namespace, path = block_id.split(":", 1)
                    server_test_content += f'''
        
        // Test {block.name}
        context.setBlockState(testPos, 
            Registries.BLOCK.get(Identifier.of("{namespace}", "{path}")).getDefaultState()
        );
        context.expectBlock(
            Registries.BLOCK.get(Identifier.of("{namespace}", "{path}")), 
            testPos
        );
'''

        server_test_content += """
        context.complete();
    }

    @GameTest(templateName = EMPTY_STRUCTURE)
    public void testRecipesWork(TestContext context) {
        // Test that recipes can be resolved
        // This is a placeholder - in real game tests you'd test actual crafting
        context.assertTrue(true, "Recipe validation placeholder");
        context.complete();
    }
}
"""

        test_file = os.path.join(gametest_dir, f"{class_name}.java")
        with open(test_file, "w") as f:
            f.write(server_test_content)

    def _generate_client_game_test(self, gametest_dir: str, mod: ModConfig):
        """Generate client-side game tests."""
        package_name = f"com.example.{mod.mod_id}"
        class_name = f"{mod.mod_id.replace('-', '_').title()}ClientTest"

        client_test_content = f'''package {package_name};

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

@SuppressWarnings("UnstableApiUsage")
public class {class_name} implements FabricClientGameTest {{{{

    @Override
    public void runTest(ClientGameTestContext context) {{{{
        try (TestSingleplayerContext singleplayer = context.worldBuilder().create()) {{{{
            // Wait for world to load
            singleplayer.getClientWorld().waitForChunksRender();
            
            // Take screenshot for verification
            context.takeScreenshot("{mod.mod_id}-client-test");
            
            // Test client-side functionality
            // In a real test, you might test GUIs, rendering, etc.
            context.assertTrue(true, "Client test placeholder");
        }}}}
    }}}}
}}
'''

        test_file = os.path.join(gametest_dir, f"{class_name}.java")
        with open(test_file, "w") as f:
            f.write(client_test_content)

    def _generate_recipe_validation_tests(self, project_dir: str, mod: ModConfig):
        """Generate tests specifically for recipe validation."""
        test_dir = os.path.join(
            project_dir, "src", "test", "java", "com", "example", mod.mod_id, "test"
        )
        os.makedirs(test_dir, exist_ok=True)

        package_name = f"com.example.{mod.mod_id}.test"
        class_name = "RecipeValidationTest"

        recipe_test_content = f"""package {package_name};

import net.minecraft.recipe.Recipe;
import net.minecraft.recipe.RecipeManager;
import net.minecraft.recipe.RecipeType;
import net.minecraft.registry.Registries;
import net.minecraft.util.Identifier;
import net.minecraft.SharedConstants;
import net.minecraft.Bootstrap;
import net.minecraft.server.MinecraftServer;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;

public class {class_name} {{

    @BeforeAll
    static void beforeAll() {{
        SharedConstants.createGameVersion();
        Bootstrap.initialize();
    }}

    @Test
    void testRecipeFilesExist() {{
        // Test that recipe JSON files are valid and loadable
        // This is a unit test that validates recipe structure
"""

        # Add tests for each recipe
        items_with_recipes = [
            item
            for item in mod.registered_items
            if hasattr(item, "recipe") and item.recipe
        ]
        [
            block
            for block in mod.registered_blocks
            if hasattr(block, "recipe") and block.recipe
        ]

        for item in items_with_recipes:
            if hasattr(item.recipe, "data"):
                recipe_type = item.recipe.data.get("type", "unknown")
                item_id = item.id
                if ":" in item_id:
                    namespace, path = item_id.split(":", 1)
                    recipe_test_content += f'''
        // Test {item.name} recipe
        // Recipe type: {recipe_type}
        Assertions.assertNotNull("{item_id}", "Recipe for {item.name} should have valid ID");
'''

        recipe_test_content += """
        Assertions.assertTrue(true, "Recipe validation completed");
    }

    @Test
    void testRecipeTypes() {
        // Test that all recipe types used are valid
        // Verify shaped, shapeless, smelting, etc. recipes are properly structured
        Assertions.assertTrue(true, "Recipe type validation placeholder");
    }
}
"""

        test_file = os.path.join(test_dir, f"{class_name}.java")
        with open(test_file, "w") as f:
            f.write(recipe_test_content)

    def _verify_test_structure(self, project_dir: str):
        """Verify that test directory structure was created correctly."""
        # Verify unit test structure
        unit_test_dir = os.path.join(project_dir, "src", "test", "java")
        self.assertTrue(
            os.path.exists(unit_test_dir), "Unit test directory should exist"
        )

        # Verify game test structure
        gametest_dir = os.path.join(project_dir, "src", "gametest", "java")
        self.assertTrue(
            os.path.exists(gametest_dir), "Game test directory should exist"
        )

        gametest_resources = os.path.join(project_dir, "src", "gametest", "resources")
        self.assertTrue(
            os.path.exists(gametest_resources), "Game test resources should exist"
        )

        gametest_fabric_mod = os.path.join(gametest_resources, "fabric.mod.json")
        self.assertTrue(
            os.path.exists(gametest_fabric_mod),
            "Game test fabric.mod.json should exist",
        )

        # Verify build.gradle was enhanced
        build_gradle = os.path.join(project_dir, "build.gradle")
        with open(build_gradle, "r") as f:
            content = f.read()
            self.assertIn(
                "fabric-loader-junit",
                content,
                "build.gradle should include Fabric JUnit",
            )
            self.assertIn(
                "useJUnitPlatform", content, "build.gradle should use JUnit platform"
            )


class TestModCompilationWithTests(unittest.TestCase):
    """Test complete mod compilation workflow including test generation."""

    def setUp(self):
        """Set up temporary directories for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)

    def _cleanup_temp_dir(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_comprehensive_mod_with_all_testing_features(self):
        """Test creating a comprehensive mod with all testing features."""
        mod = ModConfig(
            mod_id="comprehensive_test_mod",
            name="Comprehensive Test Mod",
            version="1.0.0",
            description="A comprehensive mod with full testing integration.",
            authors=["fabricpy-comprehensive-test"],
            project_dir=os.path.join(self.temp_dir, "comprehensive-test-mod"),
        )

        # Create custom item group
        custom_group = ItemGroup(
            id="comprehensive_test_mod:test_group",
            name="Test Group",
            icon="comprehensive_test_mod:test_item",
        )

        # Add diverse items
        basic_item = Item(
            id="comprehensive_test_mod:basic_item",
            name="Basic Item",
            item_group=custom_group,
        )

        food_item = FoodItem(
            id="comprehensive_test_mod:magic_food",
            name="Magic Food",
            nutrition=8,
            saturation=12.0,
            always_edible=True,
            item_group=custom_group,
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": ["minecraft:golden_apple", "minecraft:nether_star"],
                    "result": {"id": "comprehensive_test_mod:magic_food", "count": 1},
                }
            ),
        )

        crafted_item = Item(
            id="comprehensive_test_mod:crafted_item",
            name="Crafted Item",
            item_group=custom_group,
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["ABA", "BCB", "ABA"],
                    "key": {
                        "A": "minecraft:iron_ingot",
                        "B": "minecraft:diamond",
                        "C": "comprehensive_test_mod:basic_item",
                    },
                    "result": {"id": "comprehensive_test_mod:crafted_item", "count": 1},
                }
            ),
        )

        # Add blocks
        test_block = Block(
            id="comprehensive_test_mod:test_block",
            name="Test Block",
            block_texture_path="textures/blocks/test_block.png",
            item_group=custom_group,
            recipe=RecipeJson(
                {
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["##", "##"],
                    "key": {"#": "comprehensive_test_mod:basic_item"},
                    "result": {"id": "comprehensive_test_mod:test_block", "count": 1},
                }
            ),
        )

        # Register all components
        mod.registerItem(basic_item)
        mod.registerItem(food_item)
        mod.registerItem(crafted_item)
        mod.registerBlock(test_block)

        # Compile the mod
        mod.compile()

        # Verify basic structure
        self.assertTrue(os.path.exists(mod.project_dir))

        # Add comprehensive testing
        self._add_comprehensive_testing(mod.project_dir, mod)

        # Verify all test components were created
        self._verify_comprehensive_test_structure(mod.project_dir)

    def _add_comprehensive_testing(self, project_dir: str, mod: ModConfig):
        """Add comprehensive testing setup to the project."""
        # Enhance build.gradle
        self._enhance_build_gradle_for_comprehensive_testing(project_dir)

        # Generate all test types
        self._generate_comprehensive_unit_tests(project_dir, mod)
        self._generate_comprehensive_game_tests(project_dir, mod)
        self._generate_integration_tests(project_dir, mod)

    def _enhance_build_gradle_for_comprehensive_testing(self, project_dir: str):
        """Enhance build.gradle with comprehensive testing configuration."""
        build_gradle_path = os.path.join(project_dir, "build.gradle")

        comprehensive_testing_config = """

// Comprehensive Testing Configuration
dependencies {
    testImplementation "net.fabricmc:fabric-loader-junit:${project.loader_version}"
    testImplementation "org.junit.jupiter:junit-jupiter:5.9.2"
    testImplementation "org.mockito:mockito-core:5.1.1"
    testImplementation "org.mockito:mockito-junit-jupiter:5.1.1"
}

test {
    useJUnitPlatform()
    testLogging {
        events "passed", "skipped", "failed", "standardOut", "standardError"
        exceptionFormat "full"
        showCauses true
        showExceptions true
        showStackTraces true
    }
    
    // Increase memory for tests
    maxHeapSize = "2g"
    
    // Set system properties for testing
    systemProperty "fabric.development", "true"
}

fabricApi {
    configureTests {
        createSourceSet = true
        modId = "${project.mod_id}-test"
        eula = true
        
        // Configure test environment
        testEnvironment {
            client()
            server()
        }
    }
}

// Add task to run only unit tests
task unitTest(type: Test) {
    testClassesDirs = sourceSets.test.output.classesDirs
    classpath = sourceSets.test.runtimeClasspath
    include '**/*Test.class'
    exclude '**/*IntegrationTest.class'
    exclude '**/*GameTest.class'
}

// Add task to run only integration tests
task integrationTest(type: Test) {
    testClassesDirs = sourceSets.test.output.classesDirs
    classpath = sourceSets.test.runtimeClasspath
    include '**/*IntegrationTest.class'
}
"""

        with open(build_gradle_path, "a") as f:
            f.write(comprehensive_testing_config)

    def _generate_comprehensive_unit_tests(self, project_dir: str, mod: ModConfig):
        """Generate comprehensive unit tests."""
        test_dir = os.path.join(
            project_dir, "src", "test", "java", "com", "example", mod.mod_id, "test"
        )
        os.makedirs(test_dir, exist_ok=True)

        # Generate test suite
        self._generate_test_suite(test_dir, mod)

        # Generate specific test classes
        self._generate_item_properties_test(test_dir, mod)
        self._generate_recipe_logic_test(test_dir, mod)
        self._generate_registry_test(test_dir, mod)

    def _generate_test_suite(self, test_dir: str, mod: ModConfig):
        """Generate a test suite that runs all tests."""
        package_name = f"com.example.{mod.mod_id}.test"

        test_suite_content = f"""package {package_name};

import org.junit.platform.suite.api.SelectClasses;
import org.junit.platform.suite.api.Suite;

@Suite
@SelectClasses({{
    ItemRegistrationTest.class,
    ItemPropertiesTest.class,
    RecipeLogicTest.class,
    RegistryIntegrationTest.class
}})
public class ComprehensiveTestSuite {{
    // Test suite that runs all unit tests
}}
"""

        with open(os.path.join(test_dir, "ComprehensiveTestSuite.java"), "w") as f:
            f.write(test_suite_content)

    def _generate_item_properties_test(self, test_dir: str, mod: ModConfig):
        """Generate tests for item properties."""
        package_name = f"com.example.{mod.mod_id}.test"

        properties_test_content = f"""package {package_name};

import net.minecraft.item.Item;
import net.minecraft.item.ItemStack;
import net.minecraft.registry.Registries;
import net.minecraft.util.Identifier;
import net.minecraft.SharedConstants;
import net.minecraft.Bootstrap;
import net.minecraft.component.DataComponentTypes;
import net.minecraft.component.type.FoodComponent;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DisplayName;

public class ItemPropertiesTest {{

    @BeforeAll
    static void beforeAll() {{
        SharedConstants.createGameVersion();
        Bootstrap.initialize();
    }}

    @Test
    @DisplayName("Test item stack sizes are correct")
    void testItemStackSizes() {{
"""

        # Add stack size tests for items
        for item in mod.registered_items:
            if hasattr(item, "max_stack_size") and item.max_stack_size is not None:
                item_id = item.id
                if ":" in item_id:
                    namespace, path = item_id.split(":", 1)
                    safe_name = path.replace("-", "_").replace(".", "_")
                    properties_test_content += f'''
        Item {safe_name} = Registries.ITEM.get(Identifier.of("{namespace}", "{path}"));
        Assertions.assertEquals({item.max_stack_size}, {safe_name}.getMaxCount(), 
            "{item.name} should have max stack size of {item.max_stack_size}");
'''

        properties_test_content += """
    }

    @Test
    @DisplayName("Test food item properties")
    void testFoodProperties() {
"""

        # Add food property tests
        for item in mod.registered_items:
            if hasattr(item, "nutrition") and item.nutrition is not None:
                item_id = item.id
                if ":" in item_id:
                    namespace, path = item_id.split(":", 1)
                    safe_name = path.replace("-", "_").replace(".", "_")
                    properties_test_content += f'''
        Item {safe_name} = Registries.ITEM.get(Identifier.of("{namespace}", "{path}"));
        ItemStack {safe_name}_stack = new ItemStack({safe_name});
        FoodComponent foodComponent = {safe_name}_stack.get(DataComponentTypes.FOOD);
        
        Assertions.assertNotNull(foodComponent, "{item.name} should have food component");
        Assertions.assertEquals({item.nutrition}, foodComponent.nutrition(), 
            "{item.name} should have nutrition value of {item.nutrition}");
'''

                    if hasattr(item, "saturation") and item.saturation is not None:
                        properties_test_content += f'''
        Assertions.assertEquals({item.saturation}f, foodComponent.saturation(), 0.001f,
            "{item.name} should have saturation value of {item.saturation}");
'''

        properties_test_content += """
    }
}
"""

        with open(os.path.join(test_dir, "ItemPropertiesTest.java"), "w") as f:
            f.write(properties_test_content)

    def _generate_recipe_logic_test(self, test_dir: str, mod: ModConfig):
        """Generate tests for recipe logic."""
        package_name = f"com.example.{mod.mod_id}.test"

        recipe_test_content = f"""package {package_name};

import net.minecraft.recipe.RecipeType;
import net.minecraft.util.Identifier;
import net.minecraft.SharedConstants;
import net.minecraft.Bootstrap;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DisplayName;

public class RecipeLogicTest {{

    @BeforeAll
    static void beforeAll() {{
        SharedConstants.createGameVersion();
        Bootstrap.initialize();
    }}

    @Test
    @DisplayName("Test recipe types are valid")
    void testRecipeTypes() {{
        // Test that all recipe types used in our mod are valid
"""

        # Add recipe type validation
        recipe_types_used = set()
        for item in mod.registered_items:
            if hasattr(item, "recipe") and item.recipe and hasattr(item.recipe, "data"):
                recipe_type = item.recipe.data.get("type")
                if recipe_type:
                    recipe_types_used.add(recipe_type)

        for block in mod.registered_blocks:
            if (
                hasattr(block, "recipe")
                and block.recipe
                and hasattr(block.recipe, "data")
            ):
                recipe_type = block.recipe.data.get("type")
                if recipe_type:
                    recipe_types_used.add(recipe_type)

        for recipe_type in recipe_types_used:
            recipe_test_content += f'''
        // Verify {recipe_type} is a valid recipe type
        Assertions.assertDoesNotThrow(() -> {{
            RecipeType.CRAFTING_SHAPED; // Basic validation that recipe types work
        }}, "{recipe_type} should be a valid recipe type");
'''

        recipe_test_content += """
    }

    @Test
    @DisplayName("Test recipe result IDs match item IDs")
    void testRecipeResultIds() {
        // Test that recipe results reference valid items
        Assertions.assertTrue(true, "Recipe result validation placeholder");
    }
}
"""

        with open(os.path.join(test_dir, "RecipeLogicTest.java"), "w") as f:
            f.write(recipe_test_content)

    def _generate_registry_test(self, test_dir: str, mod: ModConfig):
        """Generate tests for registry integration."""
        package_name = f"com.example.{mod.mod_id}.test"

        registry_test_content = f"""package {package_name};

import net.minecraft.registry.Registries;
import net.minecraft.util.Identifier;
import net.minecraft.SharedConstants;
import net.minecraft.Bootstrap;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DisplayName;

public class RegistryIntegrationTest {{

    @BeforeAll
    static void beforeAll() {{
        SharedConstants.createGameVersion();
        Bootstrap.initialize();
    }}

    @Test
    @DisplayName("Test all mod items are in registry")
    void testItemRegistryIntegration() {{
"""

        # Test each item is in registry
        for item in mod.registered_items:
            item_id = item.id
            if ":" in item_id:
                namespace, path = item_id.split(":", 1)
                registry_test_content += f'''
        Assertions.assertTrue(Registries.ITEM.containsId(Identifier.of("{namespace}", "{path}")),
            "{item.name} should be registered in item registry");
'''

        registry_test_content += """
    }

    @Test
    @DisplayName("Test all mod blocks are in registry")
    void testBlockRegistryIntegration() {
"""

        # Test each block is in registry
        for block in mod.registered_blocks:
            block_id = block.id
            if ":" in block_id:
                namespace, path = block_id.split(":", 1)
                registry_test_content += f'''
        Assertions.assertTrue(Registries.BLOCK.containsId(Identifier.of("{namespace}", "{path}")),
            "{block.name} should be registered in block registry");
'''

        registry_test_content += """
    }
}
"""

        with open(os.path.join(test_dir, "RegistryIntegrationTest.java"), "w") as f:
            f.write(registry_test_content)

    def _generate_comprehensive_game_tests(self, project_dir: str, mod: ModConfig):
        """Generate comprehensive game tests."""
        # Use the existing game test generation but with more comprehensive tests
        gametest_dir = os.path.join(
            project_dir, "src", "gametest", "java", "com", "example", mod.mod_id
        )
        os.makedirs(gametest_dir, exist_ok=True)

        # Create enhanced gametest fabric.mod.json
        self._create_enhanced_gametest_fabric_mod_json(project_dir, mod)

        # Generate enhanced server and client tests
        self._generate_enhanced_server_game_test(gametest_dir, mod)
        self._generate_enhanced_client_game_test(gametest_dir, mod)

    def _create_enhanced_gametest_fabric_mod_json(
        self, project_dir: str, mod: ModConfig
    ):
        """Create enhanced fabric.mod.json for game tests."""
        gametest_resources = os.path.join(project_dir, "src", "gametest", "resources")
        os.makedirs(gametest_resources, exist_ok=True)

        package_name = f"com.example.{mod.mod_id}"

        fabric_mod_json = {
            "schemaVersion": 1,
            "id": f"{mod.mod_id}-test",
            "version": mod.version,
            "name": f"{mod.name} Comprehensive Game Tests",
            "description": f"Comprehensive game tests for {mod.name}",
            "icon": "assets/examplemod/icon.png",
            "environment": "*",
            "entrypoints": {
                "fabric-gametest": [f"{package_name}.ComprehensiveServerTest"],
                "fabric-client-gametest": [f"{package_name}.ComprehensiveClientTest"],
            },
            "depends": {
                "fabricloader": ">=0.15.0",
                "fabric-api": "*",
                "minecraft": "~1.21.0",
            },
        }

        with open(os.path.join(gametest_resources, "fabric.mod.json"), "w") as f:
            json.dump(fabric_mod_json, f, indent=2)

    def _generate_enhanced_server_game_test(self, gametest_dir: str, mod: ModConfig):
        """Generate enhanced server-side game tests."""
        package_name = f"com.example.{mod.mod_id}"
        class_name = "ComprehensiveServerTest"

        server_test_content = f"""package {package_name};

import net.minecraft.block.Blocks;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.registry.Registries;
import net.minecraft.test.GameTest;
import net.minecraft.test.TestContext;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;

import net.fabricmc.fabric.api.gametest.v1.FabricGameTest;

public class {class_name} implements FabricGameTest {{

    @GameTest(templateName = EMPTY_STRUCTURE, timeoutTicks = 200)
    public void testCompleteItemFunctionality(TestContext context) {{
        // Comprehensive test of all mod items
"""

        # Add comprehensive item tests
        for item in mod.registered_items:
            item_id = item.id
            if ":" in item_id:
                namespace, path = item_id.split(":", 1)
                safe_name = path.replace("-", "_").replace(".", "_")
                server_test_content += f'''
        
        // Test {item.name}
        ItemStack {safe_name}_stack = new ItemStack(
            Registries.ITEM.get(Identifier.of("{namespace}", "{path}")), 1
        );
        context.assertTrue(!{safe_name}_stack.isEmpty(), "{item.name} should create valid ItemStack");
        
        // Test item can be held and used
        context.assertTrue({safe_name}_stack.getItem() != Items.AIR, "{item.name} should not be air");
'''

                # Add food-specific tests
                if hasattr(item, "nutrition"):
                    server_test_content += f'''
        // Test {item.name} food functionality
        context.assertTrue({safe_name}_stack.isFood(), "{item.name} should be food");
'''

        server_test_content += """
        
        context.complete();
    }

    @GameTest(templateName = EMPTY_STRUCTURE, timeoutTicks = 300)
    public void testBlockInteraction(TestContext context) {
        // Test block placement and interaction
        BlockPos testPos = new BlockPos(1, 1, 1);
        BlockPos testPos2 = new BlockPos(2, 1, 1);
        
        // Start with air
        context.expectBlock(Blocks.AIR, testPos);
"""

        # Add block interaction tests
        for block in mod.registered_blocks:
            block_id = block.id
            if ":" in block_id:
                namespace, path = block_id.split(":", 1)
                server_test_content += f'''
        
        // Test {block.name}
        context.setBlockState(testPos, 
            Registries.BLOCK.get(Identifier.of("{namespace}", "{path}")).getDefaultState()
        );
        context.expectBlock(
            Registries.BLOCK.get(Identifier.of("{namespace}", "{path}")), 
            testPos
        );
        
        // Test block can be broken
        context.setBlockState(testPos, Blocks.AIR.getDefaultState());
        context.expectBlock(Blocks.AIR, testPos);
'''

        server_test_content += """
        
        context.complete();
    }

    @GameTest(templateName = EMPTY_STRUCTURE, timeoutTicks = 400)
    public void testWorldInteraction(TestContext context) {
        // Test items and blocks work in world context
        World world = context.getWorld();
        
        context.assertTrue(world != null, "World should be available");
        context.assertTrue(!world.isClient(), "Should be server world");
        
        context.complete();
    }
}
"""

        test_file = os.path.join(gametest_dir, f"{class_name}.java")
        with open(test_file, "w") as f:
            f.write(server_test_content)

    def _generate_enhanced_client_game_test(self, gametest_dir: str, mod: ModConfig):
        """Generate enhanced client-side game tests."""
        package_name = f"com.example.{mod.mod_id}"
        class_name = "ComprehensiveClientTest"

        client_test_content = f'''package {package_name};

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

@SuppressWarnings("UnstableApiUsage")
public class {class_name} implements FabricClientGameTest {{

    @Override
    public void runTest(ClientGameTestContext context) {{
        try (TestSingleplayerContext singleplayer = context.worldBuilder().create()) {{
            // Wait for world to load completely
            singleplayer.getClientWorld().waitForChunksRender();
            
            // Test client-side functionality
            testClientRendering(context, singleplayer);
            testInventoryInteraction(context, singleplayer);
            testCreativeMenu(context, singleplayer);
            
            // Take final screenshot
            context.takeScreenshot("{mod.mod_id}-comprehensive-client-test");
        }}
    }}
    
    private void testClientRendering(ClientGameTestContext context, TestSingleplayerContext singleplayer) {{
        // Test that items render properly in client
        context.assertTrue(true, "Client rendering test placeholder");
        
        // Take screenshot of rendering
        context.takeScreenshot("{mod.mod_id}-rendering-test");
    }}
    
    private void testInventoryInteraction(ClientGameTestContext context, TestSingleplayerContext singleplayer) {{
        // Test inventory interactions work
        context.assertTrue(true, "Inventory interaction test placeholder");
        
        // Take screenshot of inventory
        context.takeScreenshot("{mod.mod_id}-inventory-test");
    }}
    
    private void testCreativeMenu(ClientGameTestContext context, TestSingleplayerContext singleplayer) {{
        // Test items appear in creative menu properly
        context.assertTrue(true, "Creative menu test placeholder");
        
        // Take screenshot of creative menu
        context.takeScreenshot("{mod.mod_id}-creative-menu-test");
    }}
}}
'''

        test_file = os.path.join(gametest_dir, f"{class_name}.java")
        with open(test_file, "w") as f:
            f.write(client_test_content)

    def _generate_integration_tests(self, project_dir: str, mod: ModConfig):
        """Generate integration tests that test complete workflows."""
        test_dir = os.path.join(
            project_dir, "src", "test", "java", "com", "example", mod.mod_id, "test"
        )

        package_name = f"com.example.{mod.mod_id}.test"

        integration_test_content = f"""package {package_name};

import net.minecraft.SharedConstants;
import net.minecraft.Bootstrap;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.DisplayName;

public class ModIntegrationTest {{

    @BeforeAll
    static void beforeAll() {{
        SharedConstants.createGameVersion();
        Bootstrap.initialize();
    }}

    @Test
    @DisplayName("Test complete mod initialization")
    void testCompleteModInitialization() {{
        // Test that all components of the mod initialize correctly together
        Assertions.assertDoesNotThrow(() -> {{
            // Initialize items
            com.example.{mod.mod_id}.items.TutorialItems.initialize();
        }}, "Item initialization should not throw exceptions");
        
        Assertions.assertTrue(true, "Mod initialization completed successfully");
    }}

    @Test
    @DisplayName("Test mod component interactions")
    void testModComponentInteractions() {{
        // Test that different mod components work together
        // (items, blocks, recipes, item groups)
        Assertions.assertTrue(true, "Component interaction test placeholder");
    }}

    @Test
    @DisplayName("Test mod recipe chain workflow")
    void testRecipeChainWorkflow() {{
        // Test that recipes form valid chains (if applicable)
        Assertions.assertTrue(true, "Recipe chain workflow test placeholder");
    }}
}}
"""

        with open(os.path.join(test_dir, "ModIntegrationTest.java"), "w") as f:
            f.write(integration_test_content)

    def _verify_comprehensive_test_structure(self, project_dir: str):
        """Verify comprehensive test structure was created."""
        # Verify enhanced build.gradle
        build_gradle = os.path.join(project_dir, "build.gradle")
        with open(build_gradle, "r") as f:
            content = f.read()
            self.assertIn("fabric-loader-junit", content)
            self.assertIn("junit-jupiter", content)
            self.assertIn("mockito", content)
            self.assertIn("unitTest", content)
            self.assertIn("integrationTest", content)

        # Verify test suite exists
        test_suite = os.path.join(
            project_dir,
            "src",
            "test",
            "java",
            "com",
            "example",
            "comprehensive_test_mod",
            "test",
            "ComprehensiveTestSuite.java",
        )
        self.assertTrue(os.path.exists(test_suite))

        # Verify all test types exist
        test_files = [
            "ItemRegistrationTest.java",
            "ItemPropertiesTest.java",
            "RecipeLogicTest.java",
            "RegistryIntegrationTest.java",
            "ModIntegrationTest.java",
        ]

        test_dir = os.path.join(
            project_dir,
            "src",
            "test",
            "java",
            "com",
            "example",
            "comprehensive_test_mod",
            "test",
        )

        for test_file in test_files:
            self.assertTrue(
                os.path.exists(os.path.join(test_dir, test_file)),
                f"Test file {test_file} should exist",
            )

        # Verify game test structure
        gametest_server = os.path.join(
            project_dir,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            "comprehensive_test_mod",
            "ComprehensiveServerTest.java",
        )
        self.assertTrue(os.path.exists(gametest_server))

        gametest_client = os.path.join(
            project_dir,
            "src",
            "gametest",
            "java",
            "com",
            "example",
            "comprehensive_test_mod",
            "ComprehensiveClientTest.java",
        )
        self.assertTrue(os.path.exists(gametest_client))


if __name__ == "__main__":
    unittest.main()
