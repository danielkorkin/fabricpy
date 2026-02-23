"""
Unit tests for block mining properties.

Tests the new mining configuration features:
- hardness / resistance
- mining_level
- requires_tool (explicit and inferred)
- mining_speeds (per-tool speed overrides)
- Validation of tool types, mining levels, and mining_speeds keys
- Java code generation for blocks with mining properties
- Block tag generation (mineable/<tool>, needs_<level>_tool)
- CustomMiningBlock Java class generation
"""

import json
import os
import shutil
import tempfile
import unittest

from fabricpy import Block, ModConfig, RecipeJson, item_group
from fabricpy.block import VALID_MINING_LEVELS, VALID_TOOL_TYPES


# ===================================================================== #
#                      Block constructor tests                          #
# ===================================================================== #


class TestBlockMiningProperties(unittest.TestCase):
    """Test Block constructor with mining properties."""

    def test_default_mining_values(self):
        """New mining attrs default to None / False when unset."""
        blk = Block(id="mod:stone", name="Stone")
        self.assertIsNone(blk.hardness)
        self.assertIsNone(blk.resistance)
        self.assertIsNone(blk.mining_level)
        self.assertFalse(blk.requires_tool)
        self.assertIsNone(blk.mining_speeds)

    def test_hardness_and_resistance(self):
        blk = Block(id="mod:ore", name="Ore", hardness=3.0, resistance=5.0)
        self.assertEqual(blk.hardness, 3.0)
        self.assertEqual(blk.resistance, 5.0)

    def test_hardness_only(self):
        """Resistance stays None when only hardness is provided."""
        blk = Block(id="mod:ore", name="Ore", hardness=2.5)
        self.assertEqual(blk.hardness, 2.5)
        self.assertIsNone(blk.resistance)

    def test_resistance_only(self):
        """Hardness stays None when only resistance is provided."""
        blk = Block(id="mod:ore", name="Ore", resistance=10.0)
        self.assertIsNone(blk.hardness)
        self.assertEqual(blk.resistance, 10.0)

    def test_mining_level_valid(self):
        for lvl in ("stone", "iron", "diamond"):
            blk = Block(id="mod:ore", name="Ore", mining_level=lvl)
            self.assertEqual(blk.mining_level, lvl)

    def test_mining_level_invalid(self):
        with self.assertRaises(ValueError):
            Block(id="mod:ore", name="Ore", mining_level="wooden")

    def test_requires_tool_explicit_true(self):
        blk = Block(id="mod:ore", name="Ore", requires_tool=True)
        self.assertTrue(blk.requires_tool)

    def test_requires_tool_explicit_false(self):
        """Even with tool_type set, explicit False overrides."""
        blk = Block(id="mod:ore", name="Ore", tool_type="pickaxe", requires_tool=False)
        self.assertFalse(blk.requires_tool)

    def test_requires_tool_inferred_from_tool_type(self):
        blk = Block(id="mod:ore", name="Ore", tool_type="pickaxe")
        self.assertTrue(blk.requires_tool)

    def test_requires_tool_inferred_no_tool(self):
        blk = Block(id="mod:ore", name="Ore")
        self.assertFalse(blk.requires_tool)

    def test_mining_speeds_valid(self):
        speeds = {"pickaxe": 8.0, "shovel": 2.0}
        blk = Block(id="mod:ore", name="Ore", mining_speeds=speeds)
        self.assertEqual(blk.mining_speeds, speeds)
        # Must be a copy, not the original dict
        self.assertIsNot(blk.mining_speeds, speeds)

    def test_mining_speeds_single_tool(self):
        blk = Block(id="mod:ore", name="Ore", mining_speeds={"hoe": 4.0})
        self.assertEqual(blk.mining_speeds, {"hoe": 4.0})

    def test_mining_speeds_all_tools(self):
        speeds = {t: 1.0 for t in VALID_TOOL_TYPES}
        blk = Block(id="mod:ore", name="Ore", mining_speeds=speeds)
        self.assertEqual(set(blk.mining_speeds.keys()), VALID_TOOL_TYPES)

    def test_mining_speeds_invalid_key(self):
        with self.assertRaises(ValueError):
            Block(id="mod:ore", name="Ore", mining_speeds={"hammer": 5.0})

    def test_tool_type_valid(self):
        for t in VALID_TOOL_TYPES:
            blk = Block(id="mod:b", name="B", tool_type=t)
            self.assertEqual(blk.tool_type, t)

    def test_tool_type_invalid(self):
        with self.assertRaises(ValueError):
            Block(id="mod:b", name="B", tool_type="hammer")

    def test_full_mining_config(self):
        """All mining properties together."""
        blk = Block(
            id="mod:ruby_ore",
            name="Ruby Ore",
            hardness=4.0,
            resistance=4.5,
            tool_type="pickaxe",
            mining_level="iron",
            requires_tool=True,
            mining_speeds={"pickaxe": 8.0, "axe": 2.0},
        )
        self.assertEqual(blk.hardness, 4.0)
        self.assertEqual(blk.resistance, 4.5)
        self.assertEqual(blk.tool_type, "pickaxe")
        self.assertEqual(blk.mining_level, "iron")
        self.assertTrue(blk.requires_tool)
        self.assertEqual(blk.mining_speeds, {"pickaxe": 8.0, "axe": 2.0})


# ===================================================================== #
#                   Constants / validation helpers                       #
# ===================================================================== #


class TestMiningConstants(unittest.TestCase):
    """Verify exported constants."""

    def test_valid_tool_types(self):
        self.assertEqual(VALID_TOOL_TYPES, {"pickaxe", "axe", "shovel", "hoe", "sword"})

    def test_valid_mining_levels(self):
        self.assertEqual(VALID_MINING_LEVELS, {"stone", "iron", "diamond"})

    def test_constants_importable_from_package(self):
        from fabricpy import VALID_MINING_LEVELS, VALID_TOOL_TYPES  # noqa: F811

        self.assertIsInstance(VALID_TOOL_TYPES, set)
        self.assertIsInstance(VALID_MINING_LEVELS, set)


# ===================================================================== #
#                   Java code-generation tests                          #
# ===================================================================== #


class TestMiningJavaCodeGen(unittest.TestCase):
    """Test Java code generation for blocks with mining properties."""

    def _make_mod(self, blocks):
        mod = ModConfig(
            mod_id="testmod",
            name="Test Mod",
            description="test",
            version="1.0.0",
            authors=["Tester"],
        )
        for blk in blocks:
            mod.registerBlock(blk)
        return mod

    def _gen_blocks_src(self, mod):
        return mod._tutorial_blocks_src(f"com.example.{mod.mod_id}.blocks")

    # ── strength() property generation ────────────────────────────────── #

    def test_strength_both(self):
        blk = Block(id="testmod:ore", name="Ore", hardness=3.0, resistance=5.0)
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn("BlockBehaviour.Properties.of().strength(3.0f, 5.0f)", src)
        self.assertNotIn("ofFullCopy", src)

    def test_strength_hardness_only(self):
        """When only hardness is given, resistance defaults to 6.0."""
        blk = Block(id="testmod:ore", name="Ore", hardness=2.0)
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn("strength(2.0f, 6.0f)", src)

    def test_strength_resistance_only(self):
        """When only resistance is given, hardness defaults to 1.5."""
        blk = Block(id="testmod:ore", name="Ore", resistance=10.0)
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn("strength(1.5f, 10.0f)", src)

    def test_no_custom_strength_uses_stone_copy(self):
        blk = Block(id="testmod:ore", name="Ore")
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn("ofFullCopy(Blocks.STONE)", src)

    # ── requiresCorrectToolForDrops ───────────────────────────────────── #

    def test_requires_tool_in_props(self):
        blk = Block(id="testmod:ore", name="Ore", requires_tool=True)
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn(".requiresCorrectToolForDrops()", src)

    def test_no_requires_tool(self):
        blk = Block(id="testmod:ore", name="Ore")
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertNotIn("requiresCorrectToolForDrops", src)

    def test_tool_type_infers_requires_tool(self):
        blk = Block(id="testmod:ore", name="Ore", tool_type="pickaxe")
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn(".requiresCorrectToolForDrops()", src)

    # ── mining_speeds factory ─────────────────────────────────────────── #

    def test_mining_speeds_uses_custom_mining_block(self):
        blk = Block(
            id="testmod:ore",
            name="Ore",
            mining_speeds={"pickaxe": 8.0, "shovel": 2.0},
        )
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn("CustomMiningBlock", src)
        self.assertIn('Map.of("pickaxe", 8.0f, "shovel", 2.0f)', src)
        self.assertIn("import java.util.Map;", src)

    def test_no_mining_speeds_uses_custom_block(self):
        blk = Block(id="testmod:ore", name="Ore")
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn("CustomBlock::new", src)
        self.assertNotIn("CustomMiningBlock", src)

    # ── combined properties ───────────────────────────────────────────── #

    def test_full_props_generation(self):
        blk = Block(
            id="testmod:ruby_ore",
            name="Ruby Ore",
            hardness=4.0,
            resistance=4.5,
            tool_type="pickaxe",
            mining_level="iron",
            requires_tool=True,
            mining_speeds={"pickaxe": 8.0},
        )
        src = self._gen_blocks_src(self._make_mod([blk]))
        self.assertIn("strength(4.0f, 4.5f)", src)
        self.assertIn("requiresCorrectToolForDrops", src)
        self.assertIn("CustomMiningBlock", src)


# ===================================================================== #
#               CustomMiningBlock.java generation                       #
# ===================================================================== #


class TestCustomMiningBlockSrc(unittest.TestCase):
    """Tests for the CustomMiningBlock.java output."""

    def _src(self):
        mod = ModConfig(
            mod_id="testmod",
            name="T",
            description="t",
            version="1",
            authors=["x"],
        )
        return mod._custom_mining_block_src("com.example.testmod.blocks")

    def test_class_name(self):
        self.assertIn("public class CustomMiningBlock extends Block", self._src())

    def test_constructor_params(self):
        self.assertIn("Map<String, Float> toolSpeeds", self._src())

    def test_override_get_destroy_progress(self):
        src = self._src()
        self.assertIn("getDestroyProgress", src)
        self.assertIn("player.getDestroySpeed(state)", src)

    def test_tag_checks(self):
        src = self._src()
        for tag in (
            "ItemTags.PICKAXES",
            "ItemTags.AXES",
            "ItemTags.SHOVELS",
            "ItemTags.HOES",
            "ItemTags.SWORDS",
        ):
            self.assertIn(tag, src)

    def test_imports(self):
        src = self._src()
        self.assertIn("import net.minecraft.tags.ItemTags;", src)
        self.assertIn("import java.util.Map;", src)


# ===================================================================== #
#              Block tag file generation (write_block_tags)              #
# ===================================================================== #


class TestBlockTagGeneration(unittest.TestCase):
    """Test write_block_tags output for tool and mining-level tags."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_mod(self, blocks):
        mod = ModConfig(
            mod_id="testmod",
            name="T",
            description="t",
            version="1",
            authors=["x"],
            project_dir=self.tmpdir,
        )
        for blk in blocks:
            mod.registerBlock(blk)
        return mod

    def _tag_path(self, *parts):
        return os.path.join(
            self.tmpdir,
            "src",
            "main",
            "resources",
            "data",
            "minecraft",
            "tags",
            "block",
            *parts,
        )

    def test_tool_type_tag(self):
        blk = Block(id="testmod:ore", name="Ore", tool_type="pickaxe")
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        path = self._tag_path("mineable", "pickaxe.json")
        self.assertTrue(os.path.exists(path))
        data = json.load(open(path))
        self.assertIn("testmod:ore", data["values"])

    def test_mining_speeds_tags(self):
        """mining_speeds keys should each produce a mineable tag file."""
        blk = Block(
            id="testmod:ore",
            name="Ore",
            mining_speeds={"pickaxe": 8.0, "shovel": 2.0},
        )
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        for tool in ("pickaxe", "shovel"):
            path = self._tag_path("mineable", f"{tool}.json")
            self.assertTrue(os.path.exists(path), f"Missing {tool}.json")
            data = json.load(open(path))
            self.assertIn("testmod:ore", data["values"])

    def test_tool_type_and_mining_speeds_merged(self):
        """tool_type and mining_speeds keys together should be a union."""
        blk = Block(
            id="testmod:ore",
            name="Ore",
            tool_type="pickaxe",
            mining_speeds={"axe": 2.0},
        )
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        for tool in ("pickaxe", "axe"):
            path = self._tag_path("mineable", f"{tool}.json")
            self.assertTrue(os.path.exists(path))

    def test_mining_level_tag_stone(self):
        blk = Block(id="testmod:ore", name="Ore", mining_level="stone")
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        path = self._tag_path("needs_stone_tool.json")
        self.assertTrue(os.path.exists(path))
        data = json.load(open(path))
        self.assertIn("testmod:ore", data["values"])

    def test_mining_level_tag_iron(self):
        blk = Block(id="testmod:ore", name="Ore", mining_level="iron")
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        path = self._tag_path("needs_iron_tool.json")
        self.assertTrue(os.path.exists(path))

    def test_mining_level_tag_diamond(self):
        blk = Block(id="testmod:ore", name="Ore", mining_level="diamond")
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        path = self._tag_path("needs_diamond_tool.json")
        self.assertTrue(os.path.exists(path))

    def test_no_tags_when_no_mining_config(self):
        blk = Block(id="testmod:block", name="Block")
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        mineable_dir = self._tag_path("mineable")
        # Directory may or may not exist, but no files should be written
        if os.path.exists(mineable_dir):
            self.assertEqual(os.listdir(mineable_dir), [])

    def test_multiple_blocks_same_tool(self):
        blocks = [
            Block(id="testmod:ore_a", name="Ore A", tool_type="pickaxe"),
            Block(id="testmod:ore_b", name="Ore B", tool_type="pickaxe"),
        ]
        mod = self._make_mod(blocks)
        mod.write_block_tags(self.tmpdir, "testmod")

        path = self._tag_path("mineable", "pickaxe.json")
        data = json.load(open(path))
        self.assertIn("testmod:ore_a", data["values"])
        self.assertIn("testmod:ore_b", data["values"])

    def test_replace_is_false(self):
        """Tags should use 'replace: false' to merge with vanilla/other mods."""
        blk = Block(id="testmod:ore", name="Ore", tool_type="pickaxe")
        mod = self._make_mod([blk])
        mod.write_block_tags(self.tmpdir, "testmod")

        path = self._tag_path("mineable", "pickaxe.json")
        data = json.load(open(path))
        self.assertFalse(data["replace"])


# ===================================================================== #
#            create_block_files generates CustomMiningBlock              #
# ===================================================================== #


class TestCreateBlockFilesWithMining(unittest.TestCase):
    """Verify create_block_files writes CustomMiningBlock.java when needed."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Create the expected directory structure
        java_dir = os.path.join(self.tmpdir, "src", "main", "java")
        os.makedirs(java_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _pkg_dir(self, mod):
        return os.path.join(
            self.tmpdir,
            "src",
            "main",
            "java",
            "com",
            "example",
            mod.mod_id,
            "blocks",
        )

    def test_mining_block_java_created(self):
        mod = ModConfig(
            mod_id="testmod",
            name="T",
            description="t",
            version="1",
            authors=["x"],
            project_dir=self.tmpdir,
        )
        blk = Block(id="testmod:ore", name="Ore", mining_speeds={"pickaxe": 6.0})
        mod.registerBlock(blk)
        mod.create_block_files(self.tmpdir, f"com.example.{mod.mod_id}.blocks")

        mining_path = os.path.join(self._pkg_dir(mod), "CustomMiningBlock.java")
        self.assertTrue(os.path.exists(mining_path))
        src = open(mining_path).read()
        self.assertIn("class CustomMiningBlock", src)

    def test_no_mining_block_without_speeds(self):
        mod = ModConfig(
            mod_id="testmod",
            name="T",
            description="t",
            version="1",
            authors=["x"],
            project_dir=self.tmpdir,
        )
        blk = Block(id="testmod:b", name="B")
        mod.registerBlock(blk)
        mod.create_block_files(self.tmpdir, f"com.example.{mod.mod_id}.blocks")

        mining_path = os.path.join(self._pkg_dir(mod), "CustomMiningBlock.java")
        self.assertFalse(os.path.exists(mining_path))


# ===================================================================== #
#               Backward compatibility tests                            #
# ===================================================================== #


class TestMiningBackwardCompat(unittest.TestCase):
    """Ensure old-style Block usage still works identically."""

    def test_old_style_tool_type_still_works(self):
        blk = Block(id="testmod:ore", name="Ore", tool_type="pickaxe")
        self.assertEqual(blk.tool_type, "pickaxe")
        self.assertTrue(blk.requires_tool)

    def test_old_block_no_mining_attrs(self):
        blk = Block(id="testmod:block", name="Block")
        self.assertIsNone(blk.tool_type)
        self.assertFalse(blk.requires_tool)
        self.assertIsNone(blk.hardness)
        self.assertIsNone(blk.resistance)
        self.assertIsNone(blk.mining_level)
        self.assertIsNone(blk.mining_speeds)

    def test_old_style_generates_ofFullCopy(self):
        mod = ModConfig(
            mod_id="testmod",
            name="T",
            description="t",
            version="1",
            authors=["x"],
        )
        blk = Block(id="testmod:b", name="B")
        mod.registerBlock(blk)
        src = mod._tutorial_blocks_src(f"com.example.{mod.mod_id}.blocks")
        self.assertIn("ofFullCopy(Blocks.STONE)", src)
        self.assertIn("CustomBlock::new", src)


if __name__ == "__main__":
    unittest.main()
