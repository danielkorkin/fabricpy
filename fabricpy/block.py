# fabricpy/block.py
class Block:
    def __init__(
        self,
        id=None,
        name=None,
        max_stack_size=64,
        block_texture_path=None,
        inventory_texture_path=None,
        recipe=None,  # ← NEW
    ):
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.block_texture_path = block_texture_path
        self.inventory_texture_path = inventory_texture_path or block_texture_path
        self.recipe = recipe
        self.item_group = None
