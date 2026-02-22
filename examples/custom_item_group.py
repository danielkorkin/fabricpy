"""Example demonstrating custom creative tabs (ItemGroups).

Shows how to create your own creative inventory tabs and assign items
and blocks to them so players can find your content easily.
"""

import fabricpy

mod = fabricpy.ModConfig(
    mod_id="tabs_mod",
    name="Custom Tabs Mod",
    version="1.0.0",
    description="Demonstrates custom ItemGroup creation",
    authors=["Example Dev"],
)

# ── 1. Create custom creative tabs ──────────────────────────────────── #

gems_tab = fabricpy.ItemGroup(id="gems", name="Gems & Minerals")
magic_tab = fabricpy.ItemGroup(id="magic", name="Magic Items")

# ── 2. Items in the Gems tab ────────────────────────────────────────── #

ruby = fabricpy.Item(
    id="tabs_mod:ruby",
    name="Ruby",
    item_group=gems_tab,
)
mod.registerItem(ruby)

sapphire = fabricpy.Item(
    id="tabs_mod:sapphire",
    name="Sapphire",
    item_group=gems_tab,
)
mod.registerItem(sapphire)

topaz = fabricpy.Item(
    id="tabs_mod:topaz",
    name="Topaz",
    item_group=gems_tab,
)
mod.registerItem(topaz)

# Blocks also live in the Gems tab
ruby_block = fabricpy.Block(
    id="tabs_mod:ruby_block",
    name="Block of Ruby",
    item_group=gems_tab,
    loot_table=fabricpy.LootTable.drops_self("tabs_mod:ruby_block"),
)
mod.registerBlock(ruby_block)

# ── 3. Items in the Magic tab ───────────────────────────────────────── #

wand = fabricpy.Item(
    id="tabs_mod:wand",
    name="Magic Wand",
    max_stack_size=1,
    item_group=magic_tab,
)
mod.registerItem(wand)

enchanted_apple = fabricpy.FoodItem(
    id="tabs_mod:enchanted_apple",
    name="Enchanted Apple",
    nutrition=8,
    saturation=12.0,
    always_edible=True,
    item_group=magic_tab,
)
mod.registerFoodItem(enchanted_apple)

# ── 4. Mix custom and vanilla tabs ──────────────────────────────────── #

# Some items can still go into vanilla tabs
pickaxe = fabricpy.ToolItem(
    id="tabs_mod:ruby_pickaxe",
    name="Ruby Pickaxe",
    durability=750,
    mining_speed_multiplier=8.0,
    attack_damage=3.0,
    mining_level=2,
    enchantability=22,
    repair_ingredient="tabs_mod:ruby",
    item_group=fabricpy.item_group.TOOLS,  # vanilla tab
)
mod.registerItem(pickaxe)

# Compile the mod
# mod.compile()
# mod.run()  # optional: launch a dev client
