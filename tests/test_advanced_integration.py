"""
Advanced integration tests for fabricpy library testing complete workflows.
"""

import unittest
import tempfile
import os
import json
import shutil
from unittest.mock import Mock, patch, MagicMock

import fabricpy
from fabricpy.item import Item
from fabricpy.fooditem import FoodItem
from fabricpy.block import Block
from fabricpy.itemgroup import ItemGroup
from fabricpy.recipejson import RecipeJson
from fabricpy.modconfig import ModConfig
from fabricpy import item_group


class TestCompleteModWorkflows(unittest.TestCase):
    """Test complete mod creation workflows."""

    def test_complete_survival_mod_workflow(self):
        """Test creating a complete survival-focused mod."""
        # Create mod configuration
        mod = ModConfig(
            mod_id="survival_plus",
            name="Survival Plus",
            version="2.0.0",
            description="Enhanced survival experience with new tools, foods, and blocks.",
            authors=["ModMaker", "TestDev"]
        )
        
        # Create custom item groups
        tools_group = ItemGroup(id="survival_plus:tools", name="Survival Tools")
        foods_group = ItemGroup(id="survival_plus:foods", name="Survival Foods")
        blocks_group = ItemGroup(id="survival_plus:blocks", name="Survival Blocks")
        
        # Create advanced tools
        tools = [
            Item(
                id="survival_plus:obsidian_pickaxe",
                name="Obsidian Pickaxe",
                max_stack_size=1,
                texture_path="textures/items/obsidian_pickaxe.png",
                item_group=tools_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["OOO", " S ", " S "],
                    "key": {"O": "minecraft:obsidian", "S": "minecraft:stick"},
                    "result": {"id": "survival_plus:obsidian_pickaxe", "count": 1}
                })
            ),
            Item(
                id="survival_plus:multi_tool",
                name="Multi Tool",
                max_stack_size=1,
                texture_path="textures/items/multi_tool.png",
                item_group=tools_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["IDG", "ISI", " S "],
                    "key": {
                        "I": "minecraft:iron_ingot",
                        "D": "minecraft:diamond",
                        "G": "minecraft:gold_ingot",
                        "S": "minecraft:stick"
                    },
                    "result": {"id": "survival_plus:multi_tool", "count": 1}
                })
            )
        ]
        
        # Create survival foods
        foods = [
            FoodItem(
                id="survival_plus:energy_bar",
                name="Energy Bar",
                nutrition=8,
                saturation=12.8,
                always_edible=True,
                texture_path="textures/items/energy_bar.png",
                item_group=foods_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": ["minecraft:wheat", "minecraft:sugar", "minecraft:cocoa_beans", "minecraft:honey_bottle"],
                    "result": {"id": "survival_plus:energy_bar", "count": 2}
                })
            ),
            FoodItem(
                id="survival_plus:trail_mix",
                name="Trail Mix",
                nutrition=6,
                saturation=7.2,
                texture_path="textures/items/trail_mix.png",
                item_group=foods_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": ["minecraft:wheat_seeds", "minecraft:pumpkin_seeds", "minecraft:dried_kelp"],
                    "result": {"id": "survival_plus:trail_mix", "count": 4}
                })
            ),
            FoodItem(
                id="survival_plus:cooked_fish_stew",
                name="Cooked Fish Stew",
                nutrition=10,
                saturation=16.0,
                texture_path="textures/items/fish_stew.png",
                item_group=foods_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": [" F ", "BWB", " B "],
                    "key": {"F": "minecraft:cooked_cod", "B": "minecraft:bowl", "W": "minecraft:water_bucket"},
                    "result": {"id": "survival_plus:cooked_fish_stew", "count": 1}
                })
            )
        ]
        
        # Create building blocks
        blocks = [
            Block(
                id="survival_plus:reinforced_stone",
                name="Reinforced Stone",
                block_texture_path="textures/blocks/reinforced_stone.png",
                item_group=blocks_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["SIS", "III", "SIS"],
                    "key": {"S": "minecraft:stone", "I": "minecraft:iron_ingot"},
                    "result": {"id": "survival_plus:reinforced_stone", "count": 4}
                })
            ),
            Block(
                id="survival_plus:storage_crate",
                name="Storage Crate",
                max_stack_size=16,
                block_texture_path="textures/blocks/storage_crate.png",
                inventory_texture_path="textures/items/storage_crate.png",
                item_group=blocks_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["WWW", "W W", "WWW"],
                    "key": {"W": {"tag": "minecraft:planks"}},
                    "result": {"id": "survival_plus:storage_crate", "count": 1}
                })
            )
        ]
        
        # Register all components
        for tool in tools:
            mod.registerItem(tool)
        for food in foods:
            mod.registerItem(food)
        for block in blocks:
            mod.registerBlock(block)
        
        # Verify the complete mod
        self.assertEqual(len(mod.registered_items), 5)  # 2 tools + 3 foods
        self.assertEqual(len(mod.registered_blocks), 2)
        
        # Verify all items have recipes
        items_with_recipes = [item for item in mod.registered_items if item.recipe is not None]
        self.assertEqual(len(items_with_recipes), 5)
        
        # Verify all blocks have recipes
        blocks_with_recipes = [block for block in mod.registered_blocks if block.recipe is not None]
        self.assertEqual(len(blocks_with_recipes), 2)

    def test_complete_magic_mod_workflow(self):
        """Test creating a complete magic-themed mod."""
        mod = ModConfig(
            mod_id="arcane_arts",
            name="Arcane Arts",
            version="1.5.0",
            description="Magical items, enchanted foods, and mystical blocks.",
            authors=["WizardDev", "MagicMaker"]
        )
        
        # Create magical item group
        magic_group = ItemGroup(id="arcane_arts:magic", name="Arcane Items")
        
        # Create magical items with complex recipes
        magic_items = [
            Item(
                id="arcane_arts:crystal_wand",
                name="Crystal Wand",
                max_stack_size=1,
                texture_path="textures/items/crystal_wand.png",
                item_group=magic_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["  C", " S ", "S  "],
                    "key": {"C": "minecraft:diamond", "S": "minecraft:stick"},
                    "result": {
                        "id": "arcane_arts:crystal_wand",
                        "count": 1,
                        "nbt": "{Enchantments:[{id:\"minecraft:unbreaking\",lvl:3}]}"
                    }
                })
            ),
            Item(
                id="arcane_arts:spell_book",
                name="Spell Book",
                max_stack_size=16,
                texture_path="textures/items/spell_book.png",
                item_group=magic_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["LPL", "PBP", "LPL"],
                    "key": {"L": "minecraft:lapis_lazuli", "P": "minecraft:paper", "B": "minecraft:book"},
                    "result": {"id": "arcane_arts:spell_book", "count": 1}
                })
            )
        ]
        
        # Create magical foods
        magic_foods = [
            FoodItem(
                id="arcane_arts:mana_potion",
                name="Mana Potion",
                nutrition=0,
                saturation=0.0,
                always_edible=True,
                max_stack_size=16,
                texture_path="textures/items/mana_potion.png",
                item_group=magic_group,
                recipe=RecipeJson({
                    "type": "minecraft:brewing",
                    "ingredient": "minecraft:awkward_potion",
                    "addition": "minecraft:lapis_lazuli",
                    "result": "arcane_arts:mana_potion"
                })
            ),
            FoodItem(
                id="arcane_arts:enchanted_apple_pie",
                name="Enchanted Apple Pie",
                nutrition=12,
                saturation=20.0,
                always_edible=True,
                texture_path="textures/items/enchanted_apple_pie.png",
                item_group=magic_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["WWW", "GAG", "WWW"],
                    "key": {"W": "minecraft:wheat", "G": "minecraft:golden_apple", "A": "minecraft:apple"},
                    "result": {"id": "arcane_arts:enchanted_apple_pie", "count": 1}
                })
            )
        ]
        
        # Create magical blocks
        magic_blocks = [
            Block(
                id="arcane_arts:enchanting_altar",
                name="Enchanting Altar",
                max_stack_size=1,
                block_texture_path="textures/blocks/enchanting_altar.png",
                inventory_texture_path="textures/items/enchanting_altar.png",
                item_group=magic_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["LBL", "OEO", "OOO"],
                    "key": {
                        "L": "minecraft:lapis_lazuli",
                        "B": "minecraft:book",
                        "O": "minecraft:obsidian",
                        "E": "minecraft:enchanting_table"
                    },
                    "result": {"id": "arcane_arts:enchanting_altar", "count": 1}
                })
            ),
            Block(
                id="arcane_arts:crystal_ore",
                name="Crystal Ore",
                block_texture_path="textures/blocks/crystal_ore.png",
                item_group=magic_group,
                recipe=RecipeJson({
                    "type": "minecraft:smelting",
                    "ingredient": "arcane_arts:raw_crystal",
                    "result": "arcane_arts:crystal_shard",
                    "experience": 2.0,
                    "cookingtime": 400
                })
            )
        ]
        
        # Register all components
        for item in magic_items:
            mod.registerItem(item)
        for food in magic_foods:
            mod.registerItem(food)
        for block in magic_blocks:
            mod.registerBlock(block)
        
        # Verify the magic mod
        self.assertEqual(len(mod.registered_items), 4)  # 2 items + 2 foods
        self.assertEqual(len(mod.registered_blocks), 2)
        
        # Verify special properties
        always_edible_items = [item for item in mod.registered_items if hasattr(item, 'always_edible') and item.always_edible]
        self.assertEqual(len(always_edible_items), 2)  # Both magic foods
        
        single_stack_items = [item for item in mod.registered_items + mod.registered_blocks if item.max_stack_size == 1]
        self.assertEqual(len(single_stack_items), 2)  # Wand and altar

    def test_recipe_chain_workflow(self):
        """Test creating a mod with interconnected recipe chains."""
        mod = ModConfig(
            mod_id="crafting_chains",
            name="Crafting Chains",
            version="1.0.0",
            description="Complex crafting chains and material processing.",
            authors=["ChainMaster"]
        )
        
        # Create a complex crafting chain: Ore -> Ingot -> Alloy -> Tool
        
        # Step 1: Raw materials (would be found in world)
        raw_materials = [
            Item(id="crafting_chains:copper_ore", name="Copper Ore"),
            Item(id="crafting_chains:tin_ore", name="Tin Ore")
        ]
        
        # Step 2: Smelted ingots
        ingots = [
            Item(
                id="crafting_chains:copper_ingot",
                name="Copper Ingot",
                recipe=RecipeJson({
                    "type": "minecraft:smelting",
                    "ingredient": "crafting_chains:copper_ore",
                    "result": "crafting_chains:copper_ingot",
                    "experience": 0.5,
                    "cookingtime": 200
                })
            ),
            Item(
                id="crafting_chains:tin_ingot",
                name="Tin Ingot",
                recipe=RecipeJson({
                    "type": "minecraft:smelting",
                    "ingredient": "crafting_chains:tin_ore",
                    "result": "crafting_chains:tin_ingot",
                    "experience": 0.5,
                    "cookingtime": 200
                })
            )
        ]
        
        # Step 3: Alloy (combining ingots)
        alloy = Item(
            id="crafting_chains:bronze_ingot",
            name="Bronze Ingot",
            recipe=RecipeJson({
                "type": "minecraft:crafting_shapeless",
                "ingredients": [
                    "crafting_chains:copper_ingot",
                    "crafting_chains:copper_ingot",
                    "crafting_chains:copper_ingot",
                    "crafting_chains:tin_ingot"
                ],
                "result": {"id": "crafting_chains:bronze_ingot", "count": 4}
            })
        )
        
        # Step 4: Advanced tools using the alloy
        advanced_tools = [
            Item(
                id="crafting_chains:bronze_pickaxe",
                name="Bronze Pickaxe",
                max_stack_size=1,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["BBB", " S ", " S "],
                    "key": {"B": "crafting_chains:bronze_ingot", "S": "minecraft:stick"},
                    "result": {"id": "crafting_chains:bronze_pickaxe", "count": 1}
                })
            ),
            Item(
                id="crafting_chains:bronze_sword",
                name="Bronze Sword",
                max_stack_size=1,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": [" B ", " B ", " S "],
                    "key": {"B": "crafting_chains:bronze_ingot", "S": "minecraft:stick"},
                    "result": {"id": "crafting_chains:bronze_sword", "count": 1}
                })
            )
        ]
        
        # Step 5: Ultimate item requiring multiple tools
        ultimate_item = Item(
            id="crafting_chains:master_tool",
            name="Master Tool",
            max_stack_size=1,
            recipe=RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["PSA", "DGD", "III"],
                "key": {
                    "P": "crafting_chains:bronze_pickaxe",
                    "S": "crafting_chains:bronze_sword",
                    "A": "minecraft:diamond_axe",
                    "D": "minecraft:diamond",
                    "G": "minecraft:gold_block",
                    "I": "minecraft:iron_block"
                },
                "result": {"id": "crafting_chains:master_tool", "count": 1}
            })
        )
        
        # Register all items in the chain
        all_items = raw_materials + ingots + [alloy] + advanced_tools + [ultimate_item]
        for item in all_items:
            mod.registerItem(item)
        
        # Verify the chain
        self.assertEqual(len(mod.registered_items), 8)
        
        # Verify recipe dependencies
        items_with_recipes = [item for item in mod.registered_items if item.recipe is not None]
        self.assertEqual(len(items_with_recipes), 6)  # All except raw materials
        
        # Verify ultimate item uses other crafted items
        ultimate_recipe = ultimate_item.recipe.data
        self.assertIn("crafting_chains:bronze_pickaxe", str(ultimate_recipe))
        self.assertIn("crafting_chains:bronze_sword", str(ultimate_recipe))

    def test_food_progression_workflow(self):
        """Test creating a mod with food progression system."""
        mod = ModConfig(
            mod_id="gourmet_cooking",
            name="Gourmet Cooking",
            version="1.0.0",
            description="Advanced cooking and food progression system.",
            authors=["ChefDev"]
        )
        
        # Create custom food group
        gourmet_group = ItemGroup(id="gourmet_cooking:foods", name="Gourmet Foods")
        
        # Basic ingredients
        ingredients = [
            Item(id="gourmet_cooking:flour", name="Flour", item_group=gourmet_group),
            Item(id="gourmet_cooking:butter", name="Butter", item_group=gourmet_group),
            Item(id="gourmet_cooking:salt", name="Salt", item_group=gourmet_group)
        ]
        
        # Simple foods
        simple_foods = [
            FoodItem(
                id="gourmet_cooking:bread_dough",
                name="Bread Dough",
                nutrition=1,
                saturation=0.5,
                item_group=gourmet_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": ["gourmet_cooking:flour", "minecraft:water_bucket"],
                    "result": {"id": "gourmet_cooking:bread_dough", "count": 1}
                })
            ),
            FoodItem(
                id="gourmet_cooking:fresh_bread",
                name="Fresh Bread",
                nutrition=6,
                saturation=8.0,
                item_group=gourmet_group,
                recipe=RecipeJson({
                    "type": "minecraft:smelting",
                    "ingredient": "gourmet_cooking:bread_dough",
                    "result": "gourmet_cooking:fresh_bread",
                    "experience": 0.3,
                    "cookingtime": 300
                })
            )
        ]
        
        # Advanced foods
        advanced_foods = [
            FoodItem(
                id="gourmet_cooking:cake_batter",
                name="Cake Batter",
                nutrition=2,
                saturation=1.0,
                item_group=gourmet_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shapeless",
                    "ingredients": [
                        "gourmet_cooking:flour",
                        "gourmet_cooking:butter",
                        "minecraft:sugar",
                        "minecraft:egg",
                        "minecraft:milk_bucket"
                    ],
                    "result": {"id": "gourmet_cooking:cake_batter", "count": 1}
                })
            ),
            FoodItem(
                id="gourmet_cooking:chocolate_cake",
                name="Chocolate Cake",
                nutrition=12,
                saturation=20.0,
                max_stack_size=1,
                item_group=gourmet_group,
                recipe=RecipeJson({
                    "type": "minecraft:smelting",
                    "ingredient": "gourmet_cooking:cake_batter",
                    "result": "gourmet_cooking:chocolate_cake",
                    "experience": 1.0,
                    "cookingtime": 600
                })
            )
        ]
        
        # Gourmet foods (highest tier)
        gourmet_foods = [
            FoodItem(
                id="gourmet_cooking:five_star_meal",
                name="Five Star Meal",
                nutrition=20,
                saturation=30.0,
                always_edible=True,
                max_stack_size=1,
                item_group=gourmet_group,
                recipe=RecipeJson({
                    "type": "minecraft:crafting_shaped",
                    "pattern": ["BCM", "SPS", "FVR"],
                    "key": {
                        "B": "gourmet_cooking:fresh_bread",
                        "C": "gourmet_cooking:chocolate_cake",
                        "M": "minecraft:cooked_beef",
                        "S": "gourmet_cooking:salt",
                        "P": "minecraft:golden_apple",
                        "F": "minecraft:cooked_salmon",
                        "V": "minecraft:carrot",
                        "R": "minecraft:baked_potato"
                    },
                    "result": {"id": "gourmet_cooking:five_star_meal", "count": 1}
                })
            )
        ]
        
        # Register all foods
        all_foods = ingredients + simple_foods + advanced_foods + gourmet_foods
        for food in all_foods:
            mod.registerItem(food)
        
        # Verify the food progression
        self.assertEqual(len(mod.registered_items), 8)
        
        # Verify nutrition progression
        nutrition_values = [item.nutrition for item in mod.registered_items if hasattr(item, 'nutrition')]
        self.assertTrue(max(nutrition_values) > min(nutrition_values))  # Should have progression
        
        # Verify the ultimate food uses other crafted foods
        ultimate_recipe = gourmet_foods[0].recipe.data
        self.assertIn("gourmet_cooking:fresh_bread", str(ultimate_recipe))
        self.assertIn("gourmet_cooking:chocolate_cake", str(ultimate_recipe))


class TestModCompilationWorkflow(unittest.TestCase):
    """Test the complete mod compilation workflow."""

    def test_mod_compilation_simulation(self):
        """Test simulating the mod compilation process."""
        # Create a complete mod
        mod = ModConfig(
            mod_id="compilation_test",
            name="Compilation Test Mod",
            version="1.0.0",
            description="Testing mod compilation workflow.",
            authors=["TestDev"]
        )
        
        # Add various components
        test_item = Item(
            id="compilation_test:test_item",
            name="Test Item",
            recipe=RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["#"],
                "key": {"#": "minecraft:stone"},
                "result": {"id": "compilation_test:test_item", "count": 1}
            })
        )
        
        test_food = FoodItem(
            id="compilation_test:test_food",
            name="Test Food",
            nutrition=5,
            saturation=6.0
        )
        
        test_block = Block(
            id="compilation_test:test_block",
            name="Test Block",
            recipe=RecipeJson({
                "type": "minecraft:crafting_shaped",
                "pattern": ["##", "##"],
                "key": {"#": "compilation_test:test_item"},
                "result": {"id": "compilation_test:test_block", "count": 1}
            })
        )
        
        # Register components
        mod.registerItem(test_item)
        mod.registerItem(test_food)
        mod.registerBlock(test_block)
        
        # Verify mod is ready for compilation
        self.assertEqual(len(mod.registered_items), 2)
        self.assertEqual(len(mod.registered_blocks), 1)
        
        # Verify all registered items have proper IDs
        for item in mod.registered_items:
            self.assertIsNotNone(item.id)
            self.assertTrue(item.id.startswith("compilation_test:"))
        
        for block in mod.registered_blocks:
            self.assertIsNotNone(block.id)
            self.assertTrue(block.id.startswith("compilation_test:"))
        
        # Verify recipe dependencies are satisfied
        items_with_recipes = [item for item in mod.registered_items if item.recipe is not None]
        blocks_with_recipes = [block for block in mod.registered_blocks if block.recipe is not None]
        
        self.assertEqual(len(items_with_recipes), 1)
        self.assertEqual(len(blocks_with_recipes), 1)
        
        # The block recipe should reference the item
        block_recipe = test_block.recipe.data
        self.assertIn("compilation_test:test_item", str(block_recipe))


if __name__ == '__main__':
    unittest.main()
