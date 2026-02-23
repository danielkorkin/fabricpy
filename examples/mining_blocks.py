"""Example demonstrating block mining configuration.

Shows how to use the mining-related Block properties:

* ``hardness`` / ``resistance`` — control break time and blast durability
* ``tool_type`` — which tool mines the block efficiently
* ``mining_level`` — minimum tool tier (stone / iron / diamond)
* ``requires_tool`` — whether the correct tool is needed for drops
* ``mining_speeds`` — per-tool-type speed overrides
"""

import fabricpy

mod = fabricpy.ModConfig(
    mod_id="mining_demo",
    name="Mining Demo",
    version="1.0.0",
    description="Demonstrates mining configuration",
    authors=["Example Dev"],
)

# ── 0. Ruby item — the drop for ruby ore ────────────────────────────── #

ruby = fabricpy.Item(
    id="mining_demo:ruby",
    name="Ruby",
    item_group=fabricpy.item_group.INGREDIENTS,
)
mod.registerItem(ruby)

# ── 1. Simple ore — pickaxe required, iron tier ─────────────────────── #

ruby_ore = fabricpy.Block(
    id="mining_demo:ruby_ore",
    name="Ruby Ore",
    hardness=3.0,
    resistance=3.0,
    tool_type="pickaxe",
    mining_level="iron",  # needs at least an iron pickaxe
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_with_fortune(
        "mining_demo:ruby_ore",
        "mining_demo:ruby",
        min_count=1,
        max_count=3,
    ),
)
mod.registerBlock(ruby_ore)

# ── 2. Tough block — high hardness, diamond tier ────────────────────── #

reinforced_block = fabricpy.Block(
    id="mining_demo:reinforced_block",
    name="Reinforced Block",
    hardness=25.0,  # very slow to mine
    resistance=600.0,  # survives most explosions
    tool_type="pickaxe",
    mining_level="diamond",
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_self("mining_demo:reinforced_block"),
)
mod.registerBlock(reinforced_block)

# ── 3. Multi-tool block — mineable efficiently by multiple tools ─────── #

mixed_ore = fabricpy.Block(
    id="mining_demo:mixed_ore",
    name="Mixed Ore",
    hardness=4.0,
    resistance=4.0,
    mining_level="stone",
    requires_tool=True,
    mining_speeds={  # pickaxe is fastest, shovel also works
        "pickaxe": 8.0,
        "shovel": 3.0,
    },
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_self("mining_demo:mixed_ore"),
)
mod.registerBlock(mixed_ore)

# ── 4. Soft block — no tool required, breaks quickly ────────────────── #

soft_block = fabricpy.Block(
    id="mining_demo:soft_block",
    name="Soft Block",
    hardness=0.5,
    resistance=0.5,
    # No tool_type → any tool works, drops always
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_self("mining_demo:soft_block"),
)
mod.registerBlock(soft_block)

# ── 5. Shovel block with per-tool overrides ──────────────────────────── #

gravel_ore = fabricpy.Block(
    id="mining_demo:gravel_ore",
    name="Gravel Ore",
    hardness=1.0,
    resistance=1.0,
    tool_type="shovel",
    mining_speeds={
        "shovel": 6.0,
        "pickaxe": 1.5,  # pickaxe marginally helps
    },
    item_group=fabricpy.item_group.NATURAL,
)
mod.registerBlock(gravel_ore)

# ── Compile ──────────────────────────────────────────────────────────── #

# Uncomment to generate the mod project:
mod.compile()
mod.run()  # optional: launch a dev client with the mod loaded
