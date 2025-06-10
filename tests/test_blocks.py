"""
Unit tests for the Block class and its components.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

import fabricpy
from fabricpy.block import Block
from fabricpy.recipejson import RecipeJson
from fabricpy import item_group


class TestBlock(unittest.TestCase):
    """Test the Block class."""

    def test_block_creation_basic(self):
        """Test creating a basic block with minimal parameters."""
        block = Block(
            id="testmod:basic_block",
            name="Basic Test Block"
        )
        
        self.assertEqual(block.id, "testmod:basic_block")
        self.assertEqual(block.name, "Basic Test Block")
        self.assertEqual(block.max_stack_size, 64)  # default
        self.assertIsNone(block.block_texture_path)  # default
        self.assertIsNone(block.inventory_texture_path)  # default
        self.assertIsNone(block.recipe)  # default
        self.assertIsNone(block.item_group)  # default

    def test_block_creation_full_parameters(self):
        """Test creating a block with all parameters."""
        recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["###", "###", "###"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "testmod:test_block", "count": 1}
        })
        
        block = Block(
            id="testmod:test_block",
            name="Test Block",
            max_stack_size=64,
            block_texture_path="textures/blocks/test_block.png",
            inventory_texture_path="textures/items/test_block.png",
            recipe=recipe,
            item_group=item_group.BUILDING_BLOCKS
        )
        
        self.assertEqual(block.id, "testmod:test_block")
        self.assertEqual(block.name, "Test Block")
        self.assertEqual(block.max_stack_size, 64)
        self.assertEqual(block.block_texture_path, "textures/blocks/test_block.png")
        self.assertEqual(block.inventory_texture_path, "textures/items/test_block.png")
        self.assertEqual(block.recipe, recipe)
        self.assertEqual(block.item_group, item_group.BUILDING_BLOCKS)

    def test_block_texture_fallback(self):
        """Test that inventory texture falls back to block texture."""
        block = Block(
            id="testmod:fallback_block",
            name="Fallback Block",
            block_texture_path="textures/blocks/fallback.png"
            # No inventory_texture_path specified
        )
        
        self.assertEqual(block.block_texture_path, "textures/blocks/fallback.png")
        self.assertEqual(block.inventory_texture_path, "textures/blocks/fallback.png")

    def test_block_explicit_inventory_texture(self):
        """Test block with explicit inventory texture."""
        block = Block(
            id="testmod:different_textures",
            name="Different Textures Block",
            block_texture_path="textures/blocks/placed.png",
            inventory_texture_path="textures/items/inventory.png"
        )
        
        self.assertEqual(block.block_texture_path, "textures/blocks/placed.png")
        self.assertEqual(block.inventory_texture_path, "textures/items/inventory.png")

    def test_block_namespaced_id(self):
        """Test blocks with different namespace formats."""
        # With namespace
        block1 = Block(id="mymod:example_block", name="Example Block")
        self.assertEqual(block1.id, "mymod:example_block")
        
        # Without namespace (should still work)
        block2 = Block(id="example_block", name="Example Block")
        self.assertEqual(block2.id, "example_block")

    def test_block_with_custom_item_group(self):
        """Test block with custom ItemGroup."""
        custom_group = fabricpy.ItemGroup(id="building_materials", name="Building Materials")
        
        block = Block(
            id="testmod:grouped_block",
            name="Grouped Block",
            item_group=custom_group
        )
        
        self.assertEqual(block.item_group, custom_group)

    def test_block_edge_cases(self):
        """Test edge cases for block creation."""
        # Block with no texture paths
        no_texture_block = Block(
            id="testmod:no_texture",
            name="No Texture Block"
        )
        self.assertIsNone(no_texture_block.block_texture_path)
        self.assertIsNone(no_texture_block.inventory_texture_path)
        
        # Block with very long name
        long_name = "B" * 100
        block = Block(id="testmod:long_name_block", name=long_name)
        self.assertEqual(block.name, long_name)

    def test_block_with_complex_recipe(self):
        """Test block with a complex crafting recipe."""
        recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "ABA",
                "CDC",
                "ABA"
            ],
            "key": {
                "A": "minecraft:iron_ingot",
                "B": "minecraft:diamond",
                "C": "minecraft:redstone",
                "D": "minecraft:gold_ingot"
            },
            "result": {
                "id": "testmod:advanced_block",
                "count": 1
            }
        })
        
        advanced_block = Block(
            id="testmod:advanced_block",
            name="Advanced Block",
            recipe=recipe,
            item_group=item_group.REDSTONE
        )
        
        self.assertEqual(advanced_block.recipe, recipe)
        self.assertEqual(advanced_block.item_group, item_group.REDSTONE)


if __name__ == '__main__':
    unittest.main()
