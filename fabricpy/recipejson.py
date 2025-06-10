# fabricpy/recipejson.py
"""
Lightweight wrapper for recipe JSON.

Holds a validated `dict` representation and the original string so the
exact text can be written back to disk unchanged.
"""

from __future__ import annotations
import json
from typing import Any


class RecipeJson:
    def __init__(self, src: str | dict[str, Any]):
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
        """Return the result identifier if present (used to name the .json file)."""
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
        """Get the result ID from the recipe. Handles both string and dict results."""
        return self.result_id
