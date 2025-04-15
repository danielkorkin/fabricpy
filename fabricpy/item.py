class Item:
    def __init__(self, id=None, name=None, max_stack_size=64, texture_path=None):
        """
        Base item class.
        :param id: The item identifier (used in registration and asset file names).
        :param name: The display name of the item.
        :param max_stack_size: The maximum number of items per stack.
        :param texture_path: The local filesystem path to the item texture.
                             This path is used both to locate the texture file and to build the in-game asset reference.
        """
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.texture_path = texture_path
