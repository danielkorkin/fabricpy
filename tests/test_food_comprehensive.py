"""
Comprehensive unit tests for FoodItem class covering all food-specific functionality.
"""

import unittest

import fabricpy
from fabricpy.fooditem import FoodItem
from fabricpy.recipejson import RecipeJson
from fabricpy import item_group


class TestFoodItemComprehensive(unittest.TestCase):
    """Comprehensive tests for the FoodItem class."""

    def test_food_item_minimal_creation(self):
        """Test creating a food item with minimal parameters."""
        food = FoodItem(
            id="testmod:minimal_food",
            name="Minimal Food"
        )
        
        self.assertEqual(food.id, "testmod:minimal_food")
        self.assertEqual(food.name, "Minimal Food")
        self.assertEqual(food.nutrition, 0)
        self.assertEqual(food.saturation, 0.0)
        self.assertFalse(food.always_edible)
        self.assertEqual(food.max_stack_size, 64)

    def test_food_item_full_creation(self):
        """Test creating a food item with all parameters."""
        recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:wheat", "minecraft:sugar"],
            "result": {"id": "testmod:bread", "count": 1}
        })
        
        food = FoodItem(
            id="testmod:bread",
            name="Custom Bread",
            max_stack_size=16,
            texture_path="textures/items/bread.png",
            nutrition=5,
            saturation=6.0,
            always_edible=True,
            recipe=recipe,
            item_group=item_group.FOOD_AND_DRINK
        )
        
        self.assertEqual(food.id, "testmod:bread")
        self.assertEqual(food.name, "Custom Bread")
        self.assertEqual(food.max_stack_size, 16)
        self.assertEqual(food.texture_path, "textures/items/bread.png")
        self.assertEqual(food.nutrition, 5)
        self.assertEqual(food.saturation, 6.0)
        self.assertTrue(food.always_edible)
        self.assertEqual(food.recipe, recipe)
        self.assertEqual(food.item_group, item_group.FOOD_AND_DRINK)

    def test_food_nutrition_values(self):
        """Test various nutrition values."""
        # Zero nutrition
        food_zero = FoodItem(id="test:zero", name="Zero Food", nutrition=0)
        self.assertEqual(food_zero.nutrition, 0)
        
        # Low nutrition
        food_low = FoodItem(id="test:low", name="Low Food", nutrition=1)
        self.assertEqual(food_low.nutrition, 1)
        
        # High nutrition (like golden apple)
        food_high = FoodItem(id="test:high", name="High Food", nutrition=20)
        self.assertEqual(food_high.nutrition, 20)
        
        # Negative nutrition (should be allowed for special items)
        food_negative = FoodItem(id="test:negative", name="Negative Food", nutrition=-5)
        self.assertEqual(food_negative.nutrition, -5)

    def test_food_saturation_values(self):
        """Test various saturation values."""
        # Zero saturation
        food_zero = FoodItem(id="test:zero_sat", name="Zero Sat", saturation=0.0)
        self.assertEqual(food_zero.saturation, 0.0)
        
        # Low saturation
        food_low = FoodItem(id="test:low_sat", name="Low Sat", saturation=0.5)
        self.assertEqual(food_low.saturation, 0.5)
        
        # High saturation
        food_high = FoodItem(id="test:high_sat", name="High Sat", saturation=14.4)
        self.assertEqual(food_high.saturation, 14.4)
        
        # Fractional saturation
        food_frac = FoodItem(id="test:frac_sat", name="Frac Sat", saturation=2.125)
        self.assertEqual(food_frac.saturation, 2.125)

    def test_food_always_edible_variations(self):
        """Test always_edible property variations."""
        # Default (False)
        food_default = FoodItem(id="test:default", name="Default Food")
        self.assertFalse(food_default.always_edible)
        
        # Explicitly False
        food_false = FoodItem(id="test:false", name="False Food", always_edible=False)
        self.assertFalse(food_false.always_edible)
        
        # Explicitly True
        food_true = FoodItem(id="test:true", name="True Food", always_edible=True)
        self.assertTrue(food_true.always_edible)

    def test_food_inheritance_from_item(self):
        """Test that FoodItem properly inherits all Item functionality."""
        custom_group = fabricpy.ItemGroup(id="test_group", name="Test Group")
        recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["AB"],
            "key": {"A": "minecraft:wheat", "B": "minecraft:sugar"},
            "result": {"id": "test:cookie", "count": 8}
        })
        
        food = FoodItem(
            id="test:cookie",
            name="Test Cookie",
            max_stack_size=32,
            texture_path="textures/items/cookie.png",
            nutrition=2,
            saturation=0.4,
            always_edible=False,
            recipe=recipe,
            item_group=custom_group
        )
        
        # Test Item properties
        self.assertEqual(food.id, "test:cookie")
        self.assertEqual(food.name, "Test Cookie")
        self.assertEqual(food.max_stack_size, 32)
        self.assertEqual(food.texture_path, "textures/items/cookie.png")
        self.assertEqual(food.recipe, recipe)
        self.assertEqual(food.item_group, custom_group)
        
        # Test FoodItem-specific properties
        self.assertEqual(food.nutrition, 2)
        self.assertEqual(food.saturation, 0.4)
        self.assertFalse(food.always_edible)

    def test_food_with_vanilla_food_items(self):
        """Test creating foods similar to vanilla Minecraft foods."""
        # Apple-like
        apple = FoodItem(
            id="test:apple",
            name="Test Apple",
            nutrition=4,
            saturation=2.4,
            always_edible=False
        )
        self.assertEqual(apple.nutrition, 4)
        self.assertEqual(apple.saturation, 2.4)
        
        # Golden Apple-like (always edible)
        golden_apple = FoodItem(
            id="test:golden_apple",
            name="Test Golden Apple",
            nutrition=4,
            saturation=9.6,
            always_edible=True
        )
        self.assertTrue(golden_apple.always_edible)
        
        # Bread-like
        bread = FoodItem(
            id="test:bread",
            name="Test Bread",
            nutrition=5,
            saturation=6.0
        )
        self.assertEqual(bread.nutrition, 5)
        self.assertEqual(bread.saturation, 6.0)

    def test_food_with_complex_recipes(self):
        """Test food items with complex crafting recipes."""
        # Shaped recipe for cake-like item
        cake_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "MMM",
                "SES",
                "WWW"
            ],
            "key": {
                "M": "minecraft:milk_bucket",
                "S": "minecraft:sugar",
                "E": "minecraft:egg",
                "W": "minecraft:wheat"
            },
            "result": {"id": "test:cake", "count": 1}
        })
        
        cake = FoodItem(
            id="test:cake",
            name="Test Cake",
            max_stack_size=1,
            nutrition=2,
            saturation=0.4,
            recipe=cake_recipe
        )
        
        self.assertEqual(cake.max_stack_size, 1)
        self.assertEqual(cake.recipe, cake_recipe)
        
        # Shapeless recipe for trail mix-like item
        trail_mix_recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [
                "minecraft:wheat_seeds",
                "minecraft:pumpkin_seeds",
                "minecraft:melon_seeds",
                "minecraft:dried_kelp"
            ],
            "result": {"id": "test:trail_mix", "count": 4}
        })
        
        trail_mix = FoodItem(
            id="test:trail_mix",
            name="Test Trail Mix",
            nutrition=3,
            saturation=1.8,
            recipe=trail_mix_recipe
        )
        
        self.assertEqual(trail_mix.recipe, trail_mix_recipe)

    def test_food_edge_cases(self):
        """Test edge cases for food items."""
        # Very high nutrition values
        super_food = FoodItem(
            id="test:super_food",
            name="Super Food",
            nutrition=100,
            saturation=50.0
        )
        self.assertEqual(super_food.nutrition, 100)
        self.assertEqual(super_food.saturation, 50.0)
        
        # Zero values
        empty_food = FoodItem(
            id="test:empty_food",
            name="Empty Food",
            nutrition=0,
            saturation=0.0
        )
        self.assertEqual(empty_food.nutrition, 0)
        self.assertEqual(empty_food.saturation, 0.0)
        
        # Single stack size
        rare_food = FoodItem(
            id="test:rare_food",
            name="Rare Food",
            max_stack_size=1,
            nutrition=10,
            saturation=20.0,
            always_edible=True
        )
        self.assertEqual(rare_food.max_stack_size, 1)

    def test_food_type_validation(self):
        """Test that food item parameters accept correct types."""
        # Nutrition should accept integers
        food_int = FoodItem(id="test:int", name="Int Food", nutrition=5)
        self.assertEqual(food_int.nutrition, 5)
        self.assertIsInstance(food_int.nutrition, int)
        
        # Saturation should accept floats
        food_float = FoodItem(id="test:float", name="Float Food", saturation=2.5)
        self.assertEqual(food_float.saturation, 2.5)
        self.assertIsInstance(food_float.saturation, float)
        
        # Always_edible should accept booleans
        food_bool = FoodItem(id="test:bool", name="Bool Food", always_edible=True)
        self.assertTrue(food_bool.always_edible)
        self.assertIsInstance(food_bool.always_edible, bool)


class TestFoodItemUsageCases(unittest.TestCase):
    """Test realistic usage cases for food items."""

    def test_create_food_collection(self):
        """Test creating a collection of various food items."""
        foods = []
        
        # Basic fruits
        apple = FoodItem(id="test:apple", name="Apple", nutrition=4, saturation=2.4)
        foods.append(apple)
        
        # Cooked foods
        cooked_beef = FoodItem(id="test:cooked_beef", name="Cooked Beef", nutrition=8, saturation=12.8)
        foods.append(cooked_beef)
        
        # Special foods
        golden_carrot = FoodItem(
            id="test:golden_carrot", 
            name="Golden Carrot", 
            nutrition=6, 
            saturation=14.4,
            always_edible=True
        )
        foods.append(golden_carrot)
        
        # Verify collection
        self.assertEqual(len(foods), 3)
        self.assertTrue(all(isinstance(food, FoodItem) for food in foods))
        self.assertTrue(any(food.always_edible for food in foods))

    def test_food_mod_registration_simulation(self):
        """Simulate registering food items in a mod."""
        mod = fabricpy.ModConfig(
            mod_id="foodtest",
            name="Food Test Mod",
            version="1.0.0",
            description="A mod for testing food items.",
            authors=["Test Author"]
        )
        
        # Create various food items
        foods = [
            FoodItem(id="foodtest:apple_pie", name="Apple Pie", nutrition=8, saturation=4.8),
            FoodItem(id="foodtest:chocolate", name="Chocolate", nutrition=3, saturation=1.8),
            FoodItem(id="foodtest:energy_bar", name="Energy Bar", nutrition=6, saturation=7.2, always_edible=True)
        ]
        
        # Register foods (simulate)
        for food in foods:
            mod.registerItem(food)
        
        # Verify registration
        self.assertEqual(len(mod.registered_items), 3)
        self.assertTrue(all(isinstance(item, FoodItem) for item in mod.registered_items))


if __name__ == '__main__':
    unittest.main()
