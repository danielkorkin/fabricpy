"""Example demonstrating loot table usage with blocks.

Shows common loot table patterns including self-drops, ore-style
fortune drops, silk-touch behaviour, and entity loot tables.
"""

import fabricpy

# Configure the mod
mod = fabricpy.ModConfig(
    mod_id="example_loot",
    name="Example Loot Tables",
    version="1.0.0",
    description="Demonstrates LootTable usage",
    authors=["Example Dev"],
)

# ── 1. Block that drops itself ──────────────────────────────────────── #

ruby_block = fabricpy.Block(
    id="example_loot:ruby_block",
    name="Ruby Block",
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_self("example_loot:ruby_block"),
    tool_type="pickaxe",
)
mod.registerBlock(ruby_block)

# ── 2. Ore with fortune-affected drops ──────────────────────────────── #

ruby_ore = fabricpy.Block(
    id="example_loot:ruby_ore",
    name="Ruby Ore",
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_with_fortune(
        "example_loot:ruby_ore",
        "minecraft:diamond",  # use a vanilla item that exists
        min_count=1,
        max_count=2,
    ),
    tool_type="pickaxe",
)
mod.registerBlock(ruby_ore)

# ── 3. Glass-style silk-touch-only block ────────────────────────────── #

crystal_glass = fabricpy.Block(
    id="example_loot:crystal_glass",
    name="Crystal Glass",
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_with_silk_touch("example_loot:crystal_glass"),
    tool_type="pickaxe",
)
mod.registerBlock(crystal_glass)

# ── 4. Block that drops a different item ────────────────────────────── #

clay_block = fabricpy.Block(
    id="example_loot:clay_block",
    name="Clay Block",
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_item(
        "example_loot:clay_block",
        "minecraft:clay_ball",  # use the vanilla clay ball item
        min_count=2,
        max_count=4,
    ),
    tool_type="shovel",
)
mod.registerBlock(clay_block)

# ── 5. Block that drops nothing ─────────────────────────────────────── #

infested_block = fabricpy.Block(
    id="example_loot:infested_stone",
    name="Infested Stone",
    item_group=fabricpy.item_group.NATURAL,
    loot_table=fabricpy.LootTable.drops_nothing(),
)
mod.registerBlock(infested_block)

# ── 6. Entity loot table using the pool builder ─────────────────────── #

zombie_loot = fabricpy.LootTable.entity(
    [
        fabricpy.LootPool()
        .rolls(1)
        .entry("minecraft:bone", weight=3)
        .entry("minecraft:spider_eye", weight=1)
        .condition({"condition": "minecraft:survives_explosion"})
    ]
)
mod.registerLootTable("custom_zombie", zombie_loot)

# ── 7. Chest loot table with random rolls ───────────────────────────── #

dungeon_chest = fabricpy.LootTable.chest(
    [
        fabricpy.LootPool()
        .rolls({"type": "minecraft:uniform", "min": 2, "max": 5})
        .entry("minecraft:gold_ingot", weight=5)
        .entry("minecraft:diamond", weight=1)
        .entry("minecraft:iron_ingot", weight=10)
    ]
)
mod.registerLootTable("dungeon_chest", dungeon_chest)

# Compile the mod
# mod.compile()
# mod.run()  # optional: launch a dev client
