# fabricpy/__init__.py
"""
fabricpy – a lightweight helper library for writing Fabric mods in Python.
"""

from .modconfig import ModConfig
from .item import Item
from .fooditem import FoodItem
from .block import Block
from .itemgroup import ItemGroup
from .recipejson import RecipeJson  # ← NEW import
from . import item_group

__all__ = [
    "ModConfig",
    "Item",
    "FoodItem",
    "Block",
    "ItemGroup",
    "RecipeJson",  # ← expose
    "item_group",
]
