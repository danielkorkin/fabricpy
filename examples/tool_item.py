"""Minimal example demonstrating a ToolItem."""

import fabricpy

# Configure the mod
mod = fabricpy.ModConfig(
    mod_id="example_tools",
    name="Example Tools",
    version="1.0.0",
    description="Demonstrates ToolItem usage",
    authors=["Example Dev"],
)

# Define a ruby pickaxe tool
ruby_pickaxe = fabricpy.ToolItem(
    id="example_tools:ruby_pickaxe",
    name="Ruby Pickaxe",
    durability=500,
    mining_speed_multiplier=8.0,
    attack_damage=3.0,
    mining_level=2,
    enchantability=22,
    repair_ingredient="minecraft:ruby",
    item_group=fabricpy.item_group.TOOLS,
)

# Register the tool with the mod
mod.registerItem(ruby_pickaxe)
