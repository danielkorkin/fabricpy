# fabricpy/block.py
class Block:
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
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.block_texture_path = block_texture_path
        # fall back to block texture if no inventory-specific texture provided
        self.inventory_texture_path = inventory_texture_path or block_texture_path
        self.recipe = recipe
        self.item_group = item_group
