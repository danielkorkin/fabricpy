# fabricpy/recipejson.py  (NEW)
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

        # minimal sanity-check – make sure the mandatory “type” key exists
        if "type" not in self.data:
            raise ValueError("Recipe JSON must contain a 'type' field")

    # convenience helpers ------------------------------------------------
    @property
    def result_id(self) -> str | None:
        """Return the result identifier if present (used to name the .json file)."""
        res = self.data.get("result", {})
        # 1.21+: “id”; pre-1.21 uses “item” – support either
        return res.get("id") or res.get("item")
