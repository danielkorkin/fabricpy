# fabricpy/item.py
"""Item registration and definition for Fabric mods.

This module provides the Item class for defining custom items in Minecraft Fabric mods.
Items can have custom textures, recipes, stack sizes, and be assigned to creative tabs.
"""


class Item:
    """Represents a custom item in a Fabric mod.

    The Item class handles the definition of custom items including their properties,
    textures, recipes, and creative tab assignment. Items are registered with a ModConfig
    instance and compiled into the final mod.

    Args:
        id: The registry identifier for the item (e.g., "mymod:example_item").
            If None, must be set before compilation.
        name: The display name for the item shown in-game.
            If None, must be set before compilation.
        max_stack_size: Maximum number of items that can be stacked together.
            Defaults to 64.
        texture_path: Path to the item's texture file relative to mod resources.
            If None, a default texture will be used.
        recipe: Recipe definition for crafting this item. Can be a RecipeJson
            instance or None for no recipe.
        item_group: Creative tab to place this item in. Can be an ItemGroup
            instance, a string constant from item_group module, or None.

    Attributes:
        id (str): The registry identifier for the item.
        name (str): The display name for the item.
        max_stack_size (int): Maximum stack size for the item.
        texture_path (str): Path to the item's texture file.
        recipe (RecipeJson): Recipe definition for crafting this item.
        item_group (ItemGroup | str): Creative tab assignment for the item.

    Example:
        Creating a basic item::

            item = Item(
                id="mymod:copper_sword",
                name="Copper Sword",
                max_stack_size=1,
                texture_path="textures/items/copper_sword.png",
                item_group=fabricpy.item_group.COMBAT
            )

        Creating an item with a recipe::

            recipe = RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["#", "#", "/"],
                "key": {
                    "#": "minecraft:copper_ingot",
                    "/": "minecraft:stick"
                },
                "result": {"id": "mymod:copper_sword", "count": 1}
            })

            item = Item(
                id="mymod:copper_sword",
                name="Copper Sword",
                recipe=recipe
            )
    """

    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        max_stack_size: int = 64,
        texture_path: str | None = None,
        recipe: object | None = None,  # instance of RecipeJson or None
        item_group: object | str | None = None,
    ):
        """Initialize a new Item instance.

        Args:
            id: The registry identifier for the item.
            name: The display name for the item.
            max_stack_size: Maximum number of items that can be stacked.
            texture_path: Path to the item's texture file.
            recipe: Recipe definition for crafting this item.
            item_group: Creative tab to place this item in.
        """
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.texture_path = texture_path
        self.recipe = recipe
        self.item_group = item_group
