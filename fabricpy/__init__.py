# fabricpy/__init__.py
"""
fabricpy – a lightweight helper library for writing Fabric mods in Python.

Public API
----------
ModConfig    – configure and compile a mod project
Item         – base class for simple items
FoodItem     – edible item helper
Block        – block helper
ItemGroup    – helper for custom creative‑inventory tabs
item_group   – constants for vanilla tabs
"""

from .modconfig import ModConfig
from .item import Item
from .fooditem import FoodItem
from .block import Block
from .itemgroup import ItemGroup
from . import item_group

__all__ = [
    "ModConfig",
    "Item",
    "FoodItem",
    "Block",
    "ItemGroup",
    "item_group",
]
