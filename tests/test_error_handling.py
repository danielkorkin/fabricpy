"""
Comprehensive error handling and edge case tests for fabricpy library.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock

import fabricpy
from fabricpy.item import Item
from fabricpy.fooditem import FoodItem
from fabricpy.block import Block
from fabricpy.itemgroup import ItemGroup
from fabricpy.recipejson import RecipeJson
from fabricpy.modconfig import ModConfig
from fabricpy import item_group


class TestItemErrorHandling(unittest.TestCase):
    """Test error handling for Item class."""

    def test_item_none_id_handling(self):
        """Test item creation with None ID."""
        item = Item(id=None, name="Test Item")
        self.assertIsNone(item.id)
        self.assertEqual(item.name, "Test Item")

    def test_item_none_name_handling(self):
        """Test item creation with None name."""
        item = Item(id="test:item", name=None)
        self.assertEqual(item.id, "test:item")
        self.assertIsNone(item.name)

    def test_item_empty_string_handling(self):
        """Test item creation with empty strings."""
        item = Item(id="", name="")
        self.assertEqual(item.id, "")
        self.assertEqual(item.name, "")

    def test_item_invalid_stack_size(self):
        """Test item with invalid stack sizes."""
        # Zero stack size
        item_zero = Item(id="test:zero", name="Zero Stack", max_stack_size=0)
        self.assertEqual(item_zero.max_stack_size, 0)
        
        # Negative stack size
        item_negative = Item(id="test:negative", name="Negative Stack", max_stack_size=-1)
        self.assertEqual(item_negative.max_stack_size, -1)
        
        # Very large stack size
        item_large = Item(id="test:large", name="Large Stack", max_stack_size=9999)
        self.assertEqual(item_large.max_stack_size, 9999)

    def test_item_unicode_handling(self):
        """Test item with unicode characters."""
        item = Item(
            id="test:unicode",
            name="测试物品 🎮 Тест",
            texture_path="textures/items/测试.png"
        )
        self.assertEqual(item.name, "测试物品 🎮 Тест")
        self.assertEqual(item.texture_path, "textures/items/测试.png")

    def test_item_special_characters(self):
        """Test item with special characters in various fields."""
        item = Item(
            id="test:special!@#$%^&*()",
            name="Special Item !@#$%^&*()",
            texture_path="textures/items/special!@#$%^&*().png"
        )
        self.assertEqual(item.id, "test:special!@#$%^&*()")
        self.assertEqual(item.name, "Special Item !@#$%^&*()")

    def test_item_with_invalid_recipe(self):
        """Test item with invalid recipe objects."""
        # None recipe (should work)
        item1 = Item(id="test:none_recipe", name="None Recipe", recipe=None)
        self.assertIsNone(item1.recipe)
        
        # String recipe (should work - might be valid JSON)
        item2 = Item(id="test:string_recipe", name="String Recipe", recipe="invalid json")
        self.assertEqual(item2.recipe, "invalid json")
        
        # Number recipe (should work - stored as-is)
        item3 = Item(id="test:number_recipe", name="Number Recipe", recipe=123)
        self.assertEqual(item3.recipe, 123)


class TestFoodItemErrorHandling(unittest.TestCase):
    """Test error handling for FoodItem class."""

    def test_food_item_invalid_nutrition(self):
        """Test food item with invalid nutrition values."""
        # Very negative nutrition
        food1 = FoodItem(id="test:negative", name="Negative Food", nutrition=-1000)
        self.assertEqual(food1.nutrition, -1000)
        
        # Very high nutrition
        food2 = FoodItem(id="test:high", name="High Food", nutrition=1000000)
        self.assertEqual(food2.nutrition, 1000000)

    def test_food_item_invalid_saturation(self):
        """Test food item with invalid saturation values."""
        # Very negative saturation
        food1 = FoodItem(id="test:neg_sat", name="Negative Saturation", saturation=-1000.0)
        self.assertEqual(food1.saturation, -1000.0)
        
        # Very high saturation
        food2 = FoodItem(id="test:high_sat", name="High Saturation", saturation=1000000.0)
        self.assertEqual(food2.saturation, 1000000.0)
        
        # NaN saturation (if somehow passed)
        food3 = FoodItem(id="test:nan_sat", name="NaN Saturation", saturation=float('inf'))
        self.assertEqual(food3.saturation, float('inf'))

    def test_food_item_non_boolean_always_edible(self):
        """Test food item with non-boolean always_edible values."""
        # Integer (truthy)
        food1 = FoodItem(id="test:int_edible", name="Int Edible", always_edible=1)
        self.assertEqual(food1.always_edible, 1)  # Should store as-is
        
        # String (truthy)
        food2 = FoodItem(id="test:str_edible", name="String Edible", always_edible="yes")
        self.assertEqual(food2.always_edible, "yes")
        
        # None (falsy)
        food3 = FoodItem(id="test:none_edible", name="None Edible", always_edible=None)
        self.assertIsNone(food3.always_edible)


class TestBlockErrorHandling(unittest.TestCase):
    """Test error handling for Block class."""

    def test_block_none_textures(self):
        """Test block with None textures."""
        block = Block(
            id="test:none_textures",
            name="None Textures",
            block_texture_path=None,
            inventory_texture_path=None
        )
        self.assertIsNone(block.block_texture_path)
        self.assertIsNone(block.inventory_texture_path)

    def test_block_empty_textures(self):
        """Test block with empty texture paths."""
        block = Block(
            id="test:empty_textures",
            name="Empty Textures",
            block_texture_path="",
            inventory_texture_path=""
        )
        self.assertEqual(block.block_texture_path, "")
        self.assertEqual(block.inventory_texture_path, "")

    def test_block_texture_fallback_edge_cases(self):
        """Test block texture fallback with edge cases."""
        # Only block texture provided
        block1 = Block(
            id="test:block_only",
            name="Block Only",
            block_texture_path="textures/blocks/test.png"
        )
        self.assertEqual(block1.inventory_texture_path, "textures/blocks/test.png")
        
        # Only inventory texture provided
        block2 = Block(
            id="test:inventory_only",
            name="Inventory Only",
            inventory_texture_path="textures/items/test.png"
        )
        self.assertIsNone(block2.block_texture_path)
        self.assertEqual(block2.inventory_texture_path, "textures/items/test.png")
        
        # Both None
        block3 = Block(
            id="test:both_none",
            name="Both None",
            block_texture_path=None,
            inventory_texture_path=None
        )
        self.assertIsNone(block3.block_texture_path)
        self.assertIsNone(block3.inventory_texture_path)


class TestRecipeErrorHandling(unittest.TestCase):
    """Test error handling for Recipe system."""

    def test_recipe_invalid_json_string(self):
        """Test recipe with invalid JSON string."""
        with self.assertRaises(json.JSONDecodeError):
            RecipeJson("invalid json string {")

    def test_recipe_empty_json(self):
        """Test recipe with empty JSON."""
        with self.assertRaises(ValueError):
            recipe = RecipeJson({})

    def test_recipe_missing_required_fields(self):
        """Test recipe missing required fields."""
        # Missing type
        with self.assertRaises(ValueError):
            recipe1 = RecipeJson({
                "pattern": ["#"],
                "key": {"#": "minecraft:stone"},
                "result": {"id": "test:item", "count": 1}
            })
        
        # Missing result - should not raise error, just have no result
        recipe2 = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#"],
            "key": {"#": "minecraft:stone"}
        })
        self.assertNotIn("result", recipe2.data)

    def test_recipe_malformed_patterns(self):
        """Test recipe with malformed patterns."""
        # Empty pattern
        recipe1 = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [],
            "key": {},
            "result": {"id": "test:empty", "count": 1}
        })
        self.assertEqual(recipe1.data["pattern"], [])
        
        # Pattern with inconsistent lengths
        recipe2 = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#", "##", "###"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "test:inconsistent", "count": 1}
        })
        self.assertEqual(len(recipe2.data["pattern"]), 3)

    def test_recipe_invalid_ingredients(self):
        """Test recipe with invalid ingredients."""
        # Empty ingredients
        recipe1 = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [],
            "result": {"id": "test:empty_ingredients", "count": 1}
        })
        self.assertEqual(recipe1.data["ingredients"], [])
        
        # Null ingredients
        recipe2 = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [None, "minecraft:stone"],
            "result": {"id": "test:null_ingredient", "count": 1}
        })
        self.assertIn(None, recipe2.data["ingredients"])

    def test_recipe_result_id_extraction_edge_cases(self):
        """Test result ID extraction with edge cases."""
        # No result field
        recipe1 = RecipeJson({"type": "minecraft:crafting_shaped"})
        self.assertIsNone(recipe1.get_result_id())
        
        # Result is None
        recipe2 = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "result": None
        })
        self.assertIsNone(recipe2.get_result_id())
        
        # Result is empty dict
        recipe3 = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "result": {}
        })
        self.assertIsNone(recipe3.get_result_id())
        
        # Result has no id field
        recipe4 = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "result": {"count": 1}
        })
        self.assertIsNone(recipe4.get_result_id())


class TestModConfigErrorHandling(unittest.TestCase):
    """Test error handling for ModConfig class."""

    def test_modconfig_none_values(self):
        """Test ModConfig with None values."""
        with self.assertRaises(TypeError):
            ModConfig(
                mod_id=None,
                name=None,
                version=None,
                description=None,
                authors=None
            )

    def test_modconfig_empty_values(self):
        """Test ModConfig with empty values."""
        mod = ModConfig(
            mod_id="",
            name="",
            version="",
            description="",
            authors=[]
        )
        self.assertEqual(mod.mod_id, "")
        self.assertEqual(mod.name, "")
        self.assertEqual(mod.version, "")
        self.assertEqual(mod.description, "")
        self.assertEqual(mod.authors, [])

    def test_modconfig_invalid_authors(self):
        """Test ModConfig with invalid author formats."""
        # Single string author - should fail due to missing required parameters
        with self.assertRaises(TypeError):
            mod1 = ModConfig(mod_id="test", name="Test", authors="Single Author")
        
        # Create a proper mod for testing author validation
        mod2 = ModConfig(
            mod_id="test", 
            name="Test", 
            description="Test mod",
            version="1.0.0",
            authors=["Valid Author"]
        )
        self.assertEqual(mod2.authors, ["Valid Author"])

    def test_modconfig_register_none_items(self):
        """Test registering None items/blocks."""
        mod = ModConfig(
            mod_id="test", 
            name="Test", 
            description="Test mod",
            version="1.0.0",
            authors=["TestDev"]
        )
        
        # Register None item (should handle gracefully)
        mod.registerItem(None)
        # Should not crash, but behavior depends on implementation
        
        # Register None block
        mod.registerBlock(None)
        # Should not crash, but behavior depends on implementation

    def test_modconfig_register_invalid_objects(self):
        """Test registering invalid objects as items/blocks."""
        mod = ModConfig(
            mod_id="test", 
            name="Test", 
            description="Test mod",
            version="1.0.0",
            authors=["TestDev"]
        )
        
        # Register string as item
        mod.registerItem("not an item")
        
        # Register dict as block
        mod.registerBlock({"not": "a block"})
        
        # Register number as item
        mod.registerItem(123)


class TestItemGroupErrorHandling(unittest.TestCase):
    """Test error handling for ItemGroup class."""

    def test_itemgroup_none_values(self):
        """Test ItemGroup with None values."""
        group = ItemGroup(id=None, name=None)
        self.assertIsNone(group.id)
        self.assertIsNone(group.name)

    def test_itemgroup_empty_values(self):
        """Test ItemGroup with empty values."""
        group = ItemGroup(id="", name="")
        self.assertEqual(group.id, "")
        self.assertEqual(group.name, "")

    def test_itemgroup_invalid_icon(self):
        """Test ItemGroup with invalid icon objects."""
        group = ItemGroup(id="test", name="Test")
        
        # Set invalid icon types
        group.set_icon("string_icon")
        group.set_icon(123)
        group.set_icon(None)
        
        # Should not crash, behavior depends on implementation

    def test_itemgroup_unicode_values(self):
        """Test ItemGroup with unicode values."""
        group = ItemGroup(
            id="test:unicode_测试",
            name="Unicode Group 测试 🎮"
        )
        self.assertEqual(group.id, "test:unicode_测试")
        self.assertEqual(group.name, "Unicode Group 测试 🎮")


class TestEdgeCasesAndBoundaries(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_very_long_strings(self):
        """Test with very long strings."""
        long_string = "A" * 10000
        
        item = Item(
            id=long_string,
            name=long_string,
            texture_path=long_string
        )
        self.assertEqual(len(item.id), 10000)
        self.assertEqual(len(item.name), 10000)
        self.assertEqual(len(item.texture_path), 10000)

    def test_extreme_numeric_values(self):
        """Test with extreme numeric values."""
        # Very large numbers
        large_num = 999999999999999999999
        food = FoodItem(
            id="test:extreme",
            name="Extreme Food",
            nutrition=large_num,
            saturation=float(large_num),
            max_stack_size=large_num
        )
        self.assertEqual(food.nutrition, large_num)
        self.assertEqual(food.saturation, float(large_num))
        self.assertEqual(food.max_stack_size, large_num)

    def test_circular_references(self):
        """Test objects that might create circular references."""
        group = ItemGroup(id="test", name="Test Group")
        
        # Create item with group
        item = Item(id="test:item", name="Test Item", item_group=group)
        
        # Set item as group icon (potential circular reference)
        group.set_icon(item)
        
        # Should not cause infinite loops
        self.assertEqual(item.item_group, group)

    def test_memory_intensive_operations(self):
        """Test operations that might be memory intensive."""
        # Create large recipe with many ingredients
        large_recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:stone"] * 100,  # 100 stone
            "result": {"id": "test:compressed_stone", "count": 1}
        })
        
        self.assertEqual(len(large_recipe.data["ingredients"]), 100)
        
        # Create item with large recipe
        item = Item(
            id="test:large_recipe",
            name="Large Recipe Item",
            recipe=large_recipe
        )
        self.assertEqual(item.recipe, large_recipe)

    def test_special_json_values(self):
        """Test JSON with special values."""
        # Recipe with special JSON values
        special_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#"],
            "key": {"#": "minecraft:stone"},
            "result": {
                "id": "test:special",
                "count": 1,
                "special_null": None,
                "special_bool": True,
                "special_array": [1, 2, 3],
                "special_nested": {"a": {"b": {"c": "deep"}}}
            }
        })
        
        result = special_recipe.data["result"]
        self.assertIsNone(result["special_null"])
        self.assertTrue(result["special_bool"])
        self.assertEqual(result["special_array"], [1, 2, 3])
        self.assertEqual(result["special_nested"]["a"]["b"]["c"], "deep")


if __name__ == '__main__':
    unittest.main()
