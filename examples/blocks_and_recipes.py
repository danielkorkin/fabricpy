"""Example demonstrating blocks with recipes, textures, and click events.

Covers shaped/shapeless crafting recipes for blocks, separate block and
inventory textures, and blocks that react to player clicks using the
message helpers.
"""

import fabricpy
from fabricpy.message import send_action_bar_message, send_message

mod = fabricpy.ModConfig(
    mod_id="blocks_mod",
    name="Blocks Mod",
    version="1.0.0",
    description="Demonstrates Block features",
    authors=["Example Dev"],
)

# ── 1. Storage block with a shaped recipe ───────────────────────────── #

ruby_block_recipe = fabricpy.RecipeJson(
    {
        "type": "minecraft:crafting_shaped",
        "pattern": ["RRR", "RRR", "RRR"],
        "key": {"R": "blocks_mod:ruby"},
        "result": {"id": "blocks_mod:ruby_block", "count": 1},
    }
)

ruby_block = fabricpy.Block(
    id="blocks_mod:ruby_block",
    name="Block of Ruby",
    recipe=ruby_block_recipe,
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_self("blocks_mod:ruby_block"),
)
mod.registerBlock(ruby_block)

# ── 2. Block with separate block and inventory textures ─────────────── #

magic_lamp = fabricpy.Block(
    id="blocks_mod:magic_lamp",
    name="Magic Lamp",
    block_texture_path="textures/blocks/magic_lamp.png",
    inventory_texture_path="textures/items/magic_lamp_item.png",
    item_group=fabricpy.item_group.FUNCTIONAL,
)
mod.registerBlock(magic_lamp)

# ── 3. Block with click events using message helpers ────────────────── #

info_block = fabricpy.Block(
    id="blocks_mod:info_block",
    name="Info Block",
    left_click_event=send_message("You punched the Info Block!"),
    right_click_event=send_action_bar_message("Right-clicked!"),
    item_group=fabricpy.item_group.REDSTONE,
)
mod.registerBlock(info_block)

# ── 4. Block with click events via subclass ─────────────────────────── #


class CounterBlock(fabricpy.Block):
    """A block that tells you when it is clicked."""

    def __init__(self):
        super().__init__(
            id="blocks_mod:counter_block",
            name="Counter Block",
            item_group=fabricpy.item_group.REDSTONE,
        )

    def on_left_click(self):
        return send_message("Counter: left click registered")

    def on_right_click(self):
        return send_action_bar_message("Counter: right click registered")


counter = CounterBlock()
mod.registerBlock(counter)

# ── 5. Block with a shapeless recipe (un-crafting) ──────────────────── #

ruby_decompose_recipe = fabricpy.RecipeJson(
    {
        "type": "minecraft:crafting_shapeless",
        "ingredients": ["blocks_mod:ruby_block"],
        "result": {"id": "blocks_mod:ruby", "count": 9},
    }
)

# The recipe is for the ruby item, but we attach it to a standalone item
ruby_item = fabricpy.Item(
    id="blocks_mod:ruby",
    name="Ruby",
    recipe=ruby_decompose_recipe,
    item_group=fabricpy.item_group.INGREDIENTS,
)
mod.registerItem(ruby_item)

# Compile the mod
# mod.compile()
# mod.run()     # optional: launch a dev client
