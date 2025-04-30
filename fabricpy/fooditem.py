# fabricpy/fooditem.py
from .item import Item


class FoodItem(Item):
    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        max_stack_size: int = 64,
        texture_path: str | None = None,
        nutrition: int = 0,
        saturation: float = 0.0,
        always_edible: bool = False,
        recipe: object | None = None,  # instance of RecipeJson or None
        item_group: object | str | None = None,
    ):
        super().__init__(
            id=id,
            name=name,
            max_stack_size=max_stack_size,
            texture_path=texture_path,
            recipe=recipe,
            item_group=item_group,
        )
        self.nutrition = nutrition
        self.saturation = saturation
        self.always_edible = always_edible
