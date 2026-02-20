"""
Unit tests for the RecipeJson class.
"""

import json
import unittest

from fabricpy.recipejson import RecipeJson


class TestRecipeJson(unittest.TestCase):
    """Test the RecipeJson class."""

    def test_recipe_creation_from_string(self):
        """Test creating a recipe from a JSON string."""
        recipe_str = (
            '{"type": "minecraft:crafting_shaped", "result": {"id": "test:item"}}'
        )
        recipe = RecipeJson(recipe_str)
        self.assertEqual(recipe.data["type"], "minecraft:crafting_shaped")
        self.assertEqual(recipe.data["result"]["id"], "test:item")

    def test_recipe_creation_from_dict(self):
        """Test creating a recipe from a dictionary."""
        recipe_dict = {
            "type": "minecraft:crafting_shapeless",
            "result": {"id": "testmod:bread", "count": 2},
        }
        recipe = RecipeJson(recipe_dict)
        self.assertEqual(recipe.data["type"], "minecraft:crafting_shapeless")
        self.assertEqual(recipe.data["result"]["id"], "testmod:bread")

    def test_recipe_result_id_extraction(self):
        """Test extracting result ID from recipes."""
        recipe_new = RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "result": {"id": "testmod:new_item", "count": 1},
            }
        )
        self.assertEqual(recipe_new.result_id, "testmod:new_item")
        self.assertEqual(recipe_new.get_result_id(), "testmod:new_item")

    def test_recipe_result_id_none(self):
        """Test recipe with no result ID."""
        recipe = RecipeJson({"type": "minecraft:smelting", "result": {"count": 1}})
        self.assertIsNone(recipe.result_id)
        self.assertIsNone(recipe.get_result_id())

    def test_recipe_validation_missing_type(self):
        """Test that recipe validation fails when 'type' is missing."""
        with self.assertRaises(ValueError) as context:
            RecipeJson({"result": {"id": "testmod:item", "count": 1}})
        self.assertIn("type", str(context.exception))

    def test_recipe_complex_shaped(self):
        """Test a complex shaped recipe."""
        recipe_dict = {
            "type": "minecraft:crafting_shaped",
            "pattern": ["ABA", "CDC", "ABA"],
            "key": {
                "A": "minecraft:iron_ingot",
                "B": "minecraft:diamond",
                "C": "minecraft:redstone",
                "D": "minecraft:gold_block",
            },
            "result": {"id": "testmod:advanced_machine", "count": 1},
        }
        recipe = RecipeJson(recipe_dict)
        self.assertEqual(recipe.data["type"], "minecraft:crafting_shaped")
        self.assertEqual(len(recipe.data["pattern"]), 3)
        self.assertEqual(len(recipe.data["key"]), 4)
        self.assertEqual(recipe.result_id, "testmod:advanced_machine")

    def test_recipe_shapeless(self):
        """Test a shapeless recipe."""
        recipe_dict = {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [{"item": "minecraft:wheat"}, {"item": "minecraft:egg"}],
            "result": {"id": "testmod:cake", "count": 1},
        }
        recipe = RecipeJson(recipe_dict)
        self.assertEqual(recipe.data["type"], "minecraft:crafting_shapeless")
        self.assertEqual(len(recipe.data["ingredients"]), 2)
        self.assertEqual(recipe.result_id, "testmod:cake")

    def test_recipe_smelting(self):
        """Test a smelting recipe."""
        recipe_dict = {
            "type": "minecraft:smelting",
            "ingredient": {"item": "testmod:raw_copper"},
            "result": {"id": "minecraft:copper_ingot", "count": 1},
            "experience": 0.7,
            "cookingtime": 200,
        }
        recipe = RecipeJson(recipe_dict)
        self.assertEqual(recipe.data["type"], "minecraft:smelting")
        self.assertEqual(recipe.data["ingredient"]["item"], "testmod:raw_copper")
        self.assertEqual(recipe.data["experience"], 0.7)
        self.assertEqual(recipe.data["cookingtime"], 200)

    def test_recipe_text_property(self):
        """Test that the text property preserves formatting."""
        original_str = (
            '{"type": "minecraft:crafting_shaped", "result": {"id": "testmod:item"}}'
        )
        recipe = RecipeJson(original_str)
        parsed_from_text = json.loads(recipe.text)
        self.assertEqual(parsed_from_text["type"], "minecraft:crafting_shaped")

    def test_recipe_json_round_trip(self):
        """Test that recipe data survives round-trip conversion."""
        original_dict = {
            "type": "minecraft:crafting_shaped",
            "pattern": ["AB", "CD"],
            "key": {
                "A": "minecraft:iron_ingot",
                "B": "minecraft:gold_ingot",
                "C": "minecraft:diamond",
                "D": "minecraft:emerald",
            },
            "result": {"id": "testmod:precious_block", "count": 1},
        }
        recipe = RecipeJson(original_dict)
        parsed_dict = json.loads(recipe.text)
        self.assertEqual(parsed_dict["type"], original_dict["type"])
        self.assertEqual(parsed_dict["pattern"], original_dict["pattern"])
        self.assertEqual(parsed_dict["key"], original_dict["key"])
        self.assertEqual(parsed_dict["result"], original_dict["result"])


if __name__ == "__main__":
    unittest.main()
