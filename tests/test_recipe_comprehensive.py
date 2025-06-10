"""
Comprehensive unit tests for Recipe system covering all recipe types and edge cases.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import Mock, patch

import fabricpy
from fabricpy.recipejson import RecipeJson


class TestRecipeComprehensive(unittest.TestCase):
    """Comprehensive tests for the Recipe system."""

    def test_recipe_all_vanilla_types(self):
        """Test all vanilla Minecraft recipe types."""
        # Crafting Shaped
        shaped_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["###", " # ", "###"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "test:stone_bowl", "count": 1}
        })
        self.assertEqual(shaped_recipe.data["type"], "minecraft:crafting_shaped")
        
        # Crafting Shapeless
        shapeless_recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:wheat", "minecraft:wheat", "minecraft:wheat"],
            "result": {"id": "test:bread", "count": 1}
        })
        self.assertEqual(shapeless_recipe.data["type"], "minecraft:crafting_shapeless")
        
        # Smelting
        smelting_recipe = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": "minecraft:cobblestone",
            "result": "test:stone",
            "experience": 0.1,
            "cookingtime": 200
        })
        self.assertEqual(smelting_recipe.data["type"], "minecraft:smelting")
        
        # Blasting
        blasting_recipe = RecipeJson({
            "type": "minecraft:blasting",
            "ingredient": "minecraft:iron_ore",
            "result": "minecraft:iron_ingot",
            "experience": 0.7,
            "cookingtime": 100
        })
        self.assertEqual(blasting_recipe.data["type"], "minecraft:blasting")
        
        # Smoking
        smoking_recipe = RecipeJson({
            "type": "minecraft:smoking",
            "ingredient": "minecraft:porkchop",
            "result": "minecraft:cooked_porkchop",
            "experience": 0.35,
            "cookingtime": 100
        })
        self.assertEqual(smoking_recipe.data["type"], "minecraft:smoking")
        
        # Campfire Cooking
        campfire_recipe = RecipeJson({
            "type": "minecraft:campfire_cooking",
            "ingredient": "minecraft:beef",
            "result": "minecraft:cooked_beef",
            "experience": 0.35,
            "cookingtime": 600
        })
        self.assertEqual(campfire_recipe.data["type"], "minecraft:campfire_cooking")

    def test_recipe_shaped_patterns(self):
        """Test various shaped recipe patterns."""
        # 1x1 pattern
        tiny_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#"],
            "key": {"#": "minecraft:diamond"},
            "result": {"id": "test:diamond_shard", "count": 9}
        })
        self.assertEqual(len(tiny_recipe.data["pattern"]), 1)
        
        # 1x2 pattern
        stick_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped", 
            "pattern": ["#", "#"],
            "key": {"#": "minecraft:bamboo"},
            "result": {"id": "test:bamboo_stick", "count": 4}
        })
        self.assertEqual(len(stick_recipe.data["pattern"]), 2)
        
        # 2x1 pattern
        wide_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["##"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "test:stone_slab", "count": 6}
        })
        self.assertEqual(len(wide_recipe.data["pattern"][0]), 2)
        
        # 2x2 pattern
        medium_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["##", "##"],
            "key": {"#": "minecraft:wood"},
            "result": {"id": "test:wood_block", "count": 1}
        })
        self.assertEqual(len(medium_recipe.data["pattern"]), 2)
        self.assertEqual(len(medium_recipe.data["pattern"][0]), 2)
        
        # 3x3 pattern (full crafting grid)
        full_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["###", "###", "###"],
            "key": {"#": "minecraft:iron_ingot"},
            "result": {"id": "test:iron_block", "count": 1}
        })
        self.assertEqual(len(full_recipe.data["pattern"]), 3)
        self.assertEqual(len(full_recipe.data["pattern"][0]), 3)

    def test_recipe_complex_keys(self):
        """Test recipes with complex key mappings."""
        # Multiple different keys
        complex_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["ABC", "DEF", "GHI"],
            "key": {
                "A": "minecraft:stone",
                "B": "minecraft:iron_ingot", 
                "C": "minecraft:gold_ingot",
                "D": "minecraft:diamond",
                "E": "minecraft:emerald",
                "F": "minecraft:redstone",
                "G": "minecraft:lapis_lazuli",
                "H": "minecraft:quartz",
                "I": "minecraft:obsidian"
            },
            "result": {"id": "test:ultimate_block", "count": 1}
        })
        self.assertEqual(len(complex_recipe.data["key"]), 9)
        
        # Keys with item tags
        tag_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["###", "#X#", "###"],
            "key": {
                "#": {"tag": "minecraft:logs"},
                "X": "minecraft:stick"
            },
            "result": {"id": "test:wooden_frame", "count": 1}
        })
        self.assertIn("tag", tag_recipe.data["key"]["#"])
        
        # Keys with item counts
        count_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["# #", " X ", "# #"],
            "key": {
                "#": {"item": "minecraft:iron_ingot", "count": 2},
                "X": "minecraft:stick"
            },
            "result": {"id": "test:reinforced_tool", "count": 1}
        })
        self.assertIn("count", count_recipe.data["key"]["#"])

    def test_recipe_shapeless_variations(self):
        """Test various shapeless recipe configurations."""
        # Simple shapeless
        simple_shapeless = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:wheat"],
            "result": {"id": "test:flour", "count": 1}
        })
        self.assertEqual(len(simple_shapeless.data["ingredients"]), 1)
        
        # Multiple same ingredients
        multiple_same = RecipeJson({
            "type": "minecraft:crafting_shapeless", 
            "ingredients": [
                "minecraft:wheat",
                "minecraft:wheat", 
                "minecraft:wheat",
                "minecraft:wheat"
            ],
            "result": {"id": "test:wheat_bundle", "count": 1}
        })
        self.assertEqual(len(multiple_same.data["ingredients"]), 4)
        
        # Mixed ingredients
        mixed_ingredients = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": [
                "minecraft:apple",
                "minecraft:sugar",
                "minecraft:egg",
                {"tag": "minecraft:milk"}
            ],
            "result": {"id": "test:apple_pie", "count": 1}
        })
        self.assertEqual(len(mixed_ingredients.data["ingredients"]), 4)

    def test_recipe_cooking_variations(self):
        """Test various cooking recipe types with different parameters."""
        # Fast cooking (blast furnace style)
        fast_cook = RecipeJson({
            "type": "minecraft:blasting",
            "ingredient": "test:raw_copper",
            "result": "test:copper_ingot",
            "experience": 0.5,
            "cookingtime": 50  # Half the normal time
        })
        self.assertEqual(fast_cook.data["cookingtime"], 50)
        
        # Slow cooking (campfire style)
        slow_cook = RecipeJson({
            "type": "minecraft:campfire_cooking",
            "ingredient": "minecraft:chicken",
            "result": "minecraft:cooked_chicken", 
            "experience": 0.35,
            "cookingtime": 600  # Much longer
        })
        self.assertEqual(slow_cook.data["cookingtime"], 600)
        
        # High experience
        high_exp = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": "test:rare_ore",
            "result": "test:rare_ingot",
            "experience": 10.0,  # Much higher than normal
            "cookingtime": 200
        })
        self.assertEqual(high_exp.data["experience"], 10.0)
        
        # Zero experience
        no_exp = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": "test:stone_dust",
            "result": "minecraft:stone",
            "experience": 0.0,
            "cookingtime": 200
        })
        self.assertEqual(no_exp.data["experience"], 0.0)

    def test_recipe_result_variations(self):
        """Test various result configurations."""
        # Single item result
        single_result = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:stick"],
            "result": "test:wooden_shard"
        })
        self.assertEqual(single_result.data["result"], "test:wooden_shard")
        
        # Item with count
        count_result = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["###"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "test:stone_slabs", "count": 6}
        })
        self.assertEqual(count_result.data["result"]["count"], 6)
        
        # Item with NBT data
        nbt_result = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [" # ", "###", " # "],
            "key": {"#": "minecraft:iron_ingot"},
            "result": {
                "id": "test:enchanted_sword",
                "count": 1,
                "nbt": "{Enchantments:[{id:\"minecraft:sharpness\",lvl:1}]}"
            }
        })
        self.assertIn("nbt", nbt_result.data["result"] if isinstance(nbt_result.data["result"], dict) else {})

    def test_recipe_json_string_parsing(self):
        """Test creating recipes from JSON strings."""
        json_string = """{
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "# #",
                " # ",
                "# #"  
            ],
            "key": {
                "#": "minecraft:stick"
            },
            "result": {
                "id": "test:ladder",
                "count": 3
            }
        }"""
        
        recipe = RecipeJson(json_string)
        self.assertEqual(recipe.data["type"], "minecraft:crafting_shaped")
        self.assertEqual(recipe.data["result"]["count"], 3)
        
        # Test that the text property preserves formatting
        parsed_back = json.loads(recipe.text)
        self.assertEqual(parsed_back["type"], "minecraft:crafting_shaped")

    def test_recipe_edge_cases(self):
        """Test edge cases for recipe creation."""
        # Empty pattern (should be valid)
        empty_pattern = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [],
            "key": {},
            "result": {"id": "test:nothing", "count": 1}
        })
        self.assertEqual(len(empty_pattern.data["pattern"]), 0)
        
        # Large count result
        large_count = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:diamond_block"],
            "result": {"id": "test:diamond_dust", "count": 64}
        })
        self.assertEqual(large_count.data["result"]["count"], 64)
        
        # Very long cooking time
        long_cook = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": "test:hard_ore",
            "result": "test:hard_ingot",
            "experience": 1.0,
            "cookingtime": 10000  # Very long
        })
        self.assertEqual(long_cook.data["cookingtime"], 10000)

    def test_recipe_id_extraction(self):
        """Test extracting result IDs from various recipe formats."""
        # String result
        string_recipe = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": "minecraft:cobblestone", 
            "result": "minecraft:stone"
        })
        self.assertEqual(string_recipe.get_result_id(), "minecraft:stone")
        
        # Object result
        object_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#"],
            "key": {"#": "minecraft:wood"},
            "result": {"id": "test:wood_shard", "count": 4}
        })
        self.assertEqual(object_recipe.get_result_id(), "test:wood_shard")
        
        # No result
        no_result_recipe = RecipeJson({
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["minecraft:stick"]
        })
        self.assertIsNone(no_result_recipe.get_result_id())


class TestRecipeUsageCases(unittest.TestCase):
    """Test realistic usage cases for recipes."""

    def test_create_recipe_collection(self):
        """Test creating a collection of related recipes."""
        # Tool recipes
        tool_recipes = [
            RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["##", " #", " #"],
                "key": {"#": "minecraft:iron_ingot"},
                "result": {"id": "test:iron_hammer", "count": 1}
            }),
            RecipeJson({
                "type": "minecraft:crafting_shaped", 
                "pattern": ["# #", " # ", " # "],
                "key": {"#": "minecraft:iron_ingot"},
                "result": {"id": "test:iron_pickaxe", "count": 1}
            })
        ]
        
        # Food recipes
        food_recipes = [
            RecipeJson({
                "type": "minecraft:crafting_shapeless",
                "ingredients": ["minecraft:wheat", "minecraft:sugar", "minecraft:egg"], 
                "result": {"id": "test:cake_mix", "count": 1}
            }),
            RecipeJson({
                "type": "minecraft:smelting",
                "ingredient": "test:cake_mix",
                "result": "test:cake",
                "experience": 0.5,
                "cookingtime": 300
            })
        ]
        
        all_recipes = tool_recipes + food_recipes
        self.assertEqual(len(all_recipes), 4)
        self.assertTrue(all(isinstance(recipe, RecipeJson) for recipe in all_recipes))

    def test_recipe_mod_integration(self):
        """Test integrating recipes with mod components."""
        mod = fabricpy.ModConfig(
            mod_id="recipetest",
            name="Recipe Test Mod",
            version="1.0.0",
            description="A mod for testing recipes.",
            authors=["Test Author"]
        )
        
        # Create items with recipes
        items_with_recipes = [
            fabricpy.Item(
                id="recipetest:copper_wire",
                name="Copper Wire",
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["###"],
                    "key": {"#": "minecraft:copper_ingot"},
                    "result": {"id": "recipetest:copper_wire", "count": 3}
                })
            ),
            fabricpy.FoodItem(
                id="recipetest:energy_bar", 
                name="Energy Bar",
                nutrition=4,
                saturation=2.4,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": ["minecraft:wheat", "minecraft:sugar", "minecraft:cocoa_beans"],
                    "result": {"id": "recipetest:energy_bar", "count": 2}
                })
            )
        ]
        
        # Register items
        for item in items_with_recipes:
            mod.registerItem(item)
        
        # Verify integration
        self.assertEqual(len(mod.registered_items), 2)
        self.assertTrue(all(item.recipe is not None for item in mod.registered_items))
        self.assertTrue(all(isinstance(item.recipe, RecipeJson) for item in mod.registered_items))


if __name__ == '__main__':
    unittest.main()
