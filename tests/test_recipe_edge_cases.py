"""
Comprehensive edge case tests for RecipeJson class.
These tests focus on boundary conditions and potential failure modes.
"""

import unittest
import json
from fabricpy.recipejson import RecipeJson


class TestRecipeJsonEdgeCases(unittest.TestCase):
    """Test edge cases and potential failure modes in RecipeJson."""

    def test_result_id_with_none_result(self):
        """Test result_id when result is explicitly None."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": None
        })
        self.assertIsNone(recipe.result_id)
        self.assertIsNone(recipe.get_result_id())

    def test_result_id_with_numeric_result(self):
        """Test result_id when result is a number (invalid but handled gracefully)."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": 42
        })
        self.assertIsNone(recipe.result_id)
        self.assertIsNone(recipe.get_result_id())

    def test_result_id_with_boolean_result(self):
        """Test result_id when result is a boolean (invalid but handled gracefully)."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": True
        })
        self.assertIsNone(recipe.result_id)
        self.assertIsNone(recipe.get_result_id())

    def test_result_id_with_list_result(self):
        """Test result_id when result is a list (invalid but handled gracefully)."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": ["test:item"]
        })
        self.assertIsNone(recipe.result_id)
        self.assertIsNone(recipe.get_result_id())

    def test_result_id_empty_string(self):
        """Test result_id when result is an empty string."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": ""
        })
        self.assertEqual(recipe.result_id, "")
        self.assertEqual(recipe.get_result_id(), "")

    def test_result_id_dict_with_none_values(self):
        """Test result_id when result dict has None values."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": {"id": None, "item": None}
        })
        self.assertIsNone(recipe.result_id)
        self.assertIsNone(recipe.get_result_id())

    def test_result_id_dict_with_empty_strings(self):
        """Test result_id when result dict has empty strings."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": {"id": "", "item": ""}
        })
        # Should return the first non-None value (empty string)
        self.assertEqual(recipe.result_id, "")
        self.assertEqual(recipe.get_result_id(), "")

    def test_result_id_dict_with_mixed_values(self):
        """Test result_id when result dict has mixed value types."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": {"id": 123, "item": "test:item", "count": 1}
        })
        # Should return "test:item" since "id" is not a string
        self.assertEqual(recipe.result_id, "test:item")
        self.assertEqual(recipe.get_result_id(), "test:item")

    def test_result_id_dict_only_id(self):
        """Test result_id when result dict only has 'id'."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": {"id": "test:new_format"}
        })
        self.assertEqual(recipe.result_id, "test:new_format")
        self.assertEqual(recipe.get_result_id(), "test:new_format")

    def test_result_id_dict_only_item(self):
        """Test result_id when result dict only has 'item'."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": {"item": "test:old_format"}
        })
        self.assertEqual(recipe.result_id, "test:old_format")
        self.assertEqual(recipe.get_result_id(), "test:old_format")

    def test_result_id_dict_both_id_and_item(self):
        """Test result_id when result dict has both 'id' and 'item'."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": {"id": "test:new", "item": "test:old"}
        })
        # Should prefer 'id' over 'item'
        self.assertEqual(recipe.result_id, "test:new")
        self.assertEqual(recipe.get_result_id(), "test:new")

    def test_result_id_dict_neither_id_nor_item(self):
        """Test result_id when result dict has neither 'id' nor 'item'."""
        recipe = RecipeJson({
            "type": "minecraft:smelting",
            "result": {"count": 1, "nbt": {}}
        })
        self.assertIsNone(recipe.result_id)
        self.assertIsNone(recipe.get_result_id())

    def test_recipe_with_malformed_json_string(self):
        """Test that malformed JSON strings raise proper exceptions.""" 
        malformed_json_cases = [
            '{"type": "test", "result":}',  # Incomplete
            '{"type": "test" "result": "item"}',  # Missing comma
            '{"type": "test", "result": "item",}',  # Trailing comma
            '{type: "test", result: "item"}',  # Unquoted keys
            "{'type': 'test', 'result': 'item'}",  # Single quotes
        ]
        
        for malformed_json in malformed_json_cases:
            with self.subTest(json_string=malformed_json):
                with self.assertRaises(json.JSONDecodeError):
                    RecipeJson(malformed_json)

    def test_recipe_missing_type_field(self):
        """Test various ways the type field can be missing or invalid."""
        # Cases that should raise ValueError
        invalid_type_cases = [
            {},  # Empty dict
            {"result": "test:item"},  # Missing type
            {"type": None, "result": "test:item"},  # None type
            {"type": "", "result": "test:item"},  # Empty type
            {"type": "   ", "result": "test:item"},  # Whitespace-only type
        ]
        
        for case in invalid_type_cases:
            with self.subTest(recipe_data=case):
                with self.assertRaises(ValueError) as context:
                    RecipeJson(case)
                self.assertIn("type", str(context.exception))
        
        # Cases with non-string types that should also raise ValueError
        non_string_type_cases = [
            {"type": 123, "result": "test:item"},  # Numeric type
            {"type": [], "result": "test:item"},  # List type
            {"type": {}, "result": "test:item"},  # Dict type
            {"type": True, "result": "test:item"},  # Boolean type
        ]
        
        for case in non_string_type_cases:
            with self.subTest(recipe_data=case):
                with self.assertRaises(ValueError) as context:
                    RecipeJson(case)
                self.assertIn("type", str(context.exception))

    def test_recipe_json_whitespace_handling(self):
        """Test that JSON string whitespace is handled correctly."""
        whitespace_cases = [
            '  {"type": "test", "result": "item"}  ',  # Leading/trailing
            '{\n  "type": "test",\n  "result": "item"\n}',  # Newlines
            '{\t"type":\t"test",\t"result":\t"item"\t}',  # Tabs
            '{ "type" : "test" , "result" : "item" }',  # Extra spaces
        ]
        
        for json_string in whitespace_cases:
            with self.subTest(json_string=repr(json_string)):
                recipe = RecipeJson(json_string)
                self.assertEqual(recipe.data["type"], "test")
                self.assertEqual(recipe.data["result"], "item")
                self.assertEqual(recipe.result_id, "item")

    def test_property_vs_method_consistency(self):
        """Ensure result_id property and get_result_id() method always return same value."""
        test_cases = [
            {"type": "test"},  # No result
            {"type": "test", "result": None},  # None result
            {"type": "test", "result": "string_result"},  # String result
            {"type": "test", "result": {"id": "dict_id"}},  # Dict with id
            {"type": "test", "result": {"item": "dict_item"}},  # Dict with item
            {"type": "test", "result": {"id": "new", "item": "old"}},  # Both
            {"type": "test", "result": {}},  # Empty dict
            {"type": "test", "result": 42},  # Invalid type
            {"type": "test", "result": []},  # Invalid type
        ]
        
        for case in test_cases:
            with self.subTest(recipe_data=case):
                recipe = RecipeJson(case)
                self.assertEqual(
                    recipe.result_id, 
                    recipe.get_result_id(),
                    f"Property and method returned different values for {case}"
                )

    def test_unicode_and_special_characters(self):
        """Test recipes with unicode and special characters."""
        unicode_cases = [
            {"type": "test", "result": "test:café"},  # Accented characters
            {"type": "test", "result": "test:日本語"},  # Japanese characters  
            {"type": "test", "result": "test:🎂"},  # Emoji
            {"type": "test", "result": "test:item-with_special.chars"},  # Special chars
            {"type": "test", "result": "test:item with spaces"},  # Spaces
        ]
        
        for case in unicode_cases:
            with self.subTest(recipe_data=case):
                recipe = RecipeJson(case)
                self.assertEqual(recipe.result_id, case["result"])
                self.assertEqual(recipe.get_result_id(), case["result"])

    def test_deep_nesting_handling(self):
        """Test recipes with deeply nested structures."""
        nested_recipe = {
            "type": "minecraft:crafting_shaped",
            "pattern": ["ABC", "DEF", "GHI"],
            "key": {
                "A": {"item": "minecraft:iron_ingot", "nbt": {"display": {"Name": "Custom Iron"}}},
                "B": {"tag": "forge:ingots/gold"},
                "C": {"item": "minecraft:diamond"},
                "D": {"item": "minecraft:redstone"},
                "E": {"item": "minecraft:emerald"},
                "F": {"item": "minecraft:quartz"},
                "G": {"item": "minecraft:lapis_lazuli"},
                "H": {"item": "minecraft:glowstone_dust"},
                "I": {"item": "minecraft:blaze_powder"}
            },
            "result": {
                "id": "testmod:ultimate_tool",
                "count": 1,
                "nbt": {
                    "display": {
                        "Name": "Ultimate Tool",
                        "Lore": ["The most powerful tool"]
                    },
                    "AttributeModifiers": [
                        {
                            "AttributeName": "generic.attackDamage",
                            "Name": "Tool modifier",
                            "Amount": 10.0,
                            "Operation": 0,
                            "UUIDLeast": 1,
                            "UUIDMost": 1
                        }
                    ]
                }
            }
        }
        
        recipe = RecipeJson(nested_recipe)
        self.assertEqual(recipe.result_id, "testmod:ultimate_tool")
        self.assertEqual(recipe.get_result_id(), "testmod:ultimate_tool")
        # Ensure the complex structure is preserved
        self.assertEqual(recipe.data["key"]["A"]["nbt"]["display"]["Name"], "Custom Iron")


class TestRecipeJsonIntegration(unittest.TestCase):
    """Integration tests for RecipeJson with real-world scenarios."""

    def test_all_minecraft_recipe_types(self):
        """Test all standard Minecraft recipe types."""
        recipe_types = [
            "minecraft:crafting_shaped",
            "minecraft:crafting_shapeless",
            "minecraft:smelting",
            "minecraft:blasting",
            "minecraft:smoking",
            "minecraft:campfire_cooking",
            "minecraft:stonecutting",
            "minecraft:smithing_transform",
            "minecraft:smithing_trim",
        ]
        
        for recipe_type in recipe_types:
            with self.subTest(recipe_type=recipe_type):
                recipe_data = {
                    "type": recipe_type,
                    "result": f"test:result_for_{recipe_type.split(':')[1]}"
                }
                recipe = RecipeJson(recipe_data)
                self.assertEqual(recipe.data["type"], recipe_type)
                expected_result = f"test:result_for_{recipe_type.split(':')[1]}"
                self.assertEqual(recipe.result_id, expected_result)

    def test_recipe_serialization_round_trip(self):
        """Test that recipes can be serialized and deserialized without data loss."""
        original_recipes = [
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["AB", "CD"],
                "key": {"A": "minecraft:iron", "B": "minecraft:gold", "C": "minecraft:diamond", "D": "minecraft:emerald"},
                "result": {"id": "test:precious_block", "count": 4}
            },
            {
                "type": "minecraft:crafting_shapeless",
                "ingredients": [{"item": "minecraft:wheat"}, {"item": "minecraft:sugar"}, {"item": "minecraft:egg"}],
                "result": {"id": "test:cake", "count": 1}
            },
            {
                "type": "minecraft:smelting",
                "ingredient": {"item": "test:raw_ore"},
                "result": {"id": "test:ingot", "count": 1},
                "experience": 0.5,
                "cookingtime": 200
            }
        ]
        
        for original in original_recipes:
            with self.subTest(recipe_type=original["type"]):
                # Create from dict
                recipe1 = RecipeJson(original)
                
                # Serialize to string
                json_string = recipe1.text
                
                # Create from string
                recipe2 = RecipeJson(json_string)
                
                # Compare data
                self.assertEqual(recipe1.data, recipe2.data)
                self.assertEqual(recipe1.result_id, recipe2.result_id)
                self.assertEqual(recipe1.get_result_id(), recipe2.get_result_id())


if __name__ == '__main__':
    unittest.main()
