# fabricpy/item.py
class Item:
    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        max_stack_size: int = 64,
        texture_path: str | None = None,
        recipe: object | None = None,  # instance of RecipeJson or None
        item_group: object | str | None = None,
    ):
        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.texture_path = texture_path
        self.recipe = recipe
        self.item_group = item_group
