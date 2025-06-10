"""
Performance and stress tests for fabricpy library.
"""

import unittest
import time
import gc
import tempfile
import os
from unittest.mock import Mock, patch

import fabricpy
from fabricpy.item import Item
from fabricpy.fooditem import FoodItem
from fabricpy.block import Block
from fabricpy.recipejson import RecipeJson
from fabricpy import item_group


class TestPerformance(unittest.TestCase):
    """Performance tests for fabricpy components."""

    def test_create_many_items(self):
        """Test creating a large number of items."""
        start_time = time.time()
        items = []
        
        # Create 1000 items
        for i in range(1000):
            item = Item(
                id=f"test:item_{i}",
                name=f"Test Item {i}",
                max_stack_size=64,
                texture_path=f"textures/items/item_{i}.png",
                item_group=item_group.INGREDIENTS  # Use available constant
            )
            items.append(item)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 1000 items in reasonable time (less than 1 second)
        self.assertLess(creation_time, 1.0, f"Creating 1000 items took {creation_time:.3f}s")
        self.assertEqual(len(items), 1000)
        
        # Verify all items are properly created
        for i, item in enumerate(items):
            self.assertEqual(item.id, f"test:item_{i}")
            self.assertEqual(item.name, f"Test Item {i}")

    def test_create_many_food_items(self):
        """Test creating a large number of food items."""
        start_time = time.time()
        foods = []
        
        # Create 500 food items with varying properties
        for i in range(500):
            food = FoodItem(
                id=f"test:food_{i}",
                name=f"Test Food {i}",
                nutrition=i % 20,  # 0-19 nutrition
                saturation=float(i % 10),  # 0.0-9.0 saturation
                always_edible=(i % 10 == 0),  # Every 10th item is always edible
                item_group=item_group.FOOD_AND_DRINK
            )
            foods.append(food)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 500 food items quickly
        self.assertLess(creation_time, 0.5, f"Creating 500 food items took {creation_time:.3f}s")
        self.assertEqual(len(foods), 500)
        
        # Verify nutrition variety
        nutrition_values = [food.nutrition for food in foods]
        self.assertGreater(len(set(nutrition_values)), 1)  # Should have variety

    def test_create_many_blocks(self):
        """Test creating a large number of blocks."""
        start_time = time.time()
        blocks = []
        
        # Create 750 blocks
        for i in range(750):
            block = Block(
                id=f"test:block_{i}",
                name=f"Test Block {i}",
                block_texture_path=f"textures/blocks/block_{i}.png",
                inventory_texture_path=f"textures/items/block_{i}.png" if i % 2 == 0 else None,
                item_group=item_group.BUILDING_BLOCKS
            )
            blocks.append(block)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 750 blocks quickly
        self.assertLess(creation_time, 0.75, f"Creating 750 blocks took {creation_time:.3f}s")
        self.assertEqual(len(blocks), 750)
        
        # Verify texture fallback works
        blocks_with_fallback = [b for b in blocks if b.inventory_texture_path == b.block_texture_path]
        self.assertGreater(len(blocks_with_fallback), 0)

    def test_create_many_recipes(self):
        """Test creating a large number of recipes."""
        start_time = time.time()
        recipes = []
        
        # Create 300 recipes of various types
        for i in range(300):
            if i % 3 == 0:
                # Shaped recipe
                recipe = RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["###", "# #", "###"],
                    "key": {"#": f"test:material_{i}"},
                    "result": {"id": f"test:result_{i}", "count": 1}
                })
            elif i % 3 == 1:
                # Shapeless recipe
                recipe = RecipeJson({
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": [f"test:ingredient_{i}", f"test:ingredient_{i+1}"],
                    "result": {"id": f"test:result_{i}", "count": 2}
                })
            else:
                # Smelting recipe
                recipe = RecipeJson({
                    "type": "minecraft:smelting",
                    "ingredient": f"test:raw_{i}",
                    "result": f"test:cooked_{i}",
                    "experience": 0.1,
                    "cookingtime": 200
                })
            recipes.append(recipe)
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Should create 300 recipes quickly
        self.assertLess(creation_time, 0.5, f"Creating 300 recipes took {creation_time:.3f}s")
        self.assertEqual(len(recipes), 300)
        
        # Verify recipe type distribution
        recipe_types = [r.data["type"] for r in recipes]
        self.assertIn("minecraft:crafting_shaped", recipe_types)
        self.assertIn("minecraft:crafting_shapeless", recipe_types)
        self.assertIn("minecraft:smelting", recipe_types)

    def test_large_mod_registration(self):
        """Test registering a large number of items and blocks in a mod."""
        mod = fabricpy.ModConfig(
            mod_id="performance_test",
            name="Performance Test Mod",
            version="1.0.0",
            description="A mod for performance testing.",
            authors=["Test Author"]
        )
        
        start_time = time.time()
        
        # Register 200 items
        for i in range(200):
            item = Item(id=f"performance_test:item_{i}", name=f"Item {i}")
            mod.registerItem(item)
        
        # Register 100 food items
        for i in range(100):
            food = FoodItem(
                id=f"performance_test:food_{i}",
                name=f"Food {i}",
                nutrition=i % 10,
                saturation=float(i % 5)
            )
            mod.registerItem(food)
        
        # Register 150 blocks
        for i in range(150):
            block = Block(id=f"performance_test:block_{i}", name=f"Block {i}")
            mod.registerBlock(block)
        
        end_time = time.time()
        registration_time = end_time - start_time
        
        # Should register 450 items/blocks quickly
        self.assertLess(registration_time, 1.0, f"Registering 450 items/blocks took {registration_time:.3f}s")
        self.assertEqual(len(mod.registered_items), 300)  # 200 items + 100 food items
        self.assertEqual(len(mod.registered_blocks), 150)

    def test_memory_usage_items(self):
        """Test memory usage when creating many items."""
        # Force garbage collection before test
        gc.collect()
        
        # Create a large number of items
        items = []
        for i in range(2000):
            item = Item(
                id=f"test:memory_item_{i}",
                name=f"Memory Test Item {i}",
                max_stack_size=64,
                texture_path=f"textures/items/memory_item_{i}.png"
            )
            items.append(item)
        
        # Verify all items are created
        self.assertEqual(len(items), 2000)
        
        # Test that items maintain their properties
        sample_item = items[1000]
        self.assertEqual(sample_item.id, "test:memory_item_1000")
        self.assertEqual(sample_item.name, "Memory Test Item 1000")
        
        # Clean up
        del items
        gc.collect()

    def test_recipe_parsing_performance(self):
        """Test performance of recipe JSON parsing."""
        # Create a complex recipe JSON string
        complex_recipe_json = """{
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "ABCDEFGHI",
                "JKLMNOPQR", 
                "STUVWXYZ1"
            ],
            "key": {
                "A": "minecraft:stone", "B": "minecraft:iron_ingot", "C": "minecraft:gold_ingot",
                "D": "minecraft:diamond", "E": "minecraft:emerald", "F": "minecraft:redstone",
                "G": "minecraft:lapis_lazuli", "H": "minecraft:quartz", "I": "minecraft:obsidian",
                "J": "minecraft:coal", "K": "minecraft:charcoal", "L": "minecraft:stick",
                "M": "minecraft:string", "N": "minecraft:leather", "O": "minecraft:feather",
                "P": "minecraft:bone", "Q": "minecraft:gunpowder", "R": "minecraft:blaze_powder",
                "S": "minecraft:ender_pearl", "T": "minecraft:glass", "U": "minecraft:sand",
                "V": "minecraft:gravel", "W": "minecraft:clay", "X": "minecraft:brick",
                "Y": "minecraft:nether_brick", "Z": "minecraft:prismarine", "1": "minecraft:sea_lantern"
            },
            "result": {
                "id": "test:ultimate_item",
                "count": 1,
                "nbt": "{display:{Name:'Ultimate Item',Lore:['A very complex item']}}"
            }
        }"""
        
        start_time = time.time()
        
        # Parse the recipe 100 times
        recipes = []
        for i in range(100):
            recipe = RecipeJson(complex_recipe_json)
            recipes.append(recipe)
        
        end_time = time.time()
        parsing_time = end_time - start_time
        
        # Should parse 100 complex recipes quickly
        self.assertLess(parsing_time, 0.5, f"Parsing 100 complex recipes took {parsing_time:.3f}s")
        self.assertEqual(len(recipes), 100)
        
        # Verify parsing correctness
        for recipe in recipes:
            self.assertEqual(recipe.data["type"], "minecraft:crafting_shaped")
            self.assertEqual(len(recipe.data["key"]), 27)  # 26 letters + 1 number


class TestStressTests(unittest.TestCase):
    """Stress tests for fabricpy library."""

    def test_extreme_item_creation(self):
        """Test creating an extreme number of items."""
        # Create 5000 items (stress test)
        items = []
        for i in range(5000):
            item = Item(
                id=f"stress:item_{i}",
                name=f"Stress Item {i}",
                max_stack_size=(i % 64) + 1,  # Vary stack sizes
                texture_path=f"textures/items/stress_{i}.png"
            )
            items.append(item)
        
        self.assertEqual(len(items), 5000)
        
        # Test random access
        self.assertEqual(items[2500].id, "stress:item_2500")
        self.assertEqual(items[4999].id, "stress:item_4999")

    def test_mixed_component_creation(self):
        """Test creating a large mix of different components."""
        mod = fabricpy.ModConfig(
            mod_id="stress_test",
            name="Stress Test Mod",
            version="1.0.0",
            description="Stress testing mod.",
            authors=["Stress Tester"]
        )
        
        # Create a mix of components
        for i in range(1000):
            if i % 4 == 0:
                # Regular item
                item = Item(id=f"stress_test:item_{i}", name=f"Item {i}")
                mod.registerItem(item)
            elif i % 4 == 1:
                # Food item
                food = FoodItem(
                    id=f"stress_test:food_{i}",
                    name=f"Food {i}",
                    nutrition=i % 20,
                    saturation=float(i % 10)
                )
                mod.registerItem(food)
            elif i % 4 == 2:
                # Block
                block = Block(id=f"stress_test:block_{i}", name=f"Block {i}")
                mod.registerBlock(block)
            else:
                # Item with recipe  
                recipe = RecipeJson({
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": [f"stress_test:item_{i-3}"],
                    "result": {"id": f"stress_test:crafted_{i}", "count": 1}
                })
                item = Item(
                    id=f"stress_test:crafted_{i}",
                    name=f"Crafted {i}",
                    recipe=recipe
                )
                mod.registerItem(item)
        
        # Verify counts
        total_items = len(mod.registered_items)
        total_blocks = len(mod.registered_blocks)
        
        self.assertGreater(total_items, 700)  # Should have many items
        self.assertGreater(total_blocks, 200)  # Should have many blocks
        self.assertEqual(total_items + total_blocks, 1000)  # Total should be 1000

    def test_complex_recipe_stress(self):
        """Test creating many complex recipes."""
        recipes = []
        
        # Create 500 complex shaped recipes
        for i in range(500):
            recipe = RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": [
                    f"A{i%10}B",
                    f"{i%10}C{i%10}",
                    f"D{i%10}E"
                ],
                "key": {
                    "A": f"test:material_a_{i}",
                    "B": f"test:material_b_{i}",
                    "C": f"test:material_c_{i}",
                    "D": f"test:material_d_{i}",
                    "E": f"test:material_e_{i}",
                    f"{i%10}": f"test:number_mat_{i%10}"
                },
                "result": {
                    "id": f"test:complex_result_{i}",
                    "count": (i % 8) + 1,
                    "nbt": f"{{CustomData:{i}}}"
                }
            })
            recipes.append(recipe)
        
        self.assertEqual(len(recipes), 500)
        
        # Verify recipe complexity
        for i, recipe in enumerate(recipes):
            self.assertEqual(len(recipe.data["key"]), 6)  # 5 letters + 1 number
            self.assertEqual(recipe.data["result"]["id"], f"test:complex_result_{i}")


if __name__ == '__main__':
    unittest.main()
