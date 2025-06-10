"""
Comprehensive unit tests for Block class covering all block-specific functionality.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch

import fabricpy
from fabricpy.block import Block
from fabricpy.recipejson import RecipeJson
from fabricpy import item_group


class TestBlockComprehensive(unittest.TestCase):
    """Comprehensive tests for the Block class."""

    def test_block_minimal_creation(self):
        """Test creating a block with minimal parameters."""
        block = Block(
            id="testmod:minimal_block",
            name="Minimal Block"
        )
        
        self.assertEqual(block.id, "testmod:minimal_block")
        self.assertEqual(block.name, "Minimal Block")
        self.assertEqual(block.max_stack_size, 64)
        self.assertIsNone(block.block_texture_path)
        self.assertIsNone(block.inventory_texture_path)
        self.assertIsNone(block.recipe)
        self.assertIsNone(block.item_group)

    def test_block_texture_system(self):
        """Test the block texture system and fallbacks."""
        # Block with only block texture
        block1 = Block(
            id="test:block1",
            name="Block 1",
            block_texture_path="textures/blocks/stone.png"
        )
        self.assertEqual(block1.block_texture_path, "textures/blocks/stone.png")
        self.assertEqual(block1.inventory_texture_path, "textures/blocks/stone.png")  # fallback
        
        # Block with both textures
        block2 = Block(
            id="test:block2",
            name="Block 2",
            block_texture_path="textures/blocks/wood.png",
            inventory_texture_path="textures/items/wood_item.png"
        )
        self.assertEqual(block2.block_texture_path, "textures/blocks/wood.png")
        self.assertEqual(block2.inventory_texture_path, "textures/items/wood_item.png")
        
        # Block with only inventory texture (should not fallback to None)
        block3 = Block(
            id="test:block3",
            name="Block 3",
            inventory_texture_path="textures/items/special.png"
        )
        self.assertIsNone(block3.block_texture_path)
        self.assertEqual(block3.inventory_texture_path, "textures/items/special.png")

    def test_block_various_stack_sizes(self):
        """Test blocks with various stack sizes."""
        # Single stack (like beds)
        single_block = Block(
            id="test:single",
            name="Single Block",
            max_stack_size=1
        )
        self.assertEqual(single_block.max_stack_size, 1)
        
        # Small stack (like buckets)
        small_stack = Block(
            id="test:small",
            name="Small Stack Block",
            max_stack_size=16
        )
        self.assertEqual(small_stack.max_stack_size, 16)
        
        # Default stack
        default_stack = Block(
            id="test:default",
            name="Default Block"
        )
        self.assertEqual(default_stack.max_stack_size, 64)

    def test_block_with_complex_recipes(self):
        """Test blocks with complex crafting recipes."""
        # Stone bricks recipe
        stone_brick_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": [
                "SS",
                "SS"
            ],
            "key": {
                "S": "minecraft:stone"
            },
            "result": {"id": "test:stone_bricks", "count": 4}
        })
        
        stone_bricks = Block(
            id="test:stone_bricks",
            name="Test Stone Bricks",
            block_texture_path="textures/blocks/stone_bricks.png",
            recipe=stone_brick_recipe,
            item_group=item_group.BUILDING_BLOCKS
        )
        
        self.assertEqual(stone_bricks.recipe, stone_brick_recipe)
        self.assertEqual(stone_bricks.item_group, item_group.BUILDING_BLOCKS)
        
        # Smelting recipe for glass
        glass_recipe = RecipeJson({
            "type": "minecraft:smelting",
            "ingredient": "minecraft:sand",
            "result": "test:glass",
            "experience": 0.1,
            "cookingtime": 200
        })
        
        glass = Block(
            id="test:glass",
            name="Test Glass", 
            recipe=glass_recipe
        )
        
        self.assertEqual(glass.recipe, glass_recipe)

    def test_block_with_item_groups(self):
        """Test blocks with various item groups."""
        # Building blocks
        building_block = Block(
            id="test:building",
            name="Building Block",
            item_group=item_group.BUILDING_BLOCKS
        )
        self.assertEqual(building_block.item_group, item_group.BUILDING_BLOCKS)
        
        # Decorative blocks
        decorative_block = Block(
            id="test:decorative",
            name="Decorative Block",
            item_group=item_group.BUILDING_BLOCKS  # Use available constant
        )
        self.assertEqual(decorative_block.item_group, item_group.BUILDING_BLOCKS)
        
        # Natural blocks
        natural_block = Block(
            id="test:natural",
            name="Natural Block",
            item_group=item_group.NATURAL
        )
        self.assertEqual(natural_block.item_group, item_group.NATURAL)
        
        # Custom item group
        custom_group = fabricpy.ItemGroup(id="test_blocks", name="Test Blocks")
        custom_block = Block(
            id="test:custom",
            name="Custom Block",
            item_group=custom_group
        )
        self.assertEqual(custom_block.item_group, custom_group)

    def test_block_special_cases(self):
        """Test special block cases that might exist in Minecraft."""
        # Shulker box-like (single stack)
        shulker_like = Block(
            id="test:shulker",
            name="Shulker-like Block",
            max_stack_size=1,
            block_texture_path="textures/blocks/shulker.png",
            inventory_texture_path="textures/items/shulker_item.png"
        )
        self.assertEqual(shulker_like.max_stack_size, 1)
        
        # Glass-like (different textures)
        glass_like = Block(
            id="test:glass_like",
            name="Glass-like Block",
            block_texture_path="textures/blocks/glass.png",
            inventory_texture_path="textures/items/glass_item.png"
        )
        self.assertNotEqual(glass_like.block_texture_path, glass_like.inventory_texture_path)
        
        # Torch-like (16 stack)
        torch_like = Block(
            id="test:torch",
            name="Torch-like Block",
            max_stack_size=64  # Torches are actually 64 in modern versions
        )
        self.assertEqual(torch_like.max_stack_size, 64)

    def test_block_namespacing(self):
        """Test block ID namespacing."""
        # With explicit namespace
        namespaced = Block(id="mymod:stone", name="My Stone")
        self.assertEqual(namespaced.id, "mymod:stone")
        
        # Without namespace (vanilla-style)
        vanilla_style = Block(id="custom_stone", name="Custom Stone")
        self.assertEqual(vanilla_style.id, "custom_stone")
        
        # Complex namespace
        complex_ns = Block(id="super_mod:building:reinforced_stone", name="Reinforced Stone")
        self.assertEqual(complex_ns.id, "super_mod:building:reinforced_stone")

    def test_block_with_shaped_recipes(self):
        """Test blocks with various shaped recipe patterns."""
        # 1x1 pattern
        small_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["#"],
            "key": {"#": "minecraft:stone"},
            "result": {"id": "test:compressed_stone", "count": 1}
        })
        
        # 2x2 pattern  
        medium_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["##", "##"],
            "key": {"#": "minecraft:wood"},
            "result": {"id": "test:wood_block", "count": 1}
        })
        
        # 3x3 pattern
        large_recipe = RecipeJson({
            "type": "minecraft:crafting_shaped",
            "pattern": ["###", "###", "###"],
            "key": {"#": "minecraft:iron_ingot"},
            "result": {"id": "test:iron_block", "count": 1}
        })
        
        blocks = [
            Block(id="test:compressed_stone", name="Compressed Stone", recipe=small_recipe),
            Block(id="test:wood_block", name="Wood Block", recipe=medium_recipe),
            Block(id="test:iron_block", name="Iron Block", recipe=large_recipe)
        ]
        
        for block in blocks:
            self.assertIsNotNone(block.recipe)
            self.assertIsInstance(block.recipe, RecipeJson)

    def test_block_edge_cases(self):
        """Test edge cases for block creation."""
        # Very long names
        long_name = "A" * 200
        long_block = Block(id="test:long", name=long_name)
        self.assertEqual(long_block.name, long_name)
        
        # Unicode characters in names
        unicode_block = Block(id="test:unicode", name="测试方块 🧱")
        self.assertEqual(unicode_block.name, "测试方块 🧱")
        
        # Empty textures (should be None)
        empty_tex_block = Block(
            id="test:empty_tex",
            name="Empty Texture",
            block_texture_path="",
            inventory_texture_path=""
        )
        # Empty strings should remain as empty strings, not None
        self.assertEqual(empty_tex_block.block_texture_path, "")
        self.assertEqual(empty_tex_block.inventory_texture_path, "")


class TestBlockUsageCases(unittest.TestCase):
    """Test realistic usage cases for blocks."""

    def test_create_building_block_set(self):
        """Test creating a set of related building blocks."""
        blocks = []
        
        # Stone variants
        stone_blocks = [
            Block(id="test:smooth_stone", name="Smooth Stone", 
                  item_group=item_group.BUILDING_BLOCKS),
            Block(id="test:stone_bricks", name="Stone Bricks", 
                  item_group=item_group.BUILDING_BLOCKS),
            Block(id="test:chiseled_stone", name="Chiseled Stone", 
                  item_group=item_group.BUILDING_BLOCKS)
        ]
        blocks.extend(stone_blocks)
        
        # Wood variants
        wood_blocks = [
            Block(id="test:oak_planks", name="Oak Planks", 
                  item_group=item_group.BUILDING_BLOCKS),
            Block(id="test:birch_planks", name="Birch Planks", 
                  item_group=item_group.BUILDING_BLOCKS)
        ]
        blocks.extend(wood_blocks)
        
        # Verify collection
        self.assertEqual(len(blocks), 5)
        self.assertTrue(all(isinstance(block, Block) for block in blocks))
        self.assertTrue(all(block.item_group == item_group.BUILDING_BLOCKS for block in blocks))

    def test_block_mod_registration_simulation(self):
        """Simulate registering blocks in a mod."""
        mod = fabricpy.ModConfig(
            mod_id="blocktest",
            name="Block Test Mod", 
            version="1.0.0",
            description="A mod for testing blocks.",
            authors=["Test Author"]
        )
        
        # Create various block types
        blocks = [
            Block(id="blocktest:marble", name="Marble", 
                  item_group=item_group.BUILDING_BLOCKS),
            Block(id="blocktest:colored_glass", name="Colored Glass", 
                  item_group=item_group.BUILDING_BLOCKS),
            Block(id="blocktest:lamp", name="Lamp", max_stack_size=16,
                  item_group=item_group.FUNCTIONAL)
        ]
        
        # Register blocks (simulate)
        for block in blocks:
            mod.registerBlock(block)
        
        # Verify registration
        self.assertEqual(len(mod.registered_blocks), 3)
        self.assertTrue(all(isinstance(block, Block) for block in mod.registered_blocks))

    def test_block_with_complex_texturing(self):
        """Test blocks with complex texture setups."""
        # Block with same texture for both
        simple_block = Block(
            id="test:simple",
            name="Simple Block",
            block_texture_path="textures/blocks/simple.png"
        )
        self.assertEqual(simple_block.block_texture_path, simple_block.inventory_texture_path)
        
        # Block with different textures
        complex_block = Block(
            id="test:complex",
            name="Complex Block", 
            block_texture_path="textures/blocks/complex_block.png",
            inventory_texture_path="textures/items/complex_item.png"
        )
        self.assertNotEqual(complex_block.block_texture_path, complex_block.inventory_texture_path)
        
        # Block with only inventory texture (like some technical blocks)
        tech_block = Block(
            id="test:technical",
            name="Technical Block",
            inventory_texture_path="textures/items/technical.png"
        )
        self.assertIsNone(tech_block.block_texture_path)
        self.assertEqual(tech_block.inventory_texture_path, "textures/items/technical.png")


if __name__ == '__main__':
    unittest.main()
