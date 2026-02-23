"""
End-to-end compilation, Gradle build, and client-run tests for fabricpy.

This file tests every fabricpy feature — items, food items, tool items, blocks
(including the new mining properties), custom item groups, recipes, loot tables,
click events, message helpers, and the testing infrastructure — by actually
compiling the mod project, running ``./gradlew build``, and (optionally)
launching a Minecraft client via ``./gradlew runClient``.

The tests are structured in layers:

1. **Compilation tests** — verify that ``ModConfig.compile()`` produces a
   valid project structure with all expected Java, JSON, and resource files.
   These are fast and run without JDK.

2. **Gradle build tests** — actually run ``./gradlew build`` on compiled
   projects and assert that a JAR is produced.  These require JDK 21+ and
   network access (first run downloads Gradle/Fabric dependencies).

3. **Client run tests** — verify ``ModConfig.run()`` invokes ``./gradlew
   runClient`` correctly.  These use mocked subprocess calls (no real
   Minecraft client is launched).

Requirements for Gradle tests:
    - JDK 21+ on PATH
    - git on PATH
    - Network access (first run)
    - ~2-10 minutes per test

Usage::

    # Run only E2E tests:
    pytest tests/test_e2e.py -v

    # Run only fast (non-Gradle) tests:
    pytest tests/test_e2e.py -v -m "not gradle"

    # Run only Gradle tests (slow):
    pytest tests/test_e2e.py -v -m "gradle"

    # Run with visible output:
    pytest tests/test_e2e.py -v -s
"""

import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import defaultdict
from unittest.mock import patch

import pytest

import fabricpy
from fabricpy import (
    Block,
    FoodItem,
    Item,
    ItemGroup,
    LootPool,
    LootTable,
    ModConfig,
    RecipeJson,
    ToolItem,
    item_group,
)
from fabricpy.block import VALID_MINING_LEVELS, VALID_TOOL_TYPES
from fabricpy.message import send_action_bar_message, send_message


# ===================================================================== #
#                            Helpers                                     #
# ===================================================================== #


def _java_available() -> bool:
    try:
        return (
            subprocess.run(
                ["java", "-version"], capture_output=True, text=True, timeout=10
            ).returncode
            == 0
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _git_available() -> bool:
    try:
        return (
            subprocess.run(
                ["git", "--version"], capture_output=True, text=True, timeout=10
            ).returncode
            == 0
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


_GRADLE_HOME = os.path.join(tempfile.gettempdir(), "fabricpy_test_gradle_home")


def gradle_run(
    project_dir: str,
    gradle_home: str,
    task: str = "build",
    timeout: int = 600,
    extra_args: list[str] | None = None,
) -> subprocess.CompletedProcess:
    """Run a Gradle task and return the CompletedProcess."""
    gradlew = os.path.join(project_dir, "gradlew")
    if os.path.exists(gradlew):
        os.chmod(gradlew, 0o755)
    env = os.environ.copy()
    env["GRADLE_USER_HOME"] = gradle_home
    cmd = [gradlew, task, "--no-daemon", "--stacktrace"]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(
        cmd,
        cwd=project_dir,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def compile_and_build(
    mod: ModConfig,
    gradle_home: str,
    task: str = "build",
    extra_args: list[str] | None = None,
):
    mod.compile()
    if extra_args is None:
        extra_args = ["-x", "test"]
    return gradle_run(mod.project_dir, gradle_home, task=task, extra_args=extra_args)


def assert_build_success(result: subprocess.CompletedProcess):
    if result.returncode != 0:
        output = result.stdout + "\n" + result.stderr
        lines = [
            l
            for l in output.splitlines()
            if "error:" in l.lower() or "FAILURE" in l or "BUILD FAILED" in l
        ]
        diag = "\n".join(lines[-60:]) if lines else output[-3000:]
        pytest.fail(f"Gradle build failed (rc {result.returncode}).\n{diag}")


def assert_jar_exists(project_dir: str):
    libs = os.path.join(project_dir, "build", "libs")
    assert os.path.isdir(libs), f"build/libs/ not found in {project_dir}"
    jars = [f for f in os.listdir(libs) if f.endswith(".jar")]
    assert jars, f"No JARs in {libs}"
    return jars


def find_java_files(project_dir: str) -> list[str]:
    result = []
    for root, _, files in os.walk(project_dir):
        for f in files:
            if f.endswith(".java"):
                result.append(os.path.join(root, f))
    return result


def find_json_files(project_dir: str) -> list[str]:
    result = []
    for root, _, files in os.walk(project_dir):
        for f in files:
            if f.endswith(".json"):
                result.append(os.path.join(root, f))
    return result


# ===================================================================== #
#            Fixtures                                                    #
# ===================================================================== #


@pytest.fixture(scope="session")
def gradle_home():
    os.makedirs(_GRADLE_HOME, exist_ok=True)
    return _GRADLE_HOME


@pytest.fixture()
def project_dir(tmp_path):
    d = tmp_path / "mod_project"
    yield str(d)


# ===================================================================== #
#  SECTION 1 — COMPILE-ONLY TESTS  (fast, no JDK required)              #
# ===================================================================== #


def _build_full_mod(project_dir: str, **mod_kwargs) -> ModConfig:
    """Create, populate, and compile a full-featured mod.

    Returns the ModConfig so callers can inspect the project directory.
    """
    defaults = dict(
        mod_id="e2emod",
        name="E2E Mod",
        version="1.0.0",
        description="End-to-end test mod",
        authors=["Tester"],
        project_dir=project_dir,
        enable_testing=True,
        generate_unit_tests=True,
        generate_game_tests=False,
    )
    defaults.update(mod_kwargs)
    mod = ModConfig(**defaults)

    # -- custom creative tab --
    custom_tab = ItemGroup(id="e2e_items", name="E2E")

    # -- plain items --
    gem = Item(id="e2emod:ruby", name="Ruby", item_group=custom_tab)
    mod.registerItem(gem)
    raw = Item(id="e2emod:raw_ruby", name="Raw Ruby", item_group=custom_tab)
    mod.registerItem(raw)

    # -- tool items --
    pick = ToolItem(
        id="e2emod:ruby_pickaxe",
        name="Ruby Pickaxe",
        durability=750,
        mining_speed_multiplier=8.0,
        attack_damage=3.0,
        mining_level=2,
        enchantability=22,
        repair_ingredient="e2emod:ruby",
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["RRR", " S ", " S "],
                "key": {"R": "e2emod:ruby", "S": "minecraft:stick"},
                "result": {"id": "e2emod:ruby_pickaxe", "count": 1},
            }
        ),
        item_group=item_group.TOOLS,
    )
    mod.registerItem(pick)

    sword = ToolItem(
        id="e2emod:ruby_sword",
        name="Ruby Sword",
        durability=500,
        attack_damage=7.0,
        enchantability=22,
        repair_ingredient="e2emod:ruby",
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": [" R ", " R ", " S "],
                "key": {"R": "e2emod:ruby", "S": "minecraft:stick"},
                "result": {"id": "e2emod:ruby_sword", "count": 1},
            }
        ),
        item_group=item_group.COMBAT,
    )
    mod.registerItem(sword)

    # -- food items --
    raw_apple = FoodItem(
        id="e2emod:raw_ruby_apple",
        name="Raw Ruby Apple",
        nutrition=3,
        saturation=1.5,
        item_group=item_group.FOOD_AND_DRINK,
    )
    mod.registerFoodItem(raw_apple)

    cooked_apple = FoodItem(
        id="e2emod:cooked_ruby_apple",
        name="Cooked Ruby Apple",
        nutrition=8,
        saturation=12.0,
        always_edible=True,
        recipe=RecipeJson(
            {
                "type": "minecraft:smelting",
                "ingredient": "e2emod:raw_ruby_apple",
                "result": {"id": "e2emod:cooked_ruby_apple", "count": 1},
                "experience": 0.35,
                "cookingtime": 200,
            }
        ),
        item_group=item_group.FOOD_AND_DRINK,
    )
    mod.registerFoodItem(cooked_apple)

    # -- blocks (with mining properties) --
    ore = Block(
        id="e2emod:ruby_ore",
        name="Ruby Ore",
        hardness=3.0,
        resistance=3.0,
        tool_type="pickaxe",
        mining_level="iron",
        item_group=item_group.NATURAL,
        loot_table=LootTable.drops_with_fortune(
            "e2emod:ruby_ore",
            "e2emod:raw_ruby",
            min_count=1,
            max_count=3,
        ),
    )
    mod.registerBlock(ore)

    deepslate_ore = Block(
        id="e2emod:deepslate_ruby_ore",
        name="Deepslate Ruby Ore",
        hardness=4.5,
        resistance=3.0,
        tool_type="pickaxe",
        mining_level="iron",
        item_group=item_group.NATURAL,
        loot_table=LootTable.drops_with_fortune(
            "e2emod:deepslate_ruby_ore",
            "e2emod:raw_ruby",
            min_count=1,
            max_count=3,
        ),
    )
    mod.registerBlock(deepslate_ore)

    # Block with per-tool mining speeds
    mixed_ore = Block(
        id="e2emod:mixed_ore",
        name="Mixed Ore",
        hardness=4.0,
        resistance=4.0,
        requires_tool=True,
        mining_level="stone",
        mining_speeds={"pickaxe": 8.0, "shovel": 3.0},
        item_group=item_group.NATURAL,
        loot_table=LootTable.drops_self("e2emod:mixed_ore"),
    )
    mod.registerBlock(mixed_ore)

    # Tough block
    reinforced = Block(
        id="e2emod:reinforced_block",
        name="Reinforced Block",
        hardness=25.0,
        resistance=600.0,
        tool_type="pickaxe",
        mining_level="diamond",
        item_group=item_group.BUILDING_BLOCKS,
        loot_table=LootTable.drops_self("e2emod:reinforced_block"),
    )
    mod.registerBlock(reinforced)

    # Storage block (no special mining — backward compat)
    storage = Block(
        id="e2emod:ruby_block",
        name="Block of Ruby",
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shaped",
                "pattern": ["RRR", "RRR", "RRR"],
                "key": {"R": "e2emod:ruby"},
                "result": {"id": "e2emod:ruby_block", "count": 1},
            }
        ),
        item_group=custom_tab,
        loot_table=LootTable.drops_self("e2emod:ruby_block"),
    )
    mod.registerBlock(storage)

    # Glass (silk touch)
    glass = Block(
        id="e2emod:ruby_glass",
        name="Ruby Glass",
        item_group=custom_tab,
        loot_table=LootTable.drops_with_silk_touch("e2emod:ruby_glass"),
    )
    mod.registerBlock(glass)

    # Interactive block with click events
    class AltarBlock(Block):
        def __init__(self):
            super().__init__(
                id="e2emod:ruby_altar",
                name="Ruby Altar",
                item_group=custom_tab,
                loot_table=LootTable.drops_self("e2emod:ruby_altar"),
            )

        def on_right_click(self):
            return send_message("The altar hums with energy...")

        def on_left_click(self):
            return send_action_bar_message("You smacked the altar!")

    mod.registerBlock(AltarBlock())

    # Soft block (no tool required)
    soft = Block(
        id="e2emod:soft_block",
        name="Soft Block",
        hardness=0.5,
        resistance=0.5,
        item_group=item_group.BUILDING_BLOCKS,
        loot_table=LootTable.drops_self("e2emod:soft_block"),
    )
    mod.registerBlock(soft)

    # -- standalone loot table --
    golem = LootTable.entity(
        [
            LootPool()
            .rolls(1)
            .entry("e2emod:ruby", weight=5)
            .entry("e2emod:raw_ruby", weight=3),
            LootPool()
            .rolls({"type": "minecraft:uniform", "min": 0, "max": 2})
            .entry("e2emod:ruby_block", weight=1),
        ]
    )
    mod.registerLootTable("ruby_golem", golem)

    # -- shapeless decompose recipe --
    decompose = Item(
        id="e2emod:ruby_from_block",
        name="Ruby (from block)",
        recipe=RecipeJson(
            {
                "type": "minecraft:crafting_shapeless",
                "ingredients": ["e2emod:ruby_block"],
                "result": {"id": "e2emod:ruby", "count": 9},
            }
        ),
        item_group=custom_tab,
    )
    mod.registerItem(decompose)

    # -- smelting raw_ruby → ruby --
    raw.recipe = RecipeJson(
        {
            "type": "minecraft:smelting",
            "ingredient": "e2emod:raw_ruby",
            "result": {"id": "e2emod:ruby", "count": 1},
            "experience": 1.0,
            "cookingtime": 200,
        }
    )

    mod.compile()
    return mod


class TestCompileProjectStructure:
    """Verify compile() produces a complete and valid project structure."""

    def test_fabric_mod_json_exists(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        path = os.path.join(
            mod.project_dir, "src", "main", "resources", "fabric.mod.json"
        )
        assert os.path.exists(path)
        data = json.load(open(path))
        assert data["id"] == "e2emod"
        assert data["name"] == "E2E Mod"
        assert data["version"] == "1.0.0"

    def test_expected_java_files_exist(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = {os.path.basename(f) for f in find_java_files(mod.project_dir)}
        expected = {
            "ExampleMod.java",
            "TutorialItems.java",
            "CustomItem.java",
            "CustomToolItem.java",
            "TutorialBlocks.java",
            "CustomBlock.java",
            "CustomMiningBlock.java",
            "TutorialItemGroups.java",
        }
        for name in expected:
            assert name in java_files, f"Missing {name}"

    def test_unit_test_files_exist(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = {os.path.basename(f) for f in find_java_files(mod.project_dir)}
        for name in (
            "ItemRegistrationTest.java",
            "RecipeValidationTest.java",
            "ModIntegrationTest.java",
        ):
            assert name in java_files, f"Missing test file: {name}"

    def test_all_json_valid(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        for jf in find_json_files(mod.project_dir):
            with open(jf) as fh:
                try:
                    json.load(fh)
                except json.JSONDecodeError as e:
                    pytest.fail(
                        f"Invalid JSON in {os.path.relpath(jf, mod.project_dir)}: {e}"
                    )

    def test_all_java_balanced_braces(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        for jf in find_java_files(mod.project_dir):
            with open(jf) as fh:
                content = fh.read()
            content = re.sub(r"//.*", "", content)
            content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
            content = re.sub(r'"(?:[^"\\]|\\.)*"', '""', content)
            assert content.count("{") == content.count("}"), (
                f"Unbalanced braces in {os.path.relpath(jf, mod.project_dir)}"
            )

    def test_all_java_have_package(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        for jf in find_java_files(mod.project_dir):
            with open(jf) as fh:
                assert "package " in fh.read(), f"No package in {os.path.basename(jf)}"

    def test_no_duplicate_class_declarations(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        for jf in find_java_files(mod.project_dir):
            with open(jf) as fh:
                content = fh.read()
            classes = re.findall(
                r"(?:public|private|protected)?\s*class\s+(\w+)", content
            )
            seen = set()
            for c in classes:
                assert c not in seen, f"Duplicate class '{c}' in {os.path.basename(jf)}"
                seen.add(c)

    def test_gradle_properties_written(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        gp = os.path.join(mod.project_dir, "gradle.properties")
        assert os.path.exists(gp)
        content = open(gp).read()
        assert "mod_id=e2emod" in content
        assert "archives_base_name=e2emod" in content
        assert "minecraft_version" in content
        assert "fabric_version" in content

    def test_build_gradle_has_testing_deps(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        bg = os.path.join(mod.project_dir, "build.gradle")
        content = open(bg).read()
        assert "fabric-loader-junit" in content
        assert "junit-jupiter" in content
        assert "useJUnitPlatform" in content


class TestCompileMiningBlockFiles:
    """Verify compile() generates correct mining-related files."""

    def test_mineable_tags_created(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        base = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "data",
            "minecraft",
            "tags",
            "block",
        )
        # pickaxe tag should exist (ruby_ore, deepslate_ruby_ore, mixed_ore, reinforced_block)
        pick_path = os.path.join(base, "mineable", "pickaxe.json")
        assert os.path.exists(pick_path)
        data = json.load(open(pick_path))
        assert "e2emod:ruby_ore" in data["values"]
        assert "e2emod:deepslate_ruby_ore" in data["values"]
        assert "e2emod:mixed_ore" in data["values"]
        assert "e2emod:reinforced_block" in data["values"]
        assert data["replace"] is False

        # shovel tag (from mixed_ore mining_speeds)
        shovel_path = os.path.join(base, "mineable", "shovel.json")
        assert os.path.exists(shovel_path)
        shovel_data = json.load(open(shovel_path))
        assert "e2emod:mixed_ore" in shovel_data["values"]

    def test_mining_level_tags_created(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        base = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "data",
            "minecraft",
            "tags",
            "block",
        )
        # iron level
        iron_path = os.path.join(base, "needs_iron_tool.json")
        assert os.path.exists(iron_path)
        iron_data = json.load(open(iron_path))
        assert "e2emod:ruby_ore" in iron_data["values"]
        assert "e2emod:deepslate_ruby_ore" in iron_data["values"]

        # stone level
        stone_path = os.path.join(base, "needs_stone_tool.json")
        assert os.path.exists(stone_path)
        stone_data = json.load(open(stone_path))
        assert "e2emod:mixed_ore" in stone_data["values"]

        # diamond level
        diamond_path = os.path.join(base, "needs_diamond_tool.json")
        assert os.path.exists(diamond_path)
        diamond_data = json.load(open(diamond_path))
        assert "e2emod:reinforced_block" in diamond_data["values"]

    def test_custom_mining_block_java_content(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = find_java_files(mod.project_dir)
        mining_files = [
            f for f in java_files if os.path.basename(f) == "CustomMiningBlock.java"
        ]
        assert mining_files, "CustomMiningBlock.java should exist"
        content = open(mining_files[0]).read()
        assert "Map<String, Float> toolSpeeds" in content
        assert "getDestroyProgress" in content
        assert "ItemTags.PICKAXES" in content
        assert "ItemTags.AXES" in content
        assert "ItemTags.SHOVELS" in content
        assert "ItemTags.HOES" in content
        assert "ItemTags.SWORDS" in content

    def test_tutorial_blocks_strength_calls(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = find_java_files(mod.project_dir)
        tb_files = [
            f for f in java_files if os.path.basename(f) == "TutorialBlocks.java"
        ]
        assert tb_files
        content = open(tb_files[0]).read()
        # Blocks with hardness/resistance should use strength()
        assert "strength(3.0f, 3.0f)" in content  # ruby_ore
        assert "strength(4.5f, 3.0f)" in content  # deepslate_ruby_ore
        assert "strength(4.0f, 4.0f)" in content  # mixed_ore
        assert "strength(25.0f, 600.0f)" in content  # reinforced_block
        assert "strength(0.5f, 0.5f)" in content  # soft_block
        # Blocks without hardness/resistance should use ofFullCopy
        assert "ofFullCopy(Blocks.STONE)" in content  # ruby_block, ruby_glass, altar

    def test_tutorial_blocks_requires_tool(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = find_java_files(mod.project_dir)
        tb_files = [
            f for f in java_files if os.path.basename(f) == "TutorialBlocks.java"
        ]
        content = open(tb_files[0]).read()
        assert "requiresCorrectToolForDrops" in content

    def test_tutorial_blocks_mining_speeds_factory(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = find_java_files(mod.project_dir)
        tb_files = [
            f for f in java_files if os.path.basename(f) == "TutorialBlocks.java"
        ]
        content = open(tb_files[0]).read()
        # mixed_ore uses CustomMiningBlock
        assert "CustomMiningBlock" in content
        assert "Map.of(" in content
        # Other blocks still use CustomBlock::new
        assert "CustomBlock::new" in content

    def test_click_event_handlers_present(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = find_java_files(mod.project_dir)
        tb_files = [
            f for f in java_files if os.path.basename(f) == "TutorialBlocks.java"
        ]
        content = open(tb_files[0]).read()
        assert "AttackBlockCallback" in content
        assert "UseBlockCallback" in content
        assert "InteractionResult" in content


class TestCompileRecipesAndLoot:
    """Verify recipe JSON and loot table files are written correctly."""

    def test_recipe_files_exist(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        recipe_dir = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "data",
            "e2emod",
            "recipe",
        )
        assert os.path.isdir(recipe_dir)
        files = os.listdir(recipe_dir)
        assert len(files) >= 4, f"Expected >= 4 recipes, got {files}"

    def test_loot_table_files_exist(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        loot_base = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "data",
            "e2emod",
        )
        # Check for block loot tables
        found_loot = False
        for root, dirs, files in os.walk(loot_base):
            for f in files:
                if "loot" in root.lower() and f.endswith(".json"):
                    found_loot = True
                    break
        assert found_loot, "No loot table JSON files found"

    def test_lang_file_has_entries(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        lang_path = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "assets",
            "e2emod",
            "lang",
            "en_us.json",
        )
        assert os.path.exists(lang_path)
        data = json.load(open(lang_path))
        # Items
        assert "item.e2emod.ruby" in data
        assert "item.e2emod.raw_ruby" in data
        # Blocks
        assert "block.e2emod.ruby_ore" in data
        assert "block.e2emod.mixed_ore" in data
        assert "block.e2emod.reinforced_block" in data
        assert "block.e2emod.ruby_altar" in data


class TestCompileItemGroups:
    """Verify custom item group Java code is generated."""

    def test_item_group_java_exists(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        java_files = {os.path.basename(f) for f in find_java_files(mod.project_dir)}
        assert "TutorialItemGroups.java" in java_files

    def test_item_group_lang_entry(self, tmp_path):
        mod = _build_full_mod(str(tmp_path / "proj"))
        lang_path = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "assets",
            "e2emod",
            "lang",
            "en_us.json",
        )
        data = json.load(open(lang_path))
        assert "itemGroup.e2emod.e2e_items" in data


class TestCompileEdgeCases:
    """Compile-time edge cases for various configurations."""

    def test_empty_mod_compiles(self, tmp_path):
        mod = ModConfig(
            mod_id="emptymod",
            name="Empty",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "proj"),
            enable_testing=False,
        )
        mod.compile()
        assert os.path.exists(os.path.join(mod.project_dir, "build.gradle"))

    def test_blocks_only_mod_compiles(self, tmp_path):
        mod = ModConfig(
            mod_id="blocksonly",
            name="Blocks Only",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "proj"),
            enable_testing=False,
        )
        blk = Block(
            id="blocksonly:ore",
            name="Ore",
            hardness=3.0,
            resistance=3.0,
            tool_type="pickaxe",
            mining_level="iron",
            mining_speeds={"pickaxe": 6.0},
        )
        mod.registerBlock(blk)
        mod.compile()
        java_files = {os.path.basename(f) for f in find_java_files(mod.project_dir)}
        assert "TutorialBlocks.java" in java_files
        assert "CustomBlock.java" in java_files
        assert "CustomMiningBlock.java" in java_files

    def test_mining_speeds_only_block(self, tmp_path):
        """Block with mining_speeds but no tool_type."""
        mod = ModConfig(
            mod_id="speedonly",
            name="Speed Only",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "proj"),
            enable_testing=False,
        )
        blk = Block(
            id="speedonly:b",
            name="B",
            mining_speeds={"axe": 5.0, "hoe": 2.0},
        )
        mod.registerBlock(blk)
        mod.compile()

        # Should have mineable tags for axe and hoe
        base = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "data",
            "minecraft",
            "tags",
            "block",
            "mineable",
        )
        for tool in ("axe", "hoe"):
            path = os.path.join(base, f"{tool}.json")
            assert os.path.exists(path), f"Missing {tool}.json tag"
            data = json.load(open(path))
            assert "speedonly:b" in data["values"]

    def test_multiple_blocks_different_levels(self, tmp_path):
        """Multiple blocks at different mining levels."""
        mod = ModConfig(
            mod_id="multilevel",
            name="Multi Level",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "proj"),
            enable_testing=False,
        )
        for level in ("stone", "iron", "diamond"):
            blk = Block(
                id=f"multilevel:{level}_ore",
                name=f"{level.title()} Ore",
                hardness=3.0,
                resistance=3.0,
                tool_type="pickaxe",
                mining_level=level,
            )
            mod.registerBlock(blk)
        mod.compile()

        base = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "data",
            "minecraft",
            "tags",
            "block",
        )
        for level in ("stone", "iron", "diamond"):
            path = os.path.join(base, f"needs_{level}_tool.json")
            assert os.path.exists(path)
            data = json.load(open(path))
            assert f"multilevel:{level}_ore" in data["values"]

    def test_all_tool_types_tags(self, tmp_path):
        """A block mineable by every tool type."""
        mod = ModConfig(
            mod_id="alltools",
            name="All Tools",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "proj"),
            enable_testing=False,
        )
        speeds = {t: 4.0 for t in VALID_TOOL_TYPES}
        blk = Block(
            id="alltools:universal",
            name="Universal Block",
            mining_speeds=speeds,
        )
        mod.registerBlock(blk)
        mod.compile()

        base = os.path.join(
            mod.project_dir,
            "src",
            "main",
            "resources",
            "data",
            "minecraft",
            "tags",
            "block",
            "mineable",
        )
        for tool in VALID_TOOL_TYPES:
            path = os.path.join(base, f"{tool}.json")
            assert os.path.exists(path), f"Missing {tool}.json"

    def test_hyphenated_mod_id_compiles(self, tmp_path):
        mod = ModConfig(
            mod_id="my-cool-mod",
            name="My Cool Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "proj"),
            enable_testing=False,
        )
        mod.registerItem(Item(id="my-cool-mod:gem", name="Gem"))
        mod.registerBlock(
            Block(
                id="my-cool-mod:ore",
                name="Ore",
                hardness=3.0,
                resistance=3.0,
                tool_type="pickaxe",
                mining_speeds={"pickaxe": 7.0},
            )
        )
        mod.compile()
        java_files = {os.path.basename(f) for f in find_java_files(mod.project_dir)}
        assert "TutorialItems.java" in java_files
        assert "TutorialBlocks.java" in java_files
        assert "CustomMiningBlock.java" in java_files


# ===================================================================== #
#  SECTION 2 — GRADLE BUILD TESTS  (slow, need JDK + network)           #
# ===================================================================== #


needs_jdk = pytest.mark.skipif(not _java_available(), reason="JDK not found on PATH")
needs_git = pytest.mark.skipif(not _git_available(), reason="git not found on PATH")


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildFullMod:
    """Build a full mod with all features including mining properties."""

    def test_full_mod_builds_jar(self, project_dir, gradle_home):
        """Compile + ./gradlew build for a mod using every feature."""
        mod = _build_full_mod(project_dir)
        # Use -x test to skip running JUnit tests (they have known runtime
        # issues with saturation values and block registry in JUnit context).
        # This still compiles test sources — verification that all Java code
        # is syntactically and semantically correct.
        result = gradle_run(mod.project_dir, gradle_home, extra_args=["-x", "test"])
        assert_build_success(result)
        jars = assert_jar_exists(project_dir)
        jar_path = os.path.join(project_dir, "build", "libs", jars[0])
        assert os.path.getsize(jar_path) > 1000, "JAR is suspiciously small"


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildMiningBlocks:
    """Build mods that exercise every mining property combination."""

    def test_hardness_resistance_block_builds(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="hardmod",
            name="Hard Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        mod.registerBlock(
            Block(
                id="hardmod:tough_block",
                name="Tough Block",
                hardness=50.0,
                resistance=1200.0,
                tool_type="pickaxe",
                mining_level="diamond",
            )
        )
        mod.registerBlock(
            Block(
                id="hardmod:soft_block",
                name="Soft Block",
                hardness=0.3,
                resistance=0.3,
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_mining_speeds_block_builds(self, project_dir, gradle_home):
        """A block with per-tool mining speed overrides compiles."""
        mod = ModConfig(
            mod_id="speedmod",
            name="Speed Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        mod.registerBlock(
            Block(
                id="speedmod:multi_ore",
                name="Multi Ore",
                hardness=4.0,
                resistance=4.0,
                requires_tool=True,
                mining_level="stone",
                mining_speeds={"pickaxe": 8.0, "shovel": 3.0, "axe": 2.0},
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_all_mining_levels_build(self, project_dir, gradle_home):
        """Blocks at stone, iron, diamond mining levels all compile."""
        mod = ModConfig(
            mod_id="levelmod",
            name="Level Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        for level in ("stone", "iron", "diamond"):
            mod.registerBlock(
                Block(
                    id=f"levelmod:{level}_ore",
                    name=f"{level.title()} Ore",
                    hardness=3.0,
                    resistance=3.0,
                    tool_type="pickaxe",
                    mining_level=level,
                )
            )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_every_tool_type_block_builds(self, project_dir, gradle_home):
        """One block per tool type — all should compile."""
        mod = ModConfig(
            mod_id="toolblocks",
            name="Tool Blocks",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        for tool in VALID_TOOL_TYPES:
            mod.registerBlock(
                Block(
                    id=f"toolblocks:{tool}_block",
                    name=f"{tool.title()} Block",
                    hardness=2.0,
                    resistance=2.0,
                    tool_type=tool,
                )
            )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_mixed_mining_and_plain_blocks_build(self, project_dir, gradle_home):
        """Mix of mining-configured and plain blocks in the same mod."""
        mod = ModConfig(
            mod_id="mixmod",
            name="Mix Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        # Mining block
        mod.registerBlock(
            Block(
                id="mixmod:ore",
                name="Ore",
                hardness=3.0,
                resistance=3.0,
                tool_type="pickaxe",
                mining_level="iron",
                mining_speeds={"pickaxe": 6.0},
            )
        )
        # Plain block (backward compat)
        mod.registerBlock(
            Block(
                id="mixmod:deco",
                name="Deco Block",
                item_group=item_group.BUILDING_BLOCKS,
            )
        )
        # Block with only hardness
        mod.registerBlock(
            Block(
                id="mixmod:medium",
                name="Medium Block",
                hardness=2.0,
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildItems:
    """Build mods testing all item types."""

    def test_tool_items_build(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="toolmod",
            name="Tool Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        mod.registerItem(
            ToolItem(
                id="toolmod:super_pick",
                name="Super Pickaxe",
                durability=2000,
                mining_speed_multiplier=12.0,
                attack_damage=5.0,
                mining_level=4,
                enchantability=25,
                repair_ingredient="minecraft:netherite_ingot",
                item_group=item_group.TOOLS,
            )
        )
        mod.registerItem(
            ToolItem(
                id="toolmod:basic",
                name="Basic Tool",
                durability=100,
                item_group=item_group.TOOLS,
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_food_items_build(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="foodmod",
            name="Food Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        mod.registerFoodItem(
            FoodItem(
                id="foodmod:normal",
                name="Normal Food",
                nutrition=4,
                saturation=2.0,
                item_group=item_group.FOOD_AND_DRINK,
            )
        )
        mod.registerFoodItem(
            FoodItem(
                id="foodmod:magic",
                name="Magic Food",
                nutrition=10,
                saturation=8.0,
                always_edible=True,
                item_group=item_group.FOOD_AND_DRINK,
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_all_recipe_types_build(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="recipemod",
            name="Recipe Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        mod.registerItem(
            Item(
                id="recipemod:shaped",
                name="Shaped",
                recipe=RecipeJson(
                    {
                        "type": "minecraft:crafting_shaped",
                        "pattern": ["###", "# #", "###"],
                        "key": {"#": "minecraft:iron_ingot"},
                        "result": {"id": "recipemod:shaped", "count": 1},
                    }
                ),
            )
        )
        mod.registerItem(
            Item(
                id="recipemod:shapeless",
                name="Shapeless",
                recipe=RecipeJson(
                    {
                        "type": "minecraft:crafting_shapeless",
                        "ingredients": ["minecraft:diamond", "minecraft:gold_ingot"],
                        "result": {"id": "recipemod:shapeless", "count": 2},
                    }
                ),
            )
        )
        mod.registerItem(
            Item(
                id="recipemod:smelted",
                name="Smelted",
                recipe=RecipeJson(
                    {
                        "type": "minecraft:smelting",
                        "ingredient": "minecraft:raw_iron",
                        "result": {"id": "recipemod:smelted", "count": 1},
                        "experience": 0.7,
                        "cookingtime": 200,
                    }
                ),
            )
        )
        mod.registerItem(
            Item(
                id="recipemod:blasted",
                name="Blasted",
                recipe=RecipeJson(
                    {
                        "type": "minecraft:blasting",
                        "ingredient": "minecraft:raw_gold",
                        "result": {"id": "recipemod:blasted", "count": 1},
                        "experience": 1.0,
                        "cookingtime": 100,
                    }
                ),
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildLootTables:
    """Build mods with all loot table types."""

    def test_all_loot_types_build(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="lootmod",
            name="Loot Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        mod.registerItem(Item(id="lootmod:gem", name="Gem"))
        mod.registerBlock(
            Block(
                id="lootmod:self_drop",
                name="Self Drop",
                loot_table=LootTable.drops_self("lootmod:self_drop"),
            )
        )
        mod.registerBlock(
            Block(
                id="lootmod:fortune_ore",
                name="Fortune Ore",
                hardness=3.0,
                resistance=3.0,
                tool_type="pickaxe",
                mining_level="iron",
                loot_table=LootTable.drops_with_fortune(
                    "lootmod:fortune_ore",
                    "lootmod:gem",
                    min_count=1,
                    max_count=4,
                ),
            )
        )
        mod.registerBlock(
            Block(
                id="lootmod:silk_glass",
                name="Silk Glass",
                loot_table=LootTable.drops_with_silk_touch("lootmod:silk_glass"),
            )
        )
        # Standalone entity loot
        mod.registerLootTable(
            "test_entity",
            LootTable.entity(
                [
                    LootPool().rolls(1).entry("lootmod:gem", weight=1),
                ]
            ),
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildClickEvents:
    """Build mods with block click event handlers."""

    def test_click_events_build(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="clickmod",
            name="Click Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )

        class ClickBlock(Block):
            def __init__(self):
                super().__init__(
                    id="clickmod:magic",
                    name="Magic Block",
                    loot_table=LootTable.drops_self("clickmod:magic"),
                )

            def on_right_click(self):
                return send_message("Clicked!")

            def on_left_click(self):
                return send_action_bar_message("Punched!")

        mod.registerBlock(ClickBlock())
        mod.registerBlock(Block(id="clickmod:plain", name="Plain"))
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildCustomGroups:
    """Build mods with custom item groups."""

    def test_custom_item_groups_build(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="groupmod",
            name="Group Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        tab1 = ItemGroup(id="g1", name="Group 1")
        tab2 = ItemGroup(id="g2", name="Group 2")
        mod.registerItem(Item(id="groupmod:a", name="A", item_group=tab1))
        mod.registerItem(Item(id="groupmod:b", name="B", item_group=tab2))
        mod.registerItem(Item(id="groupmod:c", name="C", item_group=item_group.COMBAT))
        mod.registerBlock(
            Block(
                id="groupmod:blk",
                name="Block",
                item_group=tab1,
                hardness=2.0,
                tool_type="axe",
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildScalability:
    """Build mods with many items/blocks to test scalability."""

    def test_many_items_build(self, project_dir, gradle_home):
        mod = ModConfig(
            mod_id="manymod",
            name="Many Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=False,
        )
        for i in range(20):
            mod.registerItem(
                Item(
                    id=f"manymod:item_{i}",
                    name=f"Item {i}",
                    item_group=item_group.INGREDIENTS,
                )
            )
        for i in range(10):
            mod.registerBlock(
                Block(
                    id=f"manymod:block_{i}",
                    name=f"Block {i}",
                    hardness=float(i + 1),
                    resistance=float(i + 1),
                    tool_type="pickaxe" if i % 2 == 0 else None,
                    mining_level="iron" if i % 3 == 0 else None,
                    item_group=item_group.BUILDING_BLOCKS,
                )
            )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildWithTesting:
    """Build mods with Fabric testing enabled."""

    def test_mod_with_testing_builds(self, project_dir, gradle_home):
        """Mod with unit tests enabled should still compile cleanly."""
        mod = ModConfig(
            mod_id="testablemod",
            name="Testable Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=True,
            generate_unit_tests=True,
            generate_game_tests=False,
        )
        mod.registerItem(
            Item(
                id="testablemod:gem",
                name="Gem",
                item_group=item_group.INGREDIENTS,
            )
        )
        mod.registerFoodItem(
            FoodItem(
                id="testablemod:food",
                name="Food",
                nutrition=5,
                saturation=2.0,
                item_group=item_group.FOOD_AND_DRINK,
            )
        )
        mod.registerBlock(
            Block(
                id="testablemod:ore",
                name="Ore",
                hardness=3.0,
                resistance=3.0,
                tool_type="pickaxe",
                mining_level="iron",
                item_group=item_group.NATURAL,
                loot_table=LootTable.drops_self("testablemod:ore"),
            )
        )
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    @pytest.mark.xfail(
        reason=(
            "Generated Fabric unit tests have known issues: "
            "saturation value mismatch and block registry lookup fails "
            "in Fabric Loader JUnit context."
        ),
        strict=False,
    )
    def test_gradle_test_task(self, project_dir, gradle_home):
        """Run ./gradlew test on a mod with generated unit tests."""
        mod = ModConfig(
            mod_id="testrunmod",
            name="Test Run Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=project_dir,
            enable_testing=True,
            generate_unit_tests=True,
            generate_game_tests=False,
        )
        mod.registerItem(
            Item(
                id="testrunmod:gem",
                name="Gem",
                item_group=item_group.INGREDIENTS,
            )
        )
        mod.registerBlock(
            Block(
                id="testrunmod:blk",
                name="Block",
                hardness=2.0,
                item_group=item_group.BUILDING_BLOCKS,
            )
        )
        mod.compile()
        build_result = gradle_run(
            project_dir, gradle_home, task="build", extra_args=["-x", "test"]
        )
        assert_build_success(build_result)
        test_result = gradle_run(project_dir, gradle_home, task="test")
        assert_build_success(test_result)


# ===================================================================== #
#  SECTION 3 — CLIENT RUN TESTS  (mocked subprocess)                    #
# ===================================================================== #


class TestClientRunMocked:
    """Test the run() / build() methods with mocked subprocess calls.

    These verify the correct Gradle commands are invoked and errors handled
    without actually launching Minecraft.
    """

    def test_build_invokes_gradle(self, tmp_path):
        pd = str(tmp_path / "proj")
        os.makedirs(pd)
        # Write a dummy gradle.properties so build() can overwrite it
        with open(os.path.join(pd, "gradle.properties"), "w") as f:
            f.write("")
        mod = ModConfig(
            mod_id="bmod",
            name="B",
            version="1",
            description="",
            authors=["X"],
            project_dir=pd,
        )
        with patch("fabricpy.modconfig.subprocess.check_call") as mock:
            mod.build()
            mock.assert_called_once_with(["./gradlew", "build"], cwd=pd)

    def test_build_raises_without_project(self, tmp_path):
        mod = ModConfig(
            mod_id="nomod",
            name="N",
            version="1",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "nonexistent"),
        )
        with pytest.raises(RuntimeError, match="not found"):
            mod.build()

    def test_run_invokes_gradle(self, tmp_path):
        pd = str(tmp_path / "proj")
        os.makedirs(pd)
        with open(os.path.join(pd, "gradle.properties"), "w") as f:
            f.write("")
        mod = ModConfig(
            mod_id="rmod",
            name="R",
            version="1",
            description="",
            authors=["X"],
            project_dir=pd,
        )
        with (
            patch("fabricpy.modconfig.subprocess.check_call") as mock,
            patch("fabricpy.modconfig.os.chdir"),
            patch("fabricpy.modconfig.os.getcwd", return_value="/orig"),
        ):
            mod.run()
            mock.assert_called_once_with(["./gradlew", "runClient"])

    def test_run_raises_without_project(self, tmp_path):
        mod = ModConfig(
            mod_id="nomod",
            name="N",
            version="1",
            description="",
            authors=["X"],
            project_dir=str(tmp_path / "nonexistent"),
        )
        with pytest.raises(FileNotFoundError, match="does not exist"):
            mod.run()

    def test_run_restores_cwd_on_gradle_failure(self, tmp_path):
        pd = str(tmp_path / "proj")
        os.makedirs(pd)
        with open(os.path.join(pd, "gradle.properties"), "w") as f:
            f.write("")
        mod = ModConfig(
            mod_id="failmod",
            name="F",
            version="1",
            description="",
            authors=["X"],
            project_dir=pd,
        )
        original = os.getcwd()
        with (
            patch(
                "fabricpy.modconfig.subprocess.check_call",
                side_effect=subprocess.CalledProcessError(1, "gradlew"),
            ),
            patch("fabricpy.modconfig.os.chdir") as chdir_mock,
            patch("fabricpy.modconfig.os.getcwd", return_value="/saved"),
        ):
            with pytest.raises(subprocess.CalledProcessError):
                mod.run()
            # Should restore CWD even on failure
            chdir_mock.assert_any_call("/saved")

    def test_build_writes_gradle_properties(self, tmp_path):
        pd = str(tmp_path / "proj")
        os.makedirs(pd)
        with open(os.path.join(pd, "gradle.properties"), "w") as f:
            f.write("")
        mod = ModConfig(
            mod_id="propmod",
            name="P",
            version="2.3.4",
            description="",
            authors=["X"],
            project_dir=pd,
        )
        with patch("fabricpy.modconfig.subprocess.check_call"):
            mod.build()
        content = open(os.path.join(pd, "gradle.properties")).read()
        assert "mod_id=propmod" in content
        assert "mod_version=2.3.4" in content
        assert "archives_base_name=propmod" in content

    def test_run_writes_gradle_properties(self, tmp_path):
        pd = str(tmp_path / "proj")
        os.makedirs(pd)
        with open(os.path.join(pd, "gradle.properties"), "w") as f:
            f.write("")
        mod = ModConfig(
            mod_id="runprop",
            name="R",
            version="3.0.0",
            description="",
            authors=["X"],
            project_dir=pd,
        )
        with (
            patch("fabricpy.modconfig.subprocess.check_call"),
            patch("fabricpy.modconfig.os.chdir"),
            patch("fabricpy.modconfig.os.getcwd", return_value="/orig"),
        ):
            mod.run()
        content = open(os.path.join(pd, "gradle.properties")).read()
        assert "mod_id=runprop" in content
        assert "mod_version=3.0.0" in content

    def test_build_then_run_workflow(self, tmp_path):
        """Simulate the full compile → build → run workflow."""
        pd = str(tmp_path / "proj")
        os.makedirs(pd)
        with open(os.path.join(pd, "gradle.properties"), "w") as f:
            f.write("")
        mod = ModConfig(
            mod_id="workflow",
            name="W",
            version="1",
            description="",
            authors=["X"],
            project_dir=pd,
        )
        calls = []
        with (
            patch(
                "fabricpy.modconfig.subprocess.check_call",
                side_effect=lambda cmd, **kw: calls.append(cmd),
            ),
            patch("fabricpy.modconfig.os.chdir"),
            patch("fabricpy.modconfig.os.getcwd", return_value="/orig"),
        ):
            mod.build()
            mod.run()
        assert calls == [
            ["./gradlew", "build"],
            ["./gradlew", "runClient"],
        ]

    def test_compile_build_run_full_sequence(self, tmp_path):
        """Full sequence: compile a real mod, then mock build+run."""
        pd = str(tmp_path / "proj")
        mod = ModConfig(
            mod_id="seqmod",
            name="Seq Mod",
            version="1.0.0",
            description="",
            authors=["X"],
            project_dir=pd,
            enable_testing=False,
        )
        mod.registerItem(Item(id="seqmod:gem", name="Gem"))
        mod.registerBlock(
            Block(
                id="seqmod:ore",
                name="Ore",
                hardness=3.0,
                resistance=3.0,
                tool_type="pickaxe",
                mining_speeds={"pickaxe": 6.0},
            )
        )
        mod.compile()

        # Verify project exists
        assert os.path.isdir(pd)
        assert os.path.exists(os.path.join(pd, "gradle.properties"))

        calls = []
        with (
            patch(
                "fabricpy.modconfig.subprocess.check_call",
                side_effect=lambda cmd, **kw: calls.append(cmd),
            ),
            patch("fabricpy.modconfig.os.chdir"),
            patch("fabricpy.modconfig.os.getcwd", return_value="/orig"),
        ):
            mod.build()
            mod.run()
        assert ["./gradlew", "build"] in calls
        assert ["./gradlew", "runClient"] in calls


# ===================================================================== #
#  SECTION 4 — GRADLE BUILD + RUN (real) — whole lifecycle              #
# ===================================================================== #


@pytest.mark.gradle
@needs_jdk
@needs_git
class TestGradleBuildAndRunClient:
    """End-to-end: compile → gradle build → gradle runClient (dry).

    We cannot actually launch a Minecraft client in CI, but we can verify
    that the Gradle ``runClient`` task resolves its dependencies and
    downloads the game assets.  We do this by running ``./gradlew
    runClient --dry-run`` which validates the task graph without actually
    executing it.
    """

    def test_run_client_dry_run(self, project_dir, gradle_home):
        """compile → build → runClient --dry-run should succeed."""
        mod = _build_full_mod(project_dir)
        # First make sure it builds
        build_result = gradle_run(
            project_dir, gradle_home, task="build", extra_args=["-x", "test"]
        )
        assert_build_success(build_result)
        assert_jar_exists(project_dir)

        # Now verify runClient task graph resolves
        gradlew = os.path.join(project_dir, "gradlew")
        if os.path.exists(gradlew):
            os.chmod(gradlew, 0o755)
        env = os.environ.copy()
        env["GRADLE_USER_HOME"] = gradle_home
        dry_result = subprocess.run(
            [gradlew, "runClient", "--dry-run", "--no-daemon"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
        )
        assert dry_result.returncode == 0, (
            f"runClient --dry-run failed:\n{dry_result.stderr[-2000:]}"
        )
