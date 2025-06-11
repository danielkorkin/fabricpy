# fabricpy/fooditem.py
"""Food item registration and definition for Fabric mods.

This module provides the FoodItem class, which extends the base Item class
to support food-specific properties like nutrition, saturation, and eating behavior.
"""

from .item import Item


class FoodItem(Item):
    """Represents a custom food item in a Fabric mod.

    FoodItem extends the base Item class to add food-specific properties
    including nutrition value, saturation, and whether the item can always
    be eaten regardless of hunger level.

    Args:
        id: The registry identifier for the food item (e.g., "mymod:golden_apple").
            If None, must be set before compilation.
        name: The display name for the food item shown in-game.
            If None, must be set before compilation.
        max_stack_size: Maximum number of items that can be stacked together.
            Defaults to 64.
        texture_path: Path to the item's texture file relative to mod resources.
            If None, a default texture will be used.
        nutrition: Number of hunger points restored when eaten (half-hearts on hunger bar).
            Defaults to 0.
        saturation: Saturation value provided when eaten. Higher values prevent
            hunger from decreasing quickly. Defaults to 0.0.
        always_edible: Whether the food can be eaten even when the player's hunger
            bar is full. Defaults to False.
        recipe: Recipe definition for crafting this food item. Can be a RecipeJson
            instance or None for no recipe.
        item_group: Creative tab to place this item in. Can be an ItemGroup
            instance, a string constant from item_group module, or None.
            Typically FOOD_AND_DRINK for food items.

    Attributes:
        nutrition (int): Hunger points restored when eaten.
        saturation (float): Saturation value provided when eaten.
        always_edible (bool): Whether the food can always be eaten.

    Example:
        Creating a basic food item::

            apple = FoodItem(
                id="mymod:golden_apple",
                name="Golden Apple",
                nutrition=4,
                saturation=9.6,
                always_edible=True,
                item_group=fabricpy.item_group.FOOD_AND_DRINK
            )

        Creating a food item with a recipe::

            recipe = RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["###", "#A#", "###"],
                "key": {
                    "#": "minecraft:gold_ingot",
                    "A": "minecraft:apple"
                },
                "result": {"id": "mymod:golden_apple", "count": 1}
            })

            apple = FoodItem(
                id="mymod:golden_apple",
                name="Golden Apple",
                nutrition=4,
                saturation=9.6,
                recipe=recipe
            )
    """

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
        """Initialize a new FoodItem instance.

        Args:
            id: The registry identifier for the food item.
            name: The display name for the food item.
            max_stack_size: Maximum number of items that can be stacked.
            texture_path: Path to the item's texture file.
            nutrition: Number of hunger points restored when eaten.
            saturation: Saturation value provided when eaten.
            always_edible: Whether the food can be eaten when hunger is full.
            recipe: Recipe definition for crafting this food item.
            item_group: Creative tab to place this item in.
        """
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
