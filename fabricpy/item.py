# fabricpy/item.py
class Item:
    def __init__(
        self,
        id=None,
        name=None,
        max_stack_size=64,
        texture_path=None,
        recipe=None,  # ← NEW
    ):
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.texture_path = texture_path
        self.recipe = recipe  # instance of RecipeJson | None
        self.item_group = None
