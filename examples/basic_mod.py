"""Beginner example — create a simple mod with one item and one block.

This is the smallest useful mod you can build with fabricpy.  It registers
a single item and a single block, then compiles the project.  Run this
script and you will have a fully buildable Fabric mod in the output
directory.
"""

import fabricpy

# 1. Create the mod configuration ──────────────────────────────────────
mod = fabricpy.ModConfig(
    mod_id="basic_mod",
    name="Basic Mod",
    version="1.0.0",
    description="A minimal fabricpy example",
    authors=["Your Name"],
    project_dir="basic-mod-output",
)

# 2. Register a simple item ───────────────────────────────────────────
gem = fabricpy.Item(
    id="basic_mod:ruby",
    name="Ruby",
    max_stack_size=64,
    item_group=fabricpy.item_group.INGREDIENTS,
)
mod.registerItem(gem)

# 3. Register a simple block ──────────────────────────────────────────
block = fabricpy.Block(
    id="basic_mod:ruby_block",
    name="Ruby Block",
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_self("basic_mod:ruby_block"),
)
mod.registerBlock(block)

# 4. Compile — generates a complete Fabric mod project ─────────────────
# mod.compile()
# mod.run()     # optional: launch a dev client
