"""
Gradle build integration tests for the actions module.

These tests actually run ``./gradlew build`` on generated mods that use every
action helper to verify that the resulting Java compiles against the real
Fabric toolchain.

Requirements:
    - JDK 21+ installed and on PATH
    - Network access (first run fetches the Fabric template + dependencies)
    - ~2-5 minutes per test

Usage:
    pytest tests/test_actions_gradle.py -v -s          # run only actions Gradle tests
    pytest tests/ -m "not gradle"                      # skip all Gradle tests
"""

import os
import subprocess
import tempfile

import pytest

from fabricpy import Block, LootTable, ModConfig, item_group
from fabricpy.actions import (
    apply_effect,
    damage_nearby,
    delayed_action,
    drop_item,
    extinguish_area,
    give_xp,
    heal_nearby,
    launch_player,
    place_fire,
    play_sound,
    remove_xp,
    replace_block,
    sculk_event,
    summon_lightning,
    teleport_player,
)
from fabricpy.message import send_message


# --------------------------------------------------------------------------- #
# Helpers / markers (same as test_gradle_build.py)
# --------------------------------------------------------------------------- #


def _java_available() -> bool:
    try:
        result = subprocess.run(
            ["java", "-version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _git_available() -> bool:
    try:
        result = subprocess.run(
            ["git", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


pytestmark = [
    pytest.mark.gradle,
    pytest.mark.skipif(not _java_available(), reason="JDK not found on PATH"),
    pytest.mark.skipif(not _git_available(), reason="git not found on PATH"),
]

_GRADLE_HOME = os.path.join(tempfile.gettempdir(), "fabricpy_test_gradle_home")


# --------------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="session")
def gradle_home():
    os.makedirs(_GRADLE_HOME, exist_ok=True)
    return _GRADLE_HOME


@pytest.fixture()
def project_dir(tmp_path):
    d = tmp_path / "mod_project"
    yield str(d)


# --------------------------------------------------------------------------- #
# Build helpers (imported pattern from test_gradle_build.py)
# --------------------------------------------------------------------------- #


def gradle_build(project_dir, gradle_home, task="build", timeout=600):
    gradlew = os.path.join(project_dir, "gradlew")
    if os.path.exists(gradlew):
        os.chmod(gradlew, 0o755)
    env = os.environ.copy()
    env["GRADLE_USER_HOME"] = gradle_home
    return subprocess.run(
        [gradlew, task, "--no-daemon", "--stacktrace"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def compile_and_build(mod, gradle_home, task="build"):
    mod.compile()
    return gradle_build(mod.project_dir, gradle_home, task=task)


def assert_build_success(result):
    if result.returncode != 0:
        output = result.stdout + "\n" + result.stderr
        error_lines = []
        capture = False
        for line in output.splitlines():
            if "error:" in line.lower() or "FAILURE" in line or capture:
                error_lines.append(line)
                capture = True
                if len(error_lines) > 60:
                    break
            if "BUILD FAILED" in line:
                error_lines.append(line)
        diagnostic = "\n".join(error_lines[-60:]) if error_lines else output[-3000:]
        pytest.fail(
            f"Gradle build failed (exit code {result.returncode}).\n"
            f"--- Build output ---\n{diagnostic}"
        )


def assert_jar_exists(project_dir):
    libs_dir = os.path.join(project_dir, "build", "libs")
    assert os.path.isdir(libs_dir), f"build/libs/ not found in {project_dir}"
    jars = [f for f in os.listdir(libs_dir) if f.endswith(".jar")]
    assert len(jars) > 0, f"No JAR files found in {libs_dir}"
    return jars


# --------------------------------------------------------------------------- #
# Action block definitions (used across multiple tests)
# --------------------------------------------------------------------------- #


class EffectBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:effect_block",
            name="Effect Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actionsmod:effect_block"),
        )

    def on_right_click(self):
        return [
            apply_effect("SPEED", 600, 1),
            apply_effect("JUMP_BOOST", 200),
            play_sound("WITCH_DRINK"),
        ]


class ThunderBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:thunder_block",
            name="Thunder Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actionsmod:thunder_block"),
        )

    def on_break(self):
        return [
            summon_lightning(),
            sculk_event("LIGHTNING_STRIKE"),
        ]


class CombatBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:combat_block",
            name="Combat Block",
            item_group=item_group.COMBAT,
            loot_table=LootTable.drops_self("actionsmod:combat_block"),
        )

    def on_right_click(self):
        return damage_nearby(8.0, radius=10.0)

    def on_break(self):
        return heal_nearby(6.0, radius=10.0)


class TimerBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:timer_block",
            name="Timer Block",
            item_group=item_group.REDSTONE,
            loot_table=LootTable.drops_self("actionsmod:timer_block"),
        )

    def on_right_click(self):
        return delayed_action(give_xp(100), ticks=60)


class LootActionBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:loot_block",
            name="Loot Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actionsmod:loot_block"),
        )

    def on_left_click(self):
        return [
            drop_item("DIAMOND", count=3),
            drop_item("EMERALD"),
            give_xp(25),
        ]


class TeleportBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:teleport_block",
            name="Teleport Block",
            item_group=item_group.REDSTONE,
            loot_table=LootTable.drops_self("actionsmod:teleport_block"),
        )

    def on_right_click(self):
        return [
            teleport_player(0, 10, 0, relative=True),
            play_sound("ENDERMAN_TELEPORT"),
        ]


class FireBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:fire_block",
            name="Fire Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actionsmod:fire_block"),
        )

    def on_right_click(self):
        return place_fire()

    def on_break(self):
        return extinguish_area(radius=5)


class XPBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:xp_block",
            name="XP Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actionsmod:xp_block"),
        )

    def on_right_click(self):
        return give_xp(100)

    def on_left_click(self):
        return remove_xp(50)


class TransmuteBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:transmute_block",
            name="Transmute Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actionsmod:transmute_block"),
        )

    def on_right_click(self):
        return [
            replace_block("DIAMOND_BLOCK"),
            play_sound("ANVIL_LAND"),
            send_message("Transmuted!"),
        ]


class BounceBlock(Block):
    def __init__(self):
        super().__init__(
            id="actionsmod:bounce_block",
            name="Bounce Block",
            item_group=item_group.REDSTONE,
            loot_table=LootTable.drops_self("actionsmod:bounce_block"),
        )

    def on_left_click(self):
        return launch_player(dy=2.5)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


class TestActionsGradleBuild:
    """Verify that a mod using every single action compiles with Gradle."""

    def test_all_actions_mod_builds(self, project_dir, gradle_home):
        """Register blocks exercising every action and run a real Gradle build."""
        mod = ModConfig(
            mod_id="actionsmod",
            name="Actions Test Mod",
            version="1.0.0",
            description="All action functions in one mod",
            authors=["Test"],
            project_dir=project_dir,
            enable_testing=False,
        )

        for blk in [
            EffectBlock(),
            ThunderBlock(),
            CombatBlock(),
            TimerBlock(),
            LootActionBlock(),
            TeleportBlock(),
            FireBlock(),
            XPBlock(),
            TransmuteBlock(),
            BounceBlock(),
        ]:
            mod.registerBlock(blk)

        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_single_action_per_block_builds(self, project_dir, gradle_home):
        """Each action used individually should still compile."""
        mod = ModConfig(
            mod_id="singleact",
            name="Single Action Mod",
            version="1.0.0",
            description="One action per block",
            authors=["Test"],
            project_dir=project_dir,
            enable_testing=False,
        )

        class OnlyEffect(Block):
            def __init__(self):
                super().__init__(
                    id="singleact:only_effect",
                    name="Only Effect",
                    item_group=item_group.BUILDING_BLOCKS,
                    loot_table=LootTable.drops_self("singleact:only_effect"),
                )

            def on_right_click(self):
                return apply_effect("REGENERATION", 200)

        class OnlySound(Block):
            def __init__(self):
                super().__init__(
                    id="singleact:only_sound",
                    name="Only Sound",
                    item_group=item_group.BUILDING_BLOCKS,
                    loot_table=LootTable.drops_self("singleact:only_sound"),
                )

            def on_right_click(self):
                return play_sound("VILLAGER_YES")

        class OnlyReplace(Block):
            def __init__(self):
                super().__init__(
                    id="singleact:only_replace",
                    name="Only Replace",
                    item_group=item_group.BUILDING_BLOCKS,
                    loot_table=LootTable.drops_self("singleact:only_replace"),
                )

            def on_right_click(self):
                return replace_block("GOLD_BLOCK")

        class OnlyLightning(Block):
            def __init__(self):
                super().__init__(
                    id="singleact:only_lightning",
                    name="Only Lightning",
                    item_group=item_group.BUILDING_BLOCKS,
                    loot_table=LootTable.drops_self("singleact:only_lightning"),
                )

            def on_break(self):
                return summon_lightning()

        for blk in [OnlyEffect(), OnlySound(), OnlyReplace(), OnlyLightning()]:
            mod.registerBlock(blk)

        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_actions_combined_with_messages_builds(self, project_dir, gradle_home):
        """Actions and send_message combined in a handler compile cleanly."""
        mod = ModConfig(
            mod_id="combmod",
            name="Combined Mod",
            version="1.0.0",
            description="Actions plus messages",
            authors=["Test"],
            project_dir=project_dir,
            enable_testing=False,
        )

        class ComboBlock(Block):
            def __init__(self):
                super().__init__(
                    id="combmod:combo",
                    name="Combo Block",
                    item_group=item_group.BUILDING_BLOCKS,
                    loot_table=LootTable.drops_self("combmod:combo"),
                )

            def on_right_click(self):
                return [
                    send_message("Activating..."),
                    apply_effect("FIRE_RESISTANCE", 400, 0),
                    give_xp(50),
                    play_sound("PLAYER_LEVELUP"),
                ]

            def on_left_click(self):
                return [
                    send_message("Powering down!"),
                    remove_xp(10),
                    drop_item("COAL"),
                ]

            def on_break(self):
                return [
                    send_message("Destroyed!"),
                    summon_lightning(),
                    heal_nearby(4.0, radius=5.0),
                ]

        mod.registerBlock(ComboBlock())
        result = compile_and_build(mod, gradle_home)
        assert_build_success(result)
        assert_jar_exists(project_dir)

    def test_delayed_lightning_compiles(self, project_dir, gradle_home):
        """Regression: delayed_action(summon_lightning()) must compile.

        Both use ``ServerLevel instanceof`` checks, so variable names
        must not collide (``_delayLevel`` vs ``serverLevel``).
        """
        mod = ModConfig(
            mod_id="delaylight",
            name="Delayed Lightning Mod",
            version="1.0.0",
            description="Regression test for variable redefinition",
            authors=["Test"],
            project_dir=project_dir,
            enable_testing=False,
        )

        class DelayedLightningBlock(Block):
            def __init__(self):
                super().__init__(
                    id="delaylight:delayed_bolt",
                    name="Delayed Bolt",
                    item_group=item_group.REDSTONE,
                    loot_table=LootTable.drops_self("delaylight:delayed_bolt"),
                )

            def on_right_click(self):
                return delayed_action(summon_lightning(), ticks=40)

            def on_break(self):
                return summon_lightning()

        mod.registerBlock(DelayedLightningBlock())

        # Only compile (skip test task for speed)
        result = compile_and_build(mod, gradle_home, task="compileJava")
        assert_build_success(result)
