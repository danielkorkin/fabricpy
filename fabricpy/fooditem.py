# fabricpy/fooditem.py
from .item import Item


class FoodItem(Item):
    """
    Edible item helper.

    Attributes
    ----------
    nutrition : int
        Hunger points restored.
    saturation : float
        Saturation modifier.
    always_edible : bool
        Eat even when full hunger.
    """

    def __init__(
        self,
        id=None,
        name=None,
        max_stack_size=64,
        texture_path=None,
        nutrition=0,
        saturation=0.0,
        always_edible=False,
    ):
        super().__init__(id, name, max_stack_size, texture_path)
        self.nutrition = nutrition
        self.saturation = saturation
        self.always_edible = always_edible
