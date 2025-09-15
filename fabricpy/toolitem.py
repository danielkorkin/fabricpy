# fabricpy/toolitem.py
"""Tool item registration and definition for Fabric mods.

This module provides the ToolItem class, which extends the base Item class
with tool-specific properties such as durability and mining characteristics.
"""

from .item import Item


class ToolItem(Item):
    """Represents a tool item in a Fabric mod.

    ToolItem extends the base :class:`~fabricpy.item.Item` class to add
    properties relevant to tools and weapons, including durability,
    mining speed, attack damage, mining level, enchantability and a
    repair ingredient.

    Args:
        id: The registry identifier for the tool item (e.g.,
            ``"mymod:obsidian_pickaxe"``). If ``None``, must be set
            before compilation.
        name: The display name for the tool item shown in-game. If
            ``None``, must be set before compilation.
        max_stack_size: Maximum number of items that can be stacked
            together. Defaults to ``1`` for tools.
        texture_path: Path to the item's texture file relative to mod
            resources. If ``None``, a default texture will be used.
        durability: Number of uses before the tool breaks. Defaults to ``0``.
        mining_speed_multiplier: Speed multiplier when mining blocks.
            Defaults to ``1.0``.
        attack_damage: Damage dealt when used as a weapon. Defaults to ``1.0``.
        mining_level: Mining level of the tool. Defaults to ``0``.
        enchantability: How easily the tool can receive enchantments.
            Defaults to ``0``.
        repair_ingredient: Item ID used to repair the tool. Defaults to ``None``.
        recipe: Recipe definition for crafting this tool item. Can be a
            :class:`~fabricpy.recipejson.RecipeJson` instance or ``None`` for
            no recipe.
        item_group: Creative tab to place this item in. Can be an
            :class:`~fabricpy.itemgroup.ItemGroup` instance, a string constant
            from :mod:`fabricpy.item_group`, or ``None``.

    Attributes:
        durability (int): Number of uses before the tool breaks.
        mining_speed_multiplier (float): Speed multiplier when mining blocks.
        attack_damage (float): Damage dealt when used as a weapon.
        mining_level (int): Mining tier of the tool (e.g., 0 for wooden).
        enchantability (int): Likelihood of receiving better enchantments.
        repair_ingredient (str | None): Item ID used to repair the tool.

    Example:
        Creating a ruby pickaxe::

            pickaxe = ToolItem(
                id="mymod:ruby_pickaxe",
                name="Ruby Pickaxe",
                durability=500,
                mining_speed_multiplier=8.0,
                attack_damage=3.0,
                mining_level=2,
                enchantability=22,
                repair_ingredient="minecraft:ruby",
            )
    """

    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        max_stack_size: int = 1,
        texture_path: str | None = None,
        durability: int = 0,
        mining_speed_multiplier: float = 1.0,
        attack_damage: float = 1.0,
        mining_level: int = 0,
        enchantability: int = 0,
        repair_ingredient: str | None = None,
        recipe: object | None = None,
        item_group: object | str | None = None,
    ):
        """Initialize a new :class:`ToolItem` instance."""
        super().__init__(
            id=id,
            name=name,
            max_stack_size=max_stack_size,
            texture_path=texture_path,
            recipe=recipe,
            item_group=item_group,
        )
        self.durability = durability
        self.mining_speed_multiplier = mining_speed_multiplier
        self.attack_damage = attack_damage
        self.mining_level = mining_level
        self.enchantability = enchantability
        self.repair_ingredient = repair_ingredient
