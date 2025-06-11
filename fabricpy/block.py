# fabricpy/block.py
"""Block registration and definition for Fabric mods.

This module provides the Block class for defining custom blocks in Minecraft Fabric mods.
Blocks can have custom textures for both the block itself and its inventory item representation,
recipes for crafting, and creative tab assignment.
"""


class Block:
    """Represents a custom block in a Fabric mod.

    The Block class handles the definition of custom blocks including their properties,
    textures, recipes, and creative tab assignment. Blocks automatically generate
    corresponding BlockItems for inventory representation.

    Args:
        id: The registry identifier for the block (e.g., "mymod:copper_block").
            If None, must be set before compilation.
        name: The display name for the block shown in-game.
            If None, must be set before compilation.
        max_stack_size: Maximum number of block items that can be stacked together.
            Defaults to 64.
        block_texture_path: Path to the block's texture file for world rendering
            relative to mod resources. If None, a default texture will be used.
        inventory_texture_path: Path to the texture used for the block's item form
            in inventories. If None, falls back to block_texture_path.
        recipe: Recipe definition for crafting this block. Can be a RecipeJson
            instance or None for no recipe.
        item_group: Creative tab to place this block's item in. Can be an ItemGroup
            instance, a string constant from item_group module, or None.
            Typically BUILDING_BLOCKS for most blocks.

    Attributes:
        id (str): The registry identifier for the block.
        name (str): The display name for the block.
        max_stack_size (int): Maximum stack size for the block item.
        block_texture_path (str): Path to the block's world texture file.
        inventory_texture_path (str): Path to the block's inventory texture file.
        recipe (RecipeJson): Recipe definition for crafting this block.
        item_group (ItemGroup | str): Creative tab assignment for the block item.

    Example:
        Creating a basic block::

            block = Block(
                id="mymod:copper_block",
                name="Copper Block",
                block_texture_path="textures/blocks/copper_block.png",
                item_group=fabricpy.item_group.BUILDING_BLOCKS
            )

        Creating a block with separate inventory texture::

            block = Block(
                id="mymod:glowing_stone",
                name="Glowing Stone",
                block_texture_path="textures/blocks/glowing_stone.png",
                inventory_texture_path="textures/items/glowing_stone_item.png"
            )

        Creating a block with a recipe::

            recipe = RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["###", "###", "###"],
                "key": {"#": "minecraft:copper_ingot"},
                "result": {"id": "mymod:copper_block", "count": 1}
            })

            block = Block(
                id="mymod:copper_block",
                name="Copper Block",
                recipe=recipe
            )
    """

    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        max_stack_size: int = 64,
        block_texture_path: str | None = None,
        inventory_texture_path: str | None = None,
        recipe: object | None = None,  # instance of RecipeJson or None
        item_group: object | str | None = None,
    ):
        """Initialize a new Block instance.

        Args:
            id: The registry identifier for the block.
            name: The display name for the block.
            max_stack_size: Maximum number of block items that can be stacked.
            block_texture_path: Path to the block's world texture file.
            inventory_texture_path: Path to the block's inventory texture file.
                Falls back to block_texture_path if not provided.
            recipe: Recipe definition for crafting this block.
            item_group: Creative tab to place this block's item in.
        """
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.block_texture_path = block_texture_path
        # fall back to block texture if no inventory-specific texture provided
        self.inventory_texture_path = inventory_texture_path or block_texture_path
        self.recipe = recipe
        self.item_group = item_group
