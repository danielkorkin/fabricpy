"""
Unit tests for the Item class and its components.
"""

import unittest

import fabricpy
from fabricpy.item import Item
from fabricpy.fooditem import FoodItem
from fabricpy.recipejson import RecipeJson
from fabricpy import item_group


class TestItem(unittest.TestCase):
    """Test the Item class."""

    def test_item_creation_basic(self):
        """Test creating a basic item with minimal parameters."""
        item = Item(
            id="testmod:basic_item",
            name="Basic Test Item"
        )
        
        self.assertEqual(item.id, "testmod:basic_item")
        self.assertEqual(item.name, "Basic Test Item")
        self.assertEqual(item.max_stack_size, 64)  # default
        self.assertIsNone(item.texture_path)  # default
        self.assertIsNone(item.recipe)  # default
        self.assertIsNone(item.item_group)  # default

    def test_item_creation_full_parameters(self):
        """Test creating an item with all parameters."""
        recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "testmod:test_item", "count": 1}
        })
        
        item = Item(
            id="testmod:test_item",
            name="Test Item",
            max_stack_size=16,
            texture_path="textures/items/test_item.png",
            recipe=recipe,
            item_group=item_group.TOOLS
        )
        
        self.assertEqual(item.id, "testmod:test_item")
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.max_stack_size, 16)
        self.assertEqual(item.texture_path, "textures/items/test_item.png")
        self.assertEqual(item.recipe, recipe)
        self.assertEqual(item.item_group, item_group.TOOLS)

    def test_item_namespaced_id(self):
        """Test items with different namespace formats."""
        # With namespace
        item1 = Item(id="mymod:example_item", name="Example Item")
        self.assertEqual(item1.id, "mymod:example_item")
        
        # Without namespace (should still work)
        item2 = Item(id="example_item", name="Example Item")
        self.assertEqual(item2.id, "example_item")

    def test_item_with_custom_item_group(self):
        """Test item with custom ItemGroup."""
        custom_group = fabricpy.ItemGroup(id="test_group", name="Test Group")
        
        item = Item(
            id="testmod:grouped_item",
            name="Grouped Item",
            item_group=custom_group
        )
        
        self.assertEqual(item.item_group, custom_group)

    def test_item_edge_cases(self):
        """Test edge cases for item creation."""
        # Very long names
        long_name = "A" * 100
        item = Item(id="testmod:long_name", name=long_name)
        self.assertEqual(item.name, long_name)
        
        # Max stack size boundaries
        item_min = Item(id="testmod:min_stack", name="Min Stack", max_stack_size=1)
        self.assertEqual(item_min.max_stack_size, 1)
        
        item_max = Item(id="testmod:max_stack", name="Max Stack", max_stack_size=64)
        self.assertEqual(item_max.max_stack_size, 64)


class TestFoodItem(unittest.TestCase):
    """Test the FoodItem class."""

    def test_food_item_creation_basic(self):
        """Test creating a basic food item."""
        food_item = FoodItem(
            id="testmod:basic_food",
            name="Basic Food",
            nutrition=4,
            saturation=0.3
        )
        
        self.assertEqual(food_item.id, "testmod:basic_food")
        self.assertEqual(food_item.name, "Basic Food")
        self.assertEqual(food_item.nutrition, 4)
        self.assertEqual(food_item.saturation, 0.3)
        self.assertFalse(food_item.always_edible)  # default

    def test_food_item_inheritance(self):
        """Test that FoodItem properly inherits from Item."""
        food_item = FoodItem(
            id="testmod:food_with_recipe",
            name="Food with Recipe",
            max_stack_size=16,
            texture_path="textures/items/food.png",
            nutrition=6,
            saturation=0.6,
            item_group=item_group.FOOD_AND_DRINK
        )
        
        # Test Item properties
        self.assertEqual(food_item.max_stack_size, 16)
        self.assertEqual(food_item.texture_path, "textures/items/food.png")
        self.assertEqual(food_item.item_group, item_group.FOOD_AND_DRINK)
        
        # Test FoodItem specific properties
        self.assertEqual(food_item.nutrition, 6)
        self.assertEqual(food_item.saturation, 0.6)

    def test_food_item_always_edible(self):
        """Test food item that can always be eaten."""
        golden_apple = FoodItem(
            id="testmod:golden_apple",
            name="Golden Apple",
            nutrition=4,
            saturation=9.6,
            always_edible=True
        )
        
        self.assertTrue(golden_apple.always_edible)

    def test_food_item_nutrition_values(self):
        """Test various nutrition and saturation values."""
        # Low nutrition food
        low_food = FoodItem(
            id="testmod:berry",
            name="Berry",
            nutrition=1,
            saturation=0.1
        )
        self.assertEqual(low_food.nutrition, 1)
        self.assertEqual(low_food.saturation, 0.1)
        
        # High nutrition food
        high_food = FoodItem(
            id="testmod:feast",
            name="Feast",
            nutrition=20,
            saturation=12.0
        )
        self.assertEqual(high_food.nutrition, 20)
        self.assertEqual(high_food.saturation, 12.0)

    def test_food_item_with_recipe(self):
        """Test food item with a crafting recipe."""
        recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [
                {"item": "minecraft:wheat"},
                {"item": "minecraft:sugar"}
            ],
            "result": {"id": "testmod:bread", "count": 1}
        })
        
        bread = FoodItem(
            id="testmod:bread",
            name="Custom Bread",
            nutrition=5,
            saturation=6.0,
            recipe=recipe
        )
        
        self.assertEqual(bread.recipe, recipe)
        self.assertEqual(bread.nutrition, 5)


if __name__ == '__main__':
    unittest.main()
