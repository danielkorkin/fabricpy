"""
Shared pytest fixtures for fabricpy test suite.

Provides reusable mod configurations, temporary directories,
and helper utilities for testing Fabric mod generation.
"""

import os
import shutil

import pytest

from fabricpy import (
    Block,
    FoodItem,
    Item,
    ItemGroup,
    ModConfig,
    RecipeJson,
    ToolItem,
    item_group,
)


@pytest.fixture
def sample_recipe():
    """A basic shaped crafting recipe."""
    return RecipeJson(
        {
            "type": "minecraft:crafting_shaped",
            "pattern": ["###", "# #", "###"],
            "key": {"#": "minecraft:iron_ingot"},
            "result": {"id": "testmod:iron_ring", "count": 1},
        }
    )


@pytest.fixture
def sample_item(sample_recipe):
    """A basic item with a recipe."""
    return Item(
        id="testmod:iron_ring",
        name="Iron Ring",
        max_stack_size=16,
        recipe=sample_recipe,
        item_group=item_group.TOOLS,
    )


@pytest.fixture
def sample_food():
    """A basic food item."""
    return FoodItem(
        id="testmod:magic_apple",
        name="Magic Apple",
        nutrition=8,
        saturation=4.8,
        always_edible=True,
        item_group=item_group.FOOD_AND_DRINK,
    )


@pytest.fixture
def sample_tool():
    """A basic tool item."""
    return ToolItem(
        id="testmod:diamond_drill",
        name="Diamond Drill",
        durability=1000,
        mining_speed_multiplier=10.0,
        attack_damage=4.0,
        mining_level=3,
        enchantability=15,
        repair_ingredient="minecraft:diamond",
        item_group=item_group.TOOLS,
    )


@pytest.fixture
def sample_block():
    """A basic block."""
    return Block(
        id="testmod:marble_block",
        name="Marble Block",
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["##", "##"],
                "key": {"#": "minecraft:quartz"},
                "result": {"id": "testmod:marble_block", "count": 4},
            }
        ),
        item_group=item_group.BUILDING_BLOCKS,
    )


@pytest.fixture
def sample_item_group():
    """A custom item group."""
    return ItemGroup(id="testmod_weapons", name="Testmod Weapons")
