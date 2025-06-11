# fabricpy/__init__.py
"""FabricPy - A lightweight helper library for writing Fabric mods in Python.

FabricPy provides a simple, Pythonic interface for creating Minecraft Fabric mods
without needing to write Java directly. It handles mod configuration, item and block
registration, recipe creation, and project compilation.

This module exposes all the main classes and utilities needed to create Fabric mods:

- ModConfig: Main configuration and compilation class
- Item/FoodItem: Item registration classes
- Block: Block registration class
- ItemGroup: Custom creative tab creation
- RecipeJson: Recipe definition helper
- item_group: Vanilla creative tab constants

Example:
    Basic mod creation::

        import fabricpy

        # Create mod configuration
        mymod = fabricpy.ModConfig(
            mod_id="mymod",
            name="My Mod",
            version="1.0.0",
            description="A simple example mod",
            authors=["Your Name"]
        )

        # Create and register an item
        item = fabricpy.Item(
            id="mymod:example_item",
            name="Example Item"
        )
        mymod.registerItem(item)

        # Compile and run
        mymod.compile()
        mymod.run()

Attributes:
    __all__ (list): List of public API symbols exported by this module.
"""

from . import item_group
from .__version__ import __version__
from .block import Block
from .fooditem import FoodItem
from .item import Item
from .itemgroup import ItemGroup
from .modconfig import ModConfig
from .recipejson import RecipeJson  # ← NEW import

__all__ = [
    "ModConfig",
    "Item",
    "FoodItem",
    "Block",
    "ItemGroup",
    "RecipeJson",  # ← expose
    "item_group",
    "__version__",
]
