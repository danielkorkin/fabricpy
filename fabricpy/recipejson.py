# fabricpy/recipejson.py
"""Recipe JSON handling for Fabric mods.

This module provides the RecipeJson class for defining and managing
Minecraft recipe data. Recipes define how items and blocks can be crafted,
smelted, or otherwise created through various game mechanics.

The RecipeJson class handles both string and dictionary representations
of recipe data, with validation and convenient access to recipe properties.
"""

from __future__ import annotations

import json
from typing import Any


class RecipeJson:
    """Wrapper for Minecraft recipe JSON data.

    This class holds a validated dictionary representation of a Minecraft recipe
    along with the original JSON text. It provides validation, convenient property
    access, and ensures the exact text can be written back to disk unchanged.

    Recipes define how items are crafted, smelted, or created through other
    game mechanics. They must follow Minecraft's recipe JSON format.

    Args:
        src (str | dict[str, Any]): Recipe data as either a JSON string or
            a dictionary. If a string, it will be parsed as JSON. If a dict,
            it will be used directly and converted to JSON text.

    Attributes:
        text (str): The JSON string representation of the recipe.
        data (dict[str, Any]): The parsed dictionary representation of the recipe.

    Raises:
        ValueError: If the recipe is missing a required 'type' field or has
            an invalid 'type' value.
        json.JSONDecodeError: If the input string is not valid JSON.

    Example:
        Creating a recipe from JSON string::

            recipe_json = '''
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["##", "##"],
                "key": {"#": "minecraft:stone"},
                "result": {"id": "mymod:stone_block", "count": 1}
            }
            '''
            recipe = RecipeJson(recipe_json)

        Creating a recipe from dictionary::

            recipe_data = {
                "type": "minecraft:smelting",
                "ingredient": "minecraft:iron_ore",
                "result": "minecraft:iron_ingot",
                "experience": 0.7,
                "cookingtime": 200
            }
            recipe = RecipeJson(recipe_data)

        Getting the result item ID::

            result_id = recipe.result_id  # "mymod:stone_block"
    """

    def __init__(self, src: str | dict[str, Any]):
        """Initialize a new RecipeJson instance.

        Args:
            src (str | dict[str, Any]): Recipe data as JSON string or dictionary.

        Raises:
            ValueError: If recipe is missing 'type' field or has invalid 'type'.
            json.JSONDecodeError: If input string is not valid JSON.
        """
        if isinstance(src, str):
            self.text: str = src.strip()
            self.data: dict[str, Any] = json.loads(self.text)
        else:  # already a dict
            self.data = src
            self.text = json.dumps(src, indent=2)

        # minimal sanity-check – make sure the mandatory "type" key exists and is a non-empty string
        if "type" not in self.data:
            raise ValueError("Recipe JSON must contain a 'type' field")

        recipe_type = self.data["type"]
        if not isinstance(recipe_type, str) or not recipe_type.strip():
            raise ValueError("Recipe 'type' field must be a non-empty string")

    # convenience helpers ------------------------------------------------
    @property
    def result_id(self) -> str | None:
        """Get the result item identifier from the recipe.

        Extracts the item ID from the recipe's result field, which is used
        to name the generated recipe JSON file. Handles both string and
        dictionary result formats.

        Returns:
            str | None: The result item identifier (e.g., "mymod:stone_block"),
                or None if no valid result ID is found.

        Example:
            Getting result ID from different recipe formats::

                # String result format
                recipe1 = RecipeJson({"type": "minecraft:smelting", "result": "minecraft:iron_ingot"})
                print(recipe1.result_id)  # "minecraft:iron_ingot"

                # Dictionary result format (1.21+)
                recipe2 = RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "result": {"id": "mymod:custom_item", "count": 2}
                })
                print(recipe2.result_id)  # "mymod:custom_item"

                # Dictionary result format (pre-1.21)
                recipe3 = RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "result": {"item": "mymod:legacy_item", "count": 1}
                })
                print(recipe3.result_id)  # "mymod:legacy_item"
        """
        res = self.data.get("result")
        if res is None:
            return None

        # Handle string results
        if isinstance(res, str):
            return res

        # Handle dict results
        if isinstance(res, dict):
            # 1.21+: "id"; pre-1.21 uses "item" – support either
            # Only return string values
            result_id = res.get("id")
            if isinstance(result_id, str):
                return result_id

            result_item = res.get("item")
            if isinstance(result_item, str):
                return result_item

            return None

        # Handle other types (numbers, booleans, etc.) - return None
        return None

    def get_result_id(self) -> str | None:
        """Get the result ID from the recipe.

        This is an alias for the result_id property, provided for backward
        compatibility and explicit method-style access.

        Returns:
            str | None: The result item identifier, or None if not found.

        Example:
            Using the method-style accessor::

                recipe = RecipeJson({"type": "minecraft:smelting", "result": "minecraft:iron_ingot"})
                result = recipe.get_result_id()  # "minecraft:iron_ingot"
        """
        return self.result_id
