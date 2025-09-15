"""
Comprehensive integration tests for the entire fabricpy library.
"""

import unittest
import tempfile
import shutil
import os

import fabricpy
from fabricpy import ModConfig, Item, FoodItem, Block, ItemGroup, RecipeJson, ToolItem, item_group


class TestFabricPyIntegration(unittest.TestCase):
    """Integration tests for the entire fabricpy library."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = os.path.join(self.temp_dir, "integration_test_mod")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_mod_creation_workflow(self):
        """Test the complete workflow of creating a mod with all features."""
        # Step 1: Create ModConfig
        mod_config = ModConfig(
            mod_id="integration_test",
            name="Integration Test Mod",
            version="1.0.0",
            description="A complete integration test mod",
            authors=["Integration Tester", "Unit Test Bot"],
            project_dir=self.project_dir
        )
        
        # Step 2: Create custom item groups
        tools_group = ItemGroup(id="custom_tools", name="Custom Tools")
        materials_group = ItemGroup(id="rare_materials", name="Rare Materials")
        
        # Step 3: Create items with various configurations
        
        # Basic item with vanilla group
        basic_item = Item(
            id="integration_test:basic_item",
            name="Basic Integration Item",
            max_stack_size=64,
            item_group=item_group.INGREDIENTS
        )
        
        # Item with custom group and recipe
        advanced_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "ABA",
                "CDC",
                "ABA"
            ],
            "key": {
                "A": "minecraft:diamond",
                "B": "minecraft:netherite_ingot",
                "C": "minecraft:gold_ingot",
                "D": "minecraft:emerald"
            },
            "result": {
                "id": "integration_test:advanced_tool",
                "count": 1
            }
        })
        
        advanced_tool = ToolItem(
            id="integration_test:advanced_tool",
            name="Advanced Integration Tool",
            max_stack_size=1,
            recipe=advanced_recipe,
            item_group=tools_group,
            durability=500,
            mining_speed_multiplier=8.0,
            attack_damage=3.0,
            mining_level=2,
            enchantability=15,
            repair_ingredient="minecraft:diamond",
        )
        
        # Food item with complex properties
        super_food = FoodItem(
            id="integration_test:super_food",
            name="Super Integration Food",
            max_stack_size=16,
            nutrition=20,
            saturation=15.0,
            always_edible=True,
            item_group=item_group.FOOD_AND_DRINK
        )
        
        # Food item with recipe
        food_recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [
                {"item": "minecraft:golden_apple"},
                {"item": "minecraft:enchanted_golden_apple"},
                {"item": "minecraft:honey_bottle"},
                {"item": "integration_test:basic_item"}
            ],
            "result": {
                "id": "integration_test:super_food",
                "count": 2
            }
        })
        super_food.recipe = food_recipe
        
        # Rare material item
        rare_material = Item(
            id="integration_test:rare_crystal",
            name="Rare Crystal",
            max_stack_size=8,
            item_group=materials_group
        )
        
        # Step 4: Create blocks
        
        # Basic block
        basic_block = Block(
            id="integration_test:basic_block",
            name="Basic Integration Block",
            item_group=item_group.BUILDING_BLOCKS
        )
        
        # Block with recipe
        block_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "###",
                "###",
                "###"
            ],
            "key": {
                "#": "integration_test:rare_crystal"
            },
            "result": {
                "id": "integration_test:crystal_block",
                "count": 1
            }
        })
        
        crystal_block = Block(
            id="integration_test:crystal_block",
            name="Crystal Block",
            recipe=block_recipe,
            item_group=materials_group
        )
        
        # Step 5: Register all components
        mod_config.registerItem(basic_item)
        mod_config.registerItem(advanced_tool)
        mod_config.registerFoodItem(super_food)
        mod_config.registerItem(rare_material)
        mod_config.registerBlock(basic_block)
        mod_config.registerBlock(crystal_block)
        
        # Step 6: Verify registrations
        self.assertEqual(len(mod_config.registered_items), 4)
        self.assertEqual(len(mod_config.registered_blocks), 2)
        
        # Step 7: Verify custom groups detection
        custom_groups = mod_config._custom_groups
        self.assertEqual(len(custom_groups), 2)
        self.assertIn(tools_group, custom_groups)
        self.assertIn(materials_group, custom_groups)
        
        # Step 8: Test Java constant conversion
        self.assertEqual(
            mod_config._to_java_constant("integration_test:advanced_tool"),
            "INTEGRATION_TEST_ADVANCED_TOOL"
        )
        self.assertEqual(
            mod_config._to_java_constant("integration_test:crystal_block"),
            "INTEGRATION_TEST_CRYSTAL_BLOCK"
        )

    def test_recipe_system_integration(self):
        """Test the complete recipe system integration."""
        mod_config = ModConfig(
            mod_id="recipe_test",
            name="Recipe Test Mod",
            version="1.0.0",
            description="Testing recipe system",
            authors=["Recipe Tester"]
        )
        
        # Create items and blocks with various recipe types
        
        # Shaped recipe
        shaped_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["AB", "CD"],
            "key": {
                "A": "minecraft:iron_ingot",
                "B": "minecraft:gold_ingot",
                "C": "minecraft:diamond",
                "D": "minecraft:emerald"
            },
            "result": {"id": "recipe_test:precious_ingot", "count": 1}
        })
        
        precious_item = Item(
            id="recipe_test:precious_ingot",
            name="Precious Ingot",
            recipe=shaped_recipe
        )
        
        # Shapeless recipe
        shapeless_recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [
                {"item": "minecraft:apple"},
                {"item": "minecraft:honey_bottle"},
                {"item": "minecraft:sugar"}
            ],
            "result": {"id": "recipe_test:sweet_apple", "count": 1}
        })
        
        sweet_apple = FoodItem(
            id="recipe_test:sweet_apple",
            name="Sweet Apple",
            nutrition=6,
            saturation=4.0,
            recipe=shapeless_recipe
        )
        
        # Smelting recipe
        smelting_recipe = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": {"item": "recipe_test:precious_ingot"},
            "result": {"id": "recipe_test:refined_ingot", "count": 1},
            "experience": 2.0,
            "cookingtime": 400
        })
        
        refined_item = Item(
            id="recipe_test:refined_ingot",
            name="Refined Ingot",
            recipe=smelting_recipe
        )
        
        # Block with recipe
        block_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["###", "###", "###"],
            "key": {"#": "recipe_test:refined_ingot"},
            "result": {"id": "recipe_test:refined_block", "count": 1}
        })
        
        refined_block = Block(
            id="recipe_test:refined_block",
            name="Refined Block",
            recipe=block_recipe
        )
        
        # Register all
        mod_config.registerItem(precious_item)
        mod_config.registerFoodItem(sweet_apple)
        mod_config.registerItem(refined_item)
        mod_config.registerBlock(refined_block)
        
        # Verify recipe result IDs
        self.assertEqual(precious_item.recipe.result_id, "recipe_test:precious_ingot")
        self.assertEqual(sweet_apple.recipe.result_id, "recipe_test:sweet_apple")
        self.assertEqual(refined_item.recipe.result_id, "recipe_test:refined_ingot")
        self.assertEqual(refined_block.recipe.result_id, "recipe_test:refined_block")
        
        # Test that objects with recipes are properly identified
        items_with_recipes = [i for i in mod_config.registered_items if getattr(i, "recipe", None)]
        blocks_with_recipes = [b for b in mod_config.registered_blocks if getattr(b, "recipe", None)]
        
        self.assertEqual(len(items_with_recipes), 3)
        self.assertEqual(len(blocks_with_recipes), 1)

    def test_item_group_system_integration(self):
        """Test the complete item group system integration."""
        mod_config = ModConfig(
            mod_id="group_test",
            name="Group Test Mod",
            version="1.0.0",
            description="Testing item group system",
            authors=["Group Tester"]
        )
        
        # Create multiple custom groups
        weapons_group = ItemGroup(id="test_weapons", name="Test Weapons")
        armor_group = ItemGroup(id="test_armor", name="Test Armor")
        utilities_group = ItemGroup(id="test_utilities", name="Test Utilities")
        
        # Set icons for groups
        sword_icon = Item(id="group_test:icon_sword", name="Icon Sword")
        weapons_group.set_icon(sword_icon)
        
        helmet_icon = Item(id="group_test:icon_helmet", name="Icon Helmet")
        armor_group.set_icon(helmet_icon)
        
        # Create items for different groups
        
        # Weapons group
        sword = Item(id="group_test:sword", name="Test Sword", item_group=weapons_group)
        bow = Item(id="group_test:bow", name="Test Bow", item_group=weapons_group)
        axe = Item(id="group_test:axe", name="Test Axe", item_group=weapons_group)
        
        # Armor group
        helmet = Item(id="group_test:helmet", name="Test Helmet", item_group=armor_group)
        chestplate = Item(id="group_test:chestplate", name="Test Chestplate", item_group=armor_group)
        
        # Utilities group
        tool = Item(id="group_test:tool", name="Test Tool", item_group=utilities_group)
        
        # Vanilla groups
        vanilla_item1 = Item(id="group_test:ingredient", name="Ingredient", item_group=item_group.INGREDIENTS)
        vanilla_item2 = Item(id="group_test:food", name="Food", item_group=item_group.FOOD_AND_DRINK)
        
        # Blocks with custom groups
        weapon_block = Block(id="group_test:weapon_rack", name="Weapon Rack", item_group=weapons_group)
        utility_block = Block(id="group_test:utility_bench", name="Utility Bench", item_group=utilities_group)
        
        # Register all
        mod_config.registerItem(sword_icon)  # Icon items
        mod_config.registerItem(helmet_icon)
        mod_config.registerItem(sword)      # Group items
        mod_config.registerItem(bow)
        mod_config.registerItem(axe)
        mod_config.registerItem(helmet)
        mod_config.registerItem(chestplate)
        mod_config.registerItem(tool)
        mod_config.registerItem(vanilla_item1)  # Vanilla items
        mod_config.registerItem(vanilla_item2)
        mod_config.registerBlock(weapon_block)   # Blocks
        mod_config.registerBlock(utility_block)
        
        # Verify custom groups
        custom_groups = mod_config._custom_groups
        self.assertEqual(len(custom_groups), 3)
        self.assertIn(weapons_group, custom_groups)
        self.assertIn(armor_group, custom_groups)
        self.assertIn(utilities_group, custom_groups)
        
        # Verify group icons
        self.assertEqual(weapons_group.icon_item_id, "group_test:icon_sword")
        self.assertEqual(armor_group.icon_item_id, "group_test:icon_helmet")
        self.assertIsNone(utilities_group.icon_item_id)  # No icon set
        
        # Test group equality and hashing
        weapons_group_copy = ItemGroup(id="test_weapons", name="Different Name")
        self.assertEqual(weapons_group, weapons_group_copy)
        self.assertEqual(hash(weapons_group), hash(weapons_group_copy))

    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling throughout the system."""
        mod_config = ModConfig(
            mod_id="edge_test",
            name="Edge Case Test Mod",
            version="1.0.0",
            description="Testing edge cases",
            authors=["Edge Tester"]
        )
        
        # Test items with minimal configuration
        minimal_item = Item()
        self.assertIsNone(minimal_item.id)
        self.assertIsNone(minimal_item.name)
        self.assertEqual(minimal_item.max_stack_size, 64)
        
        # Test items with maximum values
        max_item = Item(
            id="edge_test:max_item",
            name="Maximum Item",
            max_stack_size=64
        )
        self.assertEqual(max_item.max_stack_size, 64)
        
        # Test food items with extreme values
        extreme_food = FoodItem(
            id="edge_test:extreme_food",
            name="Extreme Food",
            nutrition=20,  # Maximum reasonable nutrition
            saturation=20.0,  # High saturation
            always_edible=True
        )
        
        # Test blocks with texture fallback
        fallback_block = Block(
            id="edge_test:fallback_block",
            name="Fallback Block",
            block_texture_path="textures/blocks/test.png"
            # No inventory texture - should fall back
        )
        self.assertEqual(fallback_block.inventory_texture_path, "textures/blocks/test.png")
        
        # Test recipe with missing result ID
        incomplete_recipe = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": {"item": "minecraft:iron_ore"},
            "result": {"count": 1},  # No ID
            "experience": 0.7,
            "cookingtime": 200
        })
        self.assertIsNone(incomplete_recipe.result_id)
        
        # Test invalid recipe (missing type)
        with self.assertRaises(ValueError):
            RecipeJson({
                "pattern": ["#"],
                "key": {"#": "minecraft:stone"},
                "result": {"id": "test:item", "count": 1}
                # Missing "type"
            })
        
        # Register valid items
        mod_config.registerItem(max_item)
        mod_config.registerFoodItem(extreme_food)
        mod_config.registerBlock(fallback_block)
        
        # Test Java constant conversion edge cases
        self.assertEqual(mod_config._to_java_constant("123test"), "_123TEST")  # Starts with digit
        self.assertEqual(mod_config._to_java_constant("test-item.name"), "TEST_ITEM_NAME")  # Special chars
        self.assertEqual(mod_config._to_java_constant("ALREADY_UPPER"), "ALREADY_UPPER")  # Already uppercase

    def test_fabricpy_module_imports(self):
        """Test that all components can be imported from the main module."""
        # Test direct imports
        self.assertTrue(hasattr(fabricpy, 'ModConfig'))
        self.assertTrue(hasattr(fabricpy, 'Item'))
        self.assertTrue(hasattr(fabricpy, 'FoodItem'))
        self.assertTrue(hasattr(fabricpy, 'ToolItem'))
        self.assertTrue(hasattr(fabricpy, 'Block'))
        self.assertTrue(hasattr(fabricpy, 'ItemGroup'))
        self.assertTrue(hasattr(fabricpy, 'RecipeJson'))
        self.assertTrue(hasattr(fabricpy, 'item_group'))
        
        # Test that imports work
        mod_config = fabricpy.ModConfig(
            mod_id="import_test",
            name="Import Test",
            version="1.0.0",
            description="Test imports",
            authors=["Import Tester"]
        )
        
        item = fabricpy.Item(id="import_test:item", name="Import Item")
        food = fabricpy.FoodItem(id="import_test:food", name="Import Food", nutrition=1, saturation=0.1)
        block = fabricpy.Block(id="import_test:block", name="Import Block")
        fabricpy.ItemGroup(id="import_group", name="Import Group")
        fabricpy.RecipeJson({"type": "minecraft:crafting_shaped", "pattern": ["#"], "key": {"#": "minecraft:stone"}, "result": {"id": "import_test:item", "count": 1}})
        
        # Test vanilla group access
        self.assertEqual(fabricpy.item_group.TOOLS, "TOOLS")
        self.assertEqual(fabricpy.item_group.FOOD_AND_DRINK, "FOOD_AND_DRINK")
        
        # Register and verify
        mod_config.registerItem(item)
        mod_config.registerFoodItem(food)
        mod_config.registerBlock(block)
        
        self.assertEqual(len(mod_config.registered_items), 2)
        self.assertEqual(len(mod_config.registered_blocks), 1)


if __name__ == '__main__':
    # Run all integration tests
    unittest.main(verbosity=2)
