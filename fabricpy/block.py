class Block:
    def __init__(
        self,
        id=None,
        name=None,
        max_stack_size=64,
        block_texture_path=None,
        inventory_texture_path=None,
    ):
        """
        Base block class.
        :param id: The block identifier (used in registration and asset file names).
        :param name: The display name of the block.
        :param max_stack_size: The maximum number of items per stack (for the block’s BlockItem).
        :param block_texture_path: The local filesystem path to the block texture.
        :param inventory_texture_path: The local filesystem path for the inventory icon.
                                       Defaults to block_texture_path if not provided.
        """
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.block_texture_path = block_texture_path
        self.inventory_texture_path = (
            inventory_texture_path
            if inventory_texture_path is not None
            else block_texture_path
        )
        # Optional: the creative item group to which the block (as a BlockItem) should belong.
        self.item_group = None
