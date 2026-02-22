"""
Unit tests for the LootTable and LootPool classes.
"""

import json
import os
import shutil
import tempfile
import unittest

from fabricpy.block import Block
from fabricpy.loottable import (
    LootPool,
    LootTable,
    _explosion_decay_function,
    _item_entry,
    _silk_touch_condition,
    _survives_explosion,
)


class TestLootTableCreation(unittest.TestCase):
    """Test basic LootTable construction."""

    def test_creation_from_dict(self):
        """Test creating a loot table from a dictionary."""
        data = {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item", "name": "mymod:ruby_block"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                }
            ],
        }
        lt = LootTable(data)
        self.assertEqual(lt.loot_type, "minecraft:block")
        self.assertEqual(len(lt.pools), 1)
        self.assertEqual(lt.category, "blocks")
        self.assertEqual(lt.data, data)

    def test_creation_from_json_string(self):
        """Test creating a loot table from a JSON string."""
        json_str = json.dumps(
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "rolls": 1,
                        "entries": [
                            {"type": "minecraft:item", "name": "mymod:test_block"}
                        ],
                    }
                ],
            }
        )
        lt = LootTable(json_str)
        self.assertEqual(lt.loot_type, "minecraft:block")
        self.assertEqual(lt.data["pools"][0]["entries"][0]["name"], "mymod:test_block")

    def test_creation_from_pool_list(self):
        """Test creating a loot table from a list of LootPool builders."""
        pool = LootPool().rolls(1).entry("mymod:item")
        lt = LootTable([pool], loot_type="minecraft:block")
        self.assertEqual(lt.loot_type, "minecraft:block")
        self.assertEqual(len(lt.pools), 1)
        self.assertEqual(lt.pools[0]["entries"][0]["name"], "mymod:item")

    def test_creation_from_pools_requires_type(self):
        """Test that pool-list creation requires loot_type."""
        pool = LootPool().rolls(1).entry("mymod:item")
        with self.assertRaises(ValueError):
            LootTable([pool])

    def test_missing_type_raises(self):
        """Test that missing 'type' field raises ValueError."""
        with self.assertRaises(ValueError):
            LootTable({"pools": []})

    def test_empty_type_raises(self):
        """Test that empty 'type' value raises ValueError."""
        with self.assertRaises(ValueError):
            LootTable({"type": "", "pools": []})

    def test_invalid_json_string_raises(self):
        """Test that invalid JSON string raises json.JSONDecodeError."""
        with self.assertRaises(json.JSONDecodeError):
            LootTable("not valid json")

    def test_custom_category(self):
        """Test that custom category is stored."""
        lt = LootTable(
            {"type": "minecraft:entity", "pools": []},
            category="entities",
        )
        self.assertEqual(lt.category, "entities")

    def test_repr(self):
        """Test __repr__ output."""
        lt = LootTable.drops_self("mymod:block")
        r = repr(lt)
        self.assertIn("minecraft:block", r)
        self.assertIn("pools=1", r)
        self.assertIn("blocks", r)

    def test_equality(self):
        """Test __eq__ between loot tables."""
        a = LootTable.drops_self("mymod:block")
        b = LootTable.drops_self("mymod:block")
        self.assertEqual(a, b)

    def test_inequality(self):
        """Test inequality between different loot tables."""
        a = LootTable.drops_self("mymod:block_a")
        b = LootTable.drops_self("mymod:block_b")
        self.assertNotEqual(a, b)

    def test_not_equal_to_other_types(self):
        """Test that LootTable is not equal to non-LootTable objects."""
        lt = LootTable.drops_self("mymod:block")
        self.assertNotEqual(lt, "not a loot table")


class TestLootTableDropsSelf(unittest.TestCase):
    """Test the drops_self class method."""

    def test_drops_self_basic(self):
        """Test basic drops_self loot table."""
        lt = LootTable.drops_self("mymod:ruby_block")
        self.assertEqual(lt.loot_type, "minecraft:block")
        self.assertEqual(lt.category, "blocks")
        self.assertEqual(len(lt.pools), 1)

        pool = lt.pools[0]
        self.assertEqual(pool["rolls"], 1)
        self.assertEqual(len(pool["entries"]), 1)
        self.assertEqual(pool["entries"][0]["type"], "minecraft:item")
        self.assertEqual(pool["entries"][0]["name"], "mymod:ruby_block")

        # Should have survives_explosion condition
        self.assertEqual(len(pool["conditions"]), 1)
        self.assertEqual(
            pool["conditions"][0]["condition"], "minecraft:survives_explosion"
        )

    def test_drops_self_produces_valid_json(self):
        """Test that drops_self produces valid JSON."""
        lt = LootTable.drops_self("mymod:test_block")
        parsed = json.loads(lt.text)
        self.assertEqual(parsed["type"], "minecraft:block")


class TestLootTableDropsItem(unittest.TestCase):
    """Test the drops_item class method."""

    def test_drops_item_fixed_count(self):
        """Test dropping a fixed number of items."""
        lt = LootTable.drops_item("mymod:ore", "mymod:gem", count=3)
        pool = lt.pools[0]
        entry = pool["entries"][0]
        self.assertEqual(entry["name"], "mymod:gem")

        # Should have set_count and explosion_decay functions
        funcs = entry.get("functions", [])
        func_types = [f["function"] for f in funcs]
        self.assertIn("minecraft:set_count", func_types)
        self.assertIn("minecraft:explosion_decay", func_types)

    def test_drops_item_range(self):
        """Test dropping a range of items."""
        lt = LootTable.drops_item("mymod:ore", "mymod:gem", min_count=1, max_count=4)
        pool = lt.pools[0]
        entry = pool["entries"][0]
        funcs = entry["functions"]

        set_count = next(f for f in funcs if f["function"] == "minecraft:set_count")
        self.assertEqual(set_count["count"]["min"], 1)
        self.assertEqual(set_count["count"]["max"], 4)

    def test_drops_item_single(self):
        """Test dropping a single item (default)."""
        lt = LootTable.drops_item("mymod:ore", "mymod:gem")
        pool = lt.pools[0]
        entry = pool["entries"][0]
        self.assertEqual(entry["name"], "mymod:gem")
        # count=1 should still have explosion_decay
        funcs = entry.get("functions", [])
        func_types = [f["function"] for f in funcs]
        self.assertIn("minecraft:explosion_decay", func_types)


class TestLootTableDropsNothing(unittest.TestCase):
    """Test the drops_nothing class method."""

    def test_drops_nothing(self):
        """Test empty loot table."""
        lt = LootTable.drops_nothing()
        self.assertEqual(lt.loot_type, "minecraft:block")
        self.assertEqual(len(lt.pools), 0)


class TestLootTableDropsWithSilkTouch(unittest.TestCase):
    """Test the drops_with_silk_touch class method."""

    def test_silk_touch_only(self):
        """Test glass-style: drops itself with silk touch, nothing without."""
        lt = LootTable.drops_with_silk_touch("mymod:crystal_glass")
        pool = lt.pools[0]

        # Should use alternatives entry type
        alt = pool["entries"][0]
        self.assertEqual(alt["type"], "minecraft:alternatives")

        children = alt["children"]
        # First child: silk touch drops the block itself
        self.assertEqual(children[0]["name"], "mymod:crystal_glass")
        self.assertTrue(
            any(
                c.get("condition") == "minecraft:match_tool"
                for c in children[0].get("conditions", [])
            )
        )
        # No second child (nothing dropped without silk touch)
        self.assertEqual(len(children), 1)

    def test_silk_touch_with_alternative(self):
        """Test ore-style: silk touch gives block, otherwise gives item."""
        lt = LootTable.drops_with_silk_touch(
            "mymod:ruby_ore",
            no_silk_touch_item="mymod:ruby",
            no_silk_touch_count=1,
        )
        pool = lt.pools[0]
        alt = pool["entries"][0]
        children = alt["children"]

        self.assertEqual(len(children), 2)
        # Silk touch child drops the ore block
        self.assertEqual(children[0]["name"], "mymod:ruby_ore")
        # Non-silk-touch child drops the item
        self.assertEqual(children[1]["name"], "mymod:ruby")

    def test_silk_touch_custom_item(self):
        """Test silk touch with a custom item drop."""
        lt = LootTable.drops_with_silk_touch(
            "mymod:ice_block",
            silk_touch_item="mymod:packed_ice",
        )
        pool = lt.pools[0]
        alt = pool["entries"][0]
        children = alt["children"]
        self.assertEqual(children[0]["name"], "mymod:packed_ice")


class TestLootTableDropsWithFortune(unittest.TestCase):
    """Test the drops_with_fortune class method."""

    def test_fortune_basic(self):
        """Test fortune-affected ore drops."""
        lt = LootTable.drops_with_fortune(
            "mymod:ruby_ore",
            "mymod:ruby",
            min_count=1,
            max_count=2,
        )
        pool = lt.pools[0]
        alt = pool["entries"][0]
        self.assertEqual(alt["type"], "minecraft:alternatives")

        children = alt["children"]
        # First child: silk touch drops block
        self.assertEqual(children[0]["name"], "mymod:ruby_ore")
        # Second child: no silk touch drops item with fortune
        self.assertEqual(children[1]["name"], "mymod:ruby")

        funcs = children[1]["functions"]
        func_types = [f["function"] for f in funcs]
        self.assertIn("minecraft:set_count", func_types)
        self.assertIn("minecraft:apply_bonus", func_types)
        self.assertIn("minecraft:explosion_decay", func_types)

    def test_fortune_no_silk_touch_self_drop(self):
        """Test fortune without silk touch self-drop."""
        lt = LootTable.drops_with_fortune(
            "mymod:ore",
            "mymod:gem",
            silk_touch_drops_self=False,
        )
        pool = lt.pools[0]
        alt = pool["entries"][0]
        children = alt["children"]
        # Only one child: the fortune drop
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0]["name"], "mymod:gem")


class TestLootTableEntityAndChest(unittest.TestCase):
    """Test entity and chest convenience constructors."""

    def test_entity_loot_table(self):
        """Test entity loot table creation."""
        pool = LootPool().rolls(1).entry("mymod:fang", weight=3)
        lt = LootTable.entity([pool])
        self.assertEqual(lt.loot_type, "minecraft:entity")
        self.assertEqual(lt.category, "entities")
        self.assertEqual(lt.pools[0]["entries"][0]["name"], "mymod:fang")
        self.assertEqual(lt.pools[0]["entries"][0]["weight"], 3)

    def test_chest_loot_table(self):
        """Test chest loot table creation."""
        pool = (
            LootPool()
            .rolls({"type": "minecraft:uniform", "min": 2, "max": 5})
            .entry("mymod:golden_key", weight=5)
            .entry("minecraft:diamond", weight=1)
        )
        lt = LootTable.chest([pool])
        self.assertEqual(lt.loot_type, "minecraft:chest")
        self.assertEqual(lt.category, "chests")
        self.assertEqual(len(lt.pools[0]["entries"]), 2)

    def test_from_pools_custom(self):
        """Test from_pools with a custom type."""
        pool = LootPool().rolls(1).entry("mymod:item")
        lt = LootTable.from_pools("minecraft:fishing", [pool], category="gameplay")
        self.assertEqual(lt.loot_type, "minecraft:fishing")
        self.assertEqual(lt.category, "gameplay")


class TestLootPool(unittest.TestCase):
    """Test the LootPool fluent builder."""

    def test_basic_pool(self):
        """Test building a basic pool."""
        pool = LootPool().rolls(1).entry("mymod:item").build()
        self.assertEqual(pool["rolls"], 1)
        self.assertEqual(len(pool["entries"]), 1)
        self.assertEqual(pool["entries"][0]["name"], "mymod:item")

    def test_pool_with_bonus_rolls(self):
        """Test pool with bonus rolls."""
        pool = LootPool().rolls(1).bonus_rolls(2).entry("mymod:item").build()
        self.assertEqual(pool["bonus_rolls"], 2)

    def test_pool_with_weighted_entries(self):
        """Test pool with multiple weighted entries."""
        pool = (
            LootPool()
            .rolls(1)
            .entry("mymod:common", weight=10)
            .entry("mymod:rare", weight=1)
            .build()
        )
        self.assertEqual(len(pool["entries"]), 2)
        self.assertEqual(pool["entries"][0]["weight"], 10)
        self.assertEqual(pool["entries"][1]["weight"], 1)

    def test_pool_with_conditions(self):
        """Test pool with conditions."""
        pool = (
            LootPool()
            .rolls(1)
            .entry("mymod:item")
            .condition({"condition": "minecraft:survives_explosion"})
            .build()
        )
        self.assertEqual(len(pool["conditions"]), 1)
        self.assertEqual(
            pool["conditions"][0]["condition"], "minecraft:survives_explosion"
        )

    def test_pool_with_functions(self):
        """Test pool with functions."""
        pool = (
            LootPool()
            .rolls(1)
            .entry("mymod:item")
            .function({"function": "minecraft:explosion_decay"})
            .build()
        )
        self.assertEqual(len(pool["functions"]), 1)

    def test_pool_with_raw_entry(self):
        """Test pool with a raw entry dict."""
        raw = {
            "type": "minecraft:alternatives",
            "children": [
                {"type": "minecraft:item", "name": "mymod:a"},
                {"type": "minecraft:item", "name": "mymod:b"},
            ],
        }
        pool = LootPool().rolls(1).raw_entry(raw).build()
        self.assertEqual(pool["entries"][0]["type"], "minecraft:alternatives")

    def test_pool_with_quality(self):
        """Test entry with quality parameter."""
        pool = LootPool().rolls(1).entry("mymod:item", quality=5).build()
        self.assertEqual(pool["entries"][0]["quality"], 5)

    def test_pool_chaining(self):
        """Test that all setters return self for chaining."""
        pool = LootPool()
        result = pool.rolls(1)
        self.assertIs(result, pool)
        result = pool.bonus_rolls(0)
        self.assertIs(result, pool)
        result = pool.entry("mymod:item")
        self.assertIs(result, pool)
        result = pool.condition({})
        self.assertIs(result, pool)
        result = pool.function({})
        self.assertIs(result, pool)
        result = pool.raw_entry({})
        self.assertIs(result, pool)

    def test_pool_number_provider_rolls(self):
        """Test pool with number provider for rolls."""
        provider = {"type": "minecraft:uniform", "min": 1, "max": 3}
        pool = LootPool().rolls(provider).entry("mymod:item").build()
        self.assertEqual(pool["rolls"], provider)


class TestHelperFunctions(unittest.TestCase):
    """Test module-level helper functions."""

    def test_survives_explosion(self):
        """Test survives_explosion condition."""
        cond = _survives_explosion()
        self.assertEqual(cond["condition"], "minecraft:survives_explosion")

    def test_silk_touch_condition(self):
        """Test silk touch condition structure."""
        cond = _silk_touch_condition()
        self.assertEqual(cond["condition"], "minecraft:match_tool")
        self.assertIn("predicate", cond)

    def test_explosion_decay_function(self):
        """Test explosion decay function."""
        func = _explosion_decay_function()
        self.assertEqual(func["function"], "minecraft:explosion_decay")

    def test_item_entry_basic(self):
        """Test basic item entry."""
        entry = _item_entry("mymod:item")
        self.assertEqual(entry["type"], "minecraft:item")
        self.assertEqual(entry["name"], "mymod:item")
        self.assertNotIn("weight", entry)
        self.assertNotIn("quality", entry)

    def test_item_entry_with_all_params(self):
        """Test item entry with all optional params."""
        entry = _item_entry(
            "mymod:item",
            weight=5,
            quality=2,
            conditions=[{"condition": "minecraft:survives_explosion"}],
            functions=[{"function": "minecraft:explosion_decay"}],
        )
        self.assertEqual(entry["weight"], 5)
        self.assertEqual(entry["quality"], 2)
        self.assertEqual(len(entry["conditions"]), 1)
        self.assertEqual(len(entry["functions"]), 1)


class TestBlockLootTableAttribute(unittest.TestCase):
    """Test Block integration with loot tables."""

    def test_block_default_no_loot_table(self):
        """Test that Block defaults to no loot table."""
        block = Block(id="mymod:block", name="Block")
        self.assertIsNone(block.loot_table)

    def test_block_with_loot_table(self):
        """Test creating a Block with a loot table."""
        lt = LootTable.drops_self("mymod:ruby_block")
        block = Block(
            id="mymod:ruby_block",
            name="Ruby Block",
            loot_table=lt,
        )
        self.assertIsNotNone(block.loot_table)
        self.assertEqual(block.loot_table.loot_type, "minecraft:block")


class TestModConfigLootTableIntegration(unittest.TestCase):
    """Test ModConfig loot table writing."""

    def setUp(self):
        """Create a temporary directory for test output."""
        self.test_dir = tempfile.mkdtemp()
        # Create minimal directory structure
        resources = os.path.join(
            self.test_dir, "src", "main", "resources", "data", "testmod"
        )
        os.makedirs(resources, exist_ok=True)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_write_block_loot_tables(self):
        """Test that block loot tables are written to disk."""
        from fabricpy.modconfig import ModConfig

        mod = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.test_dir,
            enable_testing=False,
        )

        lt = LootTable.drops_self("testmod:ruby_block")
        block = Block(
            id="testmod:ruby_block",
            name="Ruby Block",
            loot_table=lt,
        )
        mod.registerBlock(block)
        mod.write_loot_table_files(self.test_dir, "testmod")

        expected_path = os.path.join(
            self.test_dir,
            "src",
            "main",
            "resources",
            "data",
            "testmod",
            "loot_table",
            "blocks",
            "ruby_block.json",
        )
        self.assertTrue(os.path.exists(expected_path))

        with open(expected_path) as f:
            data = json.load(f)
        self.assertEqual(data["type"], "minecraft:block")
        self.assertEqual(data["pools"][0]["entries"][0]["name"], "testmod:ruby_block")

    def test_write_standalone_loot_table(self):
        """Test that standalone loot tables are written to disk."""
        from fabricpy.modconfig import ModConfig

        mod = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.test_dir,
            enable_testing=False,
        )

        lt = LootTable.entity([LootPool().rolls(1).entry("testmod:fang")])
        mod.registerLootTable("custom_zombie", lt)
        mod.write_loot_table_files(self.test_dir, "testmod")

        expected_path = os.path.join(
            self.test_dir,
            "src",
            "main",
            "resources",
            "data",
            "testmod",
            "loot_table",
            "entities",
            "custom_zombie.json",
        )
        self.assertTrue(os.path.exists(expected_path))

        with open(expected_path) as f:
            data = json.load(f)
        self.assertEqual(data["type"], "minecraft:entity")

    def test_no_loot_tables_skips(self):
        """Test that write is skipped when no loot tables are registered."""
        from fabricpy.modconfig import ModConfig

        mod = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.test_dir,
            enable_testing=False,
        )
        # Should not raise or create any files
        mod.write_loot_table_files(self.test_dir, "testmod")

        loot_dir = os.path.join(
            self.test_dir,
            "src",
            "main",
            "resources",
            "data",
            "testmod",
            "loot_table",
        )
        self.assertFalse(os.path.exists(loot_dir))

    def test_multiple_block_loot_tables(self):
        """Test writing loot tables for multiple blocks."""
        from fabricpy.modconfig import ModConfig

        mod = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            version="1.0.0",
            description="Test",
            authors=["Test"],
            project_dir=self.test_dir,
            enable_testing=False,
        )

        blocks = [
            Block(
                id="testmod:ruby_block",
                name="Ruby Block",
                loot_table=LootTable.drops_self("testmod:ruby_block"),
            ),
            Block(
                id="testmod:ruby_ore",
                name="Ruby Ore",
                loot_table=LootTable.drops_with_fortune(
                    "testmod:ruby_ore",
                    "testmod:ruby",
                ),
            ),
        ]
        for b in blocks:
            mod.registerBlock(b)

        mod.write_loot_table_files(self.test_dir, "testmod")

        for name in ("ruby_block", "ruby_ore"):
            path = os.path.join(
                self.test_dir,
                "src",
                "main",
                "resources",
                "data",
                "testmod",
                "loot_table",
                "blocks",
                f"{name}.json",
            )
            self.assertTrue(os.path.exists(path), f"Missing loot table for {name}")


class TestLootTableJsonOutput(unittest.TestCase):
    """Test that the complete JSON output is well-formed and valid."""

    def _roundtrip(self, lt: LootTable) -> dict:
        """Parse the text back to dict and compare with data."""
        parsed = json.loads(lt.text)
        self.assertEqual(parsed, lt.data)
        return parsed

    def test_drops_self_roundtrip(self):
        data = self._roundtrip(LootTable.drops_self("mymod:block"))
        self.assertIn("pools", data)

    def test_drops_item_roundtrip(self):
        self._roundtrip(
            LootTable.drops_item("mymod:ore", "mymod:gem", min_count=1, max_count=3)
        )

    def test_drops_nothing_roundtrip(self):
        self._roundtrip(LootTable.drops_nothing())

    def test_drops_with_silk_touch_roundtrip(self):
        self._roundtrip(
            LootTable.drops_with_silk_touch(
                "mymod:glass", no_silk_touch_item="mymod:shard"
            )
        )

    def test_drops_with_fortune_roundtrip(self):
        self._roundtrip(LootTable.drops_with_fortune("mymod:ore", "mymod:gem"))

    def test_entity_roundtrip(self):
        self._roundtrip(LootTable.entity([LootPool().rolls(1).entry("mymod:drop")]))

    def test_chest_roundtrip(self):
        self._roundtrip(
            LootTable.chest(
                [
                    LootPool()
                    .rolls(3)
                    .entry("mymod:a", weight=5)
                    .entry("mymod:b", weight=1)
                ]
            )
        )


if __name__ == "__main__":
    unittest.main()
