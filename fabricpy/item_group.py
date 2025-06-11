# fabricpy/item_group.py
"""Vanilla creative tab identifiers for Minecraft Fabric mods.

This module provides string constants for all vanilla Minecraft creative tabs
(ItemGroups). These constants match the names used in net.minecraft.item.ItemGroups
and can be used when assigning items and blocks to creative tabs.

The constants provided here represent the standard creative tabs available in
vanilla Minecraft. For custom creative tabs, use the ItemGroup class instead.

Example:
    Assigning an item to a vanilla creative tab::

        import fabricpy

        item = fabricpy.Item(
            id="mymod:copper_sword",
            name="Copper Sword",
            item_group=fabricpy.item_group.COMBAT
        )

        block = fabricpy.Block(
            id="mymod:marble_block",
            name="Marble Block",
            item_group=fabricpy.item_group.BUILDING_BLOCKS
        )

Attributes:
    BUILDING_BLOCKS (str): Building blocks and construction materials.
    NATURAL (str): Natural blocks like stone, dirt, and ores.
    FUNCTIONAL (str): Functional blocks like crafting tables and furnaces.
    REDSTONE (str): Redstone components and mechanisms.
    TOOLS (str): Tools and utility items.
    COMBAT (str): Weapons, armor, and combat-related items.
    FOOD_AND_DRINK (str): Food items and potions.
    INGREDIENTS (str): Crafting ingredients and materials.
    SPAWN_EGGS (str): Spawn eggs for entities.
"""

BUILDING_BLOCKS = "BUILDING_BLOCKS"
"""str: Creative tab for building blocks and construction materials."""

NATURAL = "NATURAL"
"""str: Creative tab for natural blocks like stone, dirt, and ores."""

FUNCTIONAL = "FUNCTIONAL"
"""str: Creative tab for functional blocks like crafting tables and furnaces."""

REDSTONE = "REDSTONE"
"""str: Creative tab for redstone components and mechanisms."""

TOOLS = "TOOLS"
"""str: Creative tab for tools and utility items."""

COMBAT = "COMBAT"
"""str: Creative tab for weapons, armor, and combat-related items."""

FOOD_AND_DRINK = "FOOD_AND_DRINK"
"""str: Creative tab for food items and potions."""

INGREDIENTS = "INGREDIENTS"
"""str: Creative tab for crafting ingredients and materials."""

SPAWN_EGGS = "SPAWN_EGGS"
"""str: Creative tab for spawn eggs for entities."""
