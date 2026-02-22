"""Example demonstrating FoodItem creation with recipes.

Shows how to create food items with varying nutrition, saturation,
always-edible behaviour, and crafting recipes.
"""

import fabricpy

mod = fabricpy.ModConfig(
    mod_id="food_mod",
    name="Food Mod",
    version="1.0.0",
    description="Demonstrates FoodItem usage",
    authors=["Example Dev"],
)

# ── 1. Simple food ──────────────────────────────────────────────────── #

honey_bread = fabricpy.FoodItem(
    id="food_mod:honey_bread",
    name="Honey Bread",
    nutrition=7,
    saturation=8.0,
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(honey_bread)

# ── 2. Always-edible snack (can eat even when full) ─────────────────── #

magic_berry = fabricpy.FoodItem(
    id="food_mod:magic_berry",
    name="Magic Berry",
    nutrition=2,
    saturation=1.0,
    always_edible=True,
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(magic_berry)

# ── 3. Food with a crafting recipe ──────────────────────────────────── #

golden_carrot_recipe = fabricpy.RecipeJson(
    {
        "type": "minecraft:crafting_shaped",
        "pattern": ["GGG", "GCG", "GGG"],
        "key": {
            "G": "minecraft:gold_nugget",
            "C": "minecraft:carrot",
        },
        "result": {"id": "food_mod:super_golden_carrot", "count": 1},
    }
)

super_golden_carrot = fabricpy.FoodItem(
    id="food_mod:super_golden_carrot",
    name="Super Golden Carrot",
    nutrition=10,
    saturation=14.4,
    always_edible=True,
    recipe=golden_carrot_recipe,
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(super_golden_carrot)

# ── 4. Food with a smelting recipe (cooked item) ───────────────────── #

raw_venison = fabricpy.FoodItem(
    id="food_mod:raw_venison",
    name="Raw Venison",
    nutrition=3,
    saturation=1.8,
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(raw_venison)

cooked_venison_recipe = fabricpy.RecipeJson(
    {
        "type": "minecraft:smelting",
        "ingredient": "food_mod:raw_venison",
        "result": {"id": "food_mod:cooked_venison", "count": 1},
        "experience": 0.35,
        "cookingtime": 200,
    }
)

cooked_venison = fabricpy.FoodItem(
    id="food_mod:cooked_venison",
    name="Cooked Venison",
    nutrition=8,
    saturation=12.8,
    recipe=cooked_venison_recipe,
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(cooked_venison)

# ── 5. Low-stack gourmet food ──────────────────────────────────────── #

feast_platter = fabricpy.FoodItem(
    id="food_mod:feast_platter",
    name="Feast Platter",
    nutrition=20,
    saturation=20.0,
    max_stack_size=1,
    always_edible=True,
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(feast_platter)

# Compile the mod
# mod.compile()
# mod.run()  # optional: launch a dev client
