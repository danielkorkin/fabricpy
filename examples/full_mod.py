"""Full mod example — a complete "Ruby" content mod.

Ties together every fabricpy feature into one cohesive mod:

* Custom creative tab
* Raw material item + gem item
* Tool items (pickaxe and sword)
* Food items (raw + cooked via smelting recipe)
* Ore block with fortune-affected loot and mining configuration
* Deepslate ore variant (harder, same mining level)
* Multi-tool ore with per-tool mining speed overrides
* Storage block with shaped crafting recipe and self-drop loot
* Glass-style decorative block with silk-touch loot
* Interactive block with click events
* Entity loot table registered standalone

This script is intended as a reference for real mods.
"""

import fabricpy
from fabricpy.message import send_message

# ── Mod setup ────────────────────────────────────────────────────────── #

mod = fabricpy.ModConfig(
    mod_id="ruby_mod",
    name="Ruby Mod",
    version="1.0.0",
    description="A complete content mod adding ruby items, tools, and blocks",
    authors=["Example Dev"],
    project_dir="ruby-mod-output",
)

# ── Custom creative tab ─────────────────────────────────────────────── #

ruby_tab = fabricpy.ItemGroup(id="ruby_items", name="Ruby")

# ── Items ────────────────────────────────────────────────────────────── #

ruby = fabricpy.Item(
    id="ruby_mod:ruby",
    name="Ruby",
    item_group=ruby_tab,
)
mod.registerItem(ruby)

raw_ruby = fabricpy.Item(
    id="ruby_mod:raw_ruby",
    name="Raw Ruby",
    item_group=ruby_tab,
)
mod.registerItem(raw_ruby)

# ── Tools ────────────────────────────────────────────────────────────── #

ruby_pickaxe = fabricpy.ToolItem(
    id="ruby_mod:ruby_pickaxe",
    name="Ruby Pickaxe",
    durability=750,
    mining_speed_multiplier=8.0,
    attack_damage=3.0,
    mining_level=2,
    enchantability=22,
    repair_ingredient="ruby_mod:ruby",
    recipe=fabricpy.RecipeJson(
        {
            "type": "minecraft:crafting_shaped",
            "pattern": ["RRR", " S ", " S "],
            "key": {
                "R": "ruby_mod:ruby",
                "S": "minecraft:stick",
            },
            "result": {"id": "ruby_mod:ruby_pickaxe", "count": 1},
        }
    ),
    item_group=fabricpy.item_group.TOOLS,
)
mod.registerItem(ruby_pickaxe)

ruby_sword = fabricpy.ToolItem(
    id="ruby_mod:ruby_sword",
    name="Ruby Sword",
    durability=500,
    attack_damage=7.0,
    enchantability=22,
    repair_ingredient="ruby_mod:ruby",
    recipe=fabricpy.RecipeJson(
        {
            "type": "minecraft:crafting_shaped",
            "pattern": [" R ", " R ", " S "],
            "key": {
                "R": "ruby_mod:ruby",
                "S": "minecraft:stick",
            },
            "result": {"id": "ruby_mod:ruby_sword", "count": 1},
        }
    ),
    item_group=fabricpy.item_group.COMBAT,
)
mod.registerItem(ruby_sword)

# ── Food ─────────────────────────────────────────────────────────────── #

raw_ruby_apple = fabricpy.FoodItem(
    id="ruby_mod:raw_ruby_apple",
    name="Raw Ruby Apple",
    nutrition=3,
    saturation=1.5,
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(raw_ruby_apple)

cooked_ruby_apple = fabricpy.FoodItem(
    id="ruby_mod:cooked_ruby_apple",
    name="Cooked Ruby Apple",
    nutrition=8,
    saturation=12.0,
    always_edible=True,
    recipe=fabricpy.RecipeJson(
        {
            "type": "minecraft:smelting",
            "ingredient": "ruby_mod:raw_ruby_apple",
            "result": {"id": "ruby_mod:cooked_ruby_apple", "count": 1},
            "experience": 0.35,
            "cookingtime": 200,
        }
    ),
    item_group=fabricpy.item_group.FOOD_AND_DRINK,
)
mod.registerFoodItem(cooked_ruby_apple)

# ── Blocks ───────────────────────────────────────────────────────────── #

# Ore — drops raw ruby with fortune, or itself with silk touch
ruby_ore = fabricpy.Block(
    id="ruby_mod:ruby_ore",
    name="Ruby Ore",
    hardness=3.0,
    resistance=3.0,
    tool_type="pickaxe",
    mining_level="iron",
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_with_fortune(
        "ruby_mod:ruby_ore",
        "ruby_mod:raw_ruby",
        min_count=1,
        max_count=3,
    ),
)
mod.registerBlock(ruby_ore)

# Deepslate ore variant — harder and requires iron
deepslate_ruby_ore = fabricpy.Block(
    id="ruby_mod:deepslate_ruby_ore",
    name="Deepslate Ruby Ore",
    hardness=4.5,
    resistance=3.0,
    tool_type="pickaxe",
    mining_level="iron",
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_with_fortune(
        "ruby_mod:deepslate_ruby_ore",
        "ruby_mod:raw_ruby",
        min_count=1,
        max_count=3,
    ),
)
mod.registerBlock(deepslate_ruby_ore)

# Multi-tool ore — per-tool speed overrides, stone tier
mixed_ruby_ore = fabricpy.Block(
    id="ruby_mod:mixed_ruby_ore",
    name="Mixed Ruby Ore",
    hardness=4.0,
    resistance=4.0,
    requires_tool=True,
    mining_level="stone",
    mining_speeds={
        "pickaxe": 8.0,  # fastest
        "shovel": 3.0,  # slower but still works
    },
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_self("ruby_mod:mixed_ruby_ore"),
)
mod.registerBlock(mixed_ruby_ore)

# Storage block — craft 9 rubies into a block, drops itself
ruby_block = fabricpy.Block(
    id="ruby_mod:ruby_block",
    name="Block of Ruby",
    recipe=fabricpy.RecipeJson(
        {
            "type": "minecraft:crafting_shaped",
            "pattern": ["RRR", "RRR", "RRR"],
            "key": {"R": "ruby_mod:ruby"},
            "result": {"id": "ruby_mod:ruby_block", "count": 1},
        }
    ),
    item_group=ruby_tab,
    loot_table=fabricpy.LootTable.drops_self("ruby_mod:ruby_block"),
)
mod.registerBlock(ruby_block)

# Decorative glass — only drops with silk touch
ruby_glass = fabricpy.Block(
    id="ruby_mod:ruby_glass",
    name="Ruby Glass",
    item_group=ruby_tab,
    loot_table=fabricpy.LootTable.drops_with_silk_touch("ruby_mod:ruby_glass"),
)
mod.registerBlock(ruby_glass)


# Interactive altar block
class RubyAltar(fabricpy.Block):
    """An altar that reacts to player interaction and destruction."""

    def __init__(self):
        super().__init__(
            id="ruby_mod:ruby_altar",
            name="Ruby Altar",
            item_group=ruby_tab,
            loot_table=fabricpy.LootTable.drops_self("ruby_mod:ruby_altar"),
        )

    def on_right_click(self):
        return send_message("The altar hums with energy...")

    def on_left_click(self):
        return send_message("The altar resists your blow!")

    def on_break(self):
        return send_message("The altar crumbles and its energy fades...")


altar = RubyAltar()
mod.registerBlock(altar)

# ── Standalone loot tables ──────────────────────────────────────────── #

# Ruby golem entity drops
ruby_golem_loot = fabricpy.LootTable.entity(
    [
        fabricpy.LootPool()
        .rolls(1)
        .entry("ruby_mod:ruby", weight=5)
        .entry("ruby_mod:raw_ruby", weight=3),
        fabricpy.LootPool()
        .rolls({"type": "minecraft:uniform", "min": 0, "max": 2})
        .entry("ruby_mod:ruby_block", weight=1),
    ]
)
mod.registerLootTable("ruby_golem", ruby_golem_loot)

# Decompose block back into rubies (shapeless)
ruby_decompose = fabricpy.Item(
    id="ruby_mod:ruby_from_block",
    name="Ruby (from block)",
    recipe=fabricpy.RecipeJson(
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": ["ruby_mod:ruby_block"],
            "result": {"id": "ruby_mod:ruby", "count": 9},
        }
    ),
    item_group=ruby_tab,
)
mod.registerItem(ruby_decompose)

# Smelt raw ruby into gem
raw_ruby_smelt = fabricpy.RecipeJson(
    {
        "type": "minecraft:smelting",
        "ingredient": "ruby_mod:raw_ruby",
        "result": {"id": "ruby_mod:ruby", "count": 1},
        "experience": 1.0,
        "cookingtime": 200,
    }
)
# Attach smelting recipe to the raw ruby item
raw_ruby.recipe = raw_ruby_smelt

# ── Compile ──────────────────────────────────────────────────────────── #

# Uncomment to generate the mod project:
# mod.compile()
# mod.run()
