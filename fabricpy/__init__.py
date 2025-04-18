# fabricpy/__init__.py
"""
fabricpy – a lightweight helper library for making Fabric mods in Python.

Public API
----------
ModConfig   – configure and compile a mod project
Item        – base class for simple items
FoodItem    – edible item helper
Block       – block helper
item_group  – creative‑tab constants
"""

from .modconfig import ModConfig
from .item import Item
from .fooditem import FoodItem
from .block import Block
from . import item_group

__all__ = ["ModConfig", "Item", "FoodItem", "Block", "item_group"]
