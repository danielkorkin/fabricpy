"""
Java code-generation tests for the actions module.

These tests verify that when blocks use action helpers, the generated
``TutorialBlocks.java`` source contains the correct Java imports and
the event handler callback bodies include the expected action code.

No Gradle or JDK required — these are fast Python-only checks.
"""

import unittest

import fabricpy
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


# -- helpers -------------------------------------------------------------- #


def _make_mod():
    """Create a throwaway ModConfig for source generation."""
    return ModConfig(
        mod_id="actiontest",
        name="Action Test Mod",
        version="1.0.0",
        description="Tests action import generation",
        authors=["Test"],
        project_dir="/tmp/action-test-dummy",
    )


def _java_src_for(*blocks):
    """Register blocks and return the generated TutorialBlocks Java source."""
    mod = _make_mod()
    for blk in blocks:
        mod.registerBlock(blk)
    return mod._tutorial_blocks_src("com.example.actiontest.blocks")


# -- test blocks ---------------------------------------------------------- #


class EffectBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:effect_block",
            name="Effect Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actiontest:effect_block"),
        )

    def on_right_click(self):
        return [
            apply_effect("SPEED", 600, 1),
            apply_effect("JUMP_BOOST", 200),
            play_sound("WITCH_DRINK"),
        ]


class LightningBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:lightning_block",
            name="Lightning Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actiontest:lightning_block"),
        )

    def on_break(self):
        return [
            summon_lightning(),
            sculk_event("LIGHTNING_STRIKE"),
        ]


class CombatBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:combat_block",
            name="Combat Block",
            item_group=item_group.COMBAT,
            loot_table=LootTable.drops_self("actiontest:combat_block"),
        )

    def on_right_click(self):
        return damage_nearby(8.0, radius=10.0)

    def on_break(self):
        return heal_nearby(6.0, radius=10.0)


class TimerBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:timer_block",
            name="Timer Block",
            item_group=item_group.REDSTONE,
            loot_table=LootTable.drops_self("actiontest:timer_block"),
        )

    def on_right_click(self):
        return delayed_action(give_xp(100), ticks=60)


class LootActionBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:loot_action_block",
            name="Loot Action Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actiontest:loot_action_block"),
        )

    def on_left_click(self):
        return [
            drop_item("DIAMOND", count=3),
            drop_item("EMERALD", count=1),
            give_xp(25),
        ]


class TeleportBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:teleport_block",
            name="Teleport Block",
            item_group=item_group.REDSTONE,
            loot_table=LootTable.drops_self("actiontest:teleport_block"),
        )

    def on_right_click(self):
        return [
            teleport_player(0, 10, 0, relative=True),
            play_sound("ENDERMAN_TELEPORT"),
        ]


class FireBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:fire_block",
            name="Fire Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actiontest:fire_block"),
        )

    def on_right_click(self):
        return place_fire()

    def on_break(self):
        return extinguish_area(radius=5)


class XPBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:xp_block",
            name="XP Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actiontest:xp_block"),
        )

    def on_right_click(self):
        return give_xp(100)

    def on_left_click(self):
        return remove_xp(50)


class ReplaceBlock(Block):
    def __init__(self):
        super().__init__(
            id="actiontest:replace_block",
            name="Replace Block",
            item_group=item_group.BUILDING_BLOCKS,
            loot_table=LootTable.drops_self("actiontest:replace_block"),
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
            id="actiontest:bounce_block",
            name="Bounce Block",
            item_group=item_group.REDSTONE,
            loot_table=LootTable.drops_self("actiontest:bounce_block"),
        )

    def on_left_click(self):
        return launch_player(dy=2.5)


# ========================================================================= #
#  Tests                                                                     #
# ========================================================================= #


class TestActionImports(unittest.TestCase):
    """Verify that all required Java imports are emitted."""

    def test_potion_effect_imports(self):
        src = _java_src_for(EffectBlock())
        self.assertIn("import net.minecraft.world.effect.MobEffectInstance;", src)
        self.assertIn("import net.minecraft.world.effect.MobEffects;", src)
        self.assertIn("import net.minecraft.sounds.SoundEvents;", src)
        self.assertIn("import net.minecraft.sounds.SoundSource;", src)

    def test_lightning_imports(self):
        src = _java_src_for(LightningBlock())
        self.assertIn("import net.minecraft.server.level.ServerLevel;", src)
        self.assertIn("import net.minecraft.world.entity.LightningBolt;", src)
        self.assertIn("import net.minecraft.world.entity.EntityType;", src)
        self.assertIn("import net.minecraft.world.level.gameevent.GameEvent;", src)

    def test_combat_imports(self):
        src = _java_src_for(CombatBlock())
        self.assertIn("import net.minecraft.world.entity.LivingEntity;", src)
        self.assertIn("import net.minecraft.world.phys.AABB;", src)

    def test_timer_imports(self):
        src = _java_src_for(TimerBlock())
        self.assertIn(
            "import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;", src
        )
        self.assertIn("import net.minecraft.server.level.ServerLevel;", src)

    def test_item_drop_imports(self):
        src = _java_src_for(LootActionBlock())
        self.assertIn("import net.minecraft.world.item.ItemStack;", src)
        self.assertIn("import net.minecraft.world.item.Items;", src)

    def test_blockpos_import_for_right_click(self):
        src = _java_src_for(EffectBlock())
        self.assertIn("import net.minecraft.core.BlockPos;", src)

    def test_blockpos_import_for_extinguish(self):
        src = _java_src_for(FireBlock())
        self.assertIn("import net.minecraft.core.BlockPos;", src)

    def test_component_import_for_message(self):
        src = _java_src_for(ReplaceBlock())
        self.assertIn("import net.minecraft.network.chat.Component;", src)


class TestActionImportsAllCombined(unittest.TestCase):
    """Verify that using all actions together produces all required imports."""

    def test_all_imports_present(self):
        src = _java_src_for(
            EffectBlock(),
            LightningBlock(),
            CombatBlock(),
            TimerBlock(),
            LootActionBlock(),
            TeleportBlock(),
            FireBlock(),
            XPBlock(),
            ReplaceBlock(),
            BounceBlock(),
        )
        required_imports = [
            "import net.minecraft.world.effect.MobEffectInstance;",
            "import net.minecraft.world.effect.MobEffects;",
            "import net.minecraft.sounds.SoundEvents;",
            "import net.minecraft.sounds.SoundSource;",
            "import net.minecraft.server.level.ServerLevel;",
            "import net.minecraft.world.entity.LightningBolt;",
            "import net.minecraft.world.entity.EntityType;",
            "import net.minecraft.world.item.ItemStack;",
            "import net.minecraft.world.item.Items;",
            "import net.minecraft.world.entity.LivingEntity;",
            "import net.minecraft.world.phys.AABB;",
            "import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;",
            "import net.minecraft.world.level.gameevent.GameEvent;",
            "import net.minecraft.core.BlockPos;",
            "import net.minecraft.network.chat.Component;",
            "import net.minecraft.world.InteractionResult;",
        ]
        for imp in required_imports:
            self.assertIn(imp, src, f"Missing import: {imp}")


class TestRightClickBlockPosAlias(unittest.TestCase):
    """Verify BlockPos pos = hitResult.getBlockPos() in right-click handler."""

    def test_blockpos_alias_present(self):
        src = _java_src_for(EffectBlock())
        self.assertIn("BlockPos pos = hitResult.getBlockPos();", src)

    def test_uses_pos_not_hitresult_in_check(self):
        src = _java_src_for(EffectBlock())
        # The block check should use pos, not hitResult.getBlockPos()
        self.assertIn("world.getBlockState(pos).getBlock()", src)


class TestActionCodeInHandlers(unittest.TestCase):
    """Verify that action code appears in the generated event handler bodies."""

    def test_effect_code_in_right_click(self):
        src = _java_src_for(EffectBlock())
        self.assertIn("MobEffects.SPEED, 600, 1", src)
        self.assertIn("MobEffects.JUMP_BOOST, 200, 0", src)
        self.assertIn("SoundEvents.WITCH_DRINK", src)

    def test_lightning_code_in_break(self):
        src = _java_src_for(LightningBlock())
        self.assertIn("LightningBolt bolt = new LightningBolt(", src)
        self.assertIn("serverLevel.addFreshEntity(bolt)", src)
        self.assertIn("GameEvent.LIGHTNING_STRIKE", src)

    def test_damage_code_in_right_click(self):
        src = _java_src_for(CombatBlock())
        self.assertIn("getEntitiesOfClass(LivingEntity.class", src)
        self.assertIn("damageSources().magic()", src)

    def test_heal_code_in_break(self):
        src = _java_src_for(CombatBlock())
        self.assertIn("e.heal(6.0f)", src)

    def test_delayed_code_in_right_click(self):
        src = _java_src_for(TimerBlock())
        self.assertIn("ServerTickEvents.END_SERVER_TICK.register", src)
        self.assertIn("getTickCount() + 60", src)
        self.assertIn("giveExperiencePoints(100)", src)

    def test_drop_item_code_in_left_click(self):
        src = _java_src_for(LootActionBlock())
        self.assertIn("Items.DIAMOND, 3", src)
        self.assertIn("Items.EMERALD, 1", src)
        self.assertIn("giveExperiencePoints(25)", src)

    def test_teleport_code_in_right_click(self):
        src = _java_src_for(TeleportBlock())
        self.assertIn("player.teleportTo(", src)
        self.assertIn("pos.getY() + 10", src)

    def test_fire_code_in_right_click_and_break(self):
        src = _java_src_for(FireBlock())
        self.assertIn("Blocks.FIRE.defaultBlockState()", src)
        self.assertIn("pos.offset(dx, dy, dz)", src)
        self.assertIn("Blocks.AIR.defaultBlockState()", src)

    def test_xp_code_in_handlers(self):
        src = _java_src_for(XPBlock())
        self.assertIn("giveExperiencePoints(100)", src)
        self.assertIn("giveExperiencePoints(-50)", src)

    def test_replace_block_code_in_right_click(self):
        src = _java_src_for(ReplaceBlock())
        self.assertIn("Blocks.DIAMOND_BLOCK.defaultBlockState()", src)
        self.assertIn("SoundEvents.ANVIL_LAND", src)
        self.assertIn('Component.literal("Transmuted!")', src)

    def test_launch_code_in_left_click(self):
        src = _java_src_for(BounceBlock())
        self.assertIn("player.push(0.0, 2.5, 0.0)", src)
        self.assertIn("player.hurtMarked = true", src)


class TestNoSpuriousImports(unittest.TestCase):
    """Verify that imports are only added when the corresponding action is used."""

    def test_no_sound_import_without_sound(self):
        src = _java_src_for(XPBlock())
        self.assertNotIn("import net.minecraft.sounds.SoundEvents;", src)

    def test_no_lightning_import_without_lightning(self):
        src = _java_src_for(XPBlock())
        self.assertNotIn("import net.minecraft.world.entity.LightningBolt;", src)

    def test_no_aabb_import_without_aoe(self):
        src = _java_src_for(EffectBlock())
        self.assertNotIn("import net.minecraft.world.phys.AABB;", src)

    def test_no_ticktask_import_without_delay(self):
        src = _java_src_for(EffectBlock())
        self.assertNotIn(
            "import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;", src
        )

    def test_no_gameevent_import_without_sculk(self):
        src = _java_src_for(EffectBlock())
        self.assertNotIn("import net.minecraft.world.level.gameevent.GameEvent;", src)


class TestVariableRedefinitionRegression(unittest.TestCase):
    """Regression: delayed_action(summon_lightning()) must not redefine serverLevel."""

    def test_delayed_lightning_uses_distinct_variables(self):
        """delayed_action wraps summon_lightning — both need ServerLevel but
        must use different variable names to avoid a Java compile error."""

        class DelayedLightningBlock(Block):
            def __init__(self):
                super().__init__(
                    id="actiontest:delayed_lightning",
                    name="Delayed Lightning",
                    item_group=item_group.REDSTONE,
                    loot_table=LootTable.drops_self("actiontest:delayed_lightning"),
                )

            def on_right_click(self):
                return delayed_action(summon_lightning(), ticks=40)

        src = _java_src_for(DelayedLightningBlock())
        # The outer delayed_action should use _delayLevel
        self.assertIn("_delayLevel", src)
        # The inner summon_lightning should still use serverLevel
        self.assertIn("serverLevel", src)
        # They must be different — _delayLevel cannot also be named serverLevel
        self.assertNotIn(
            "instanceof ServerLevel serverLevel) {\n"
            "    serverLevel.getServer().schedule",
            src,
            "delayed_action must use _delayLevel, not serverLevel, "
            "to avoid redefinition when wrapping summon_lightning()",
        )

    def test_nested_delayed_lightning_balanced_braces(self):
        """Braces must be balanced when delayed_action wraps summon_lightning."""
        import re

        class DelayedLightningBlock(Block):
            def __init__(self):
                super().__init__(
                    id="actiontest:delayed_lightning2",
                    name="Delayed Lightning 2",
                    item_group=item_group.REDSTONE,
                    loot_table=LootTable.drops_self("actiontest:delayed_lightning2"),
                )

            def on_right_click(self):
                return delayed_action(summon_lightning(), ticks=40)

        src = _java_src_for(DelayedLightningBlock())
        stripped = re.sub(r"//.*", "", src)
        stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
        stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', stripped)
        opens = stripped.count("{")
        closes = stripped.count("}")
        self.assertEqual(opens, closes, "Unbalanced braces in delayed-lightning code")


class TestActionCompilationWorkflow(unittest.TestCase):
    """Test the compilation workflow with action blocks — file generation."""

    def test_compile_mod_with_actions(self):
        """Compile a mod with action blocks and verify the project is generated."""
        import os
        import shutil
        import tempfile

        temp_dir = tempfile.mkdtemp()
        try:
            mod = ModConfig(
                mod_id="actioncompile",
                name="Action Compile Test",
                version="1.0.0",
                description="Tests action compilation",
                authors=["Test"],
                project_dir=os.path.join(temp_dir, "action-compile-test"),
                enable_testing=False,
            )

            mod.registerBlock(EffectBlock())
            mod.registerBlock(LightningBlock())
            mod.registerBlock(CombatBlock())
            mod.registerBlock(TimerBlock())
            mod.registerBlock(LootActionBlock())
            mod.registerBlock(TeleportBlock())
            mod.registerBlock(FireBlock())
            mod.registerBlock(XPBlock())
            mod.registerBlock(ReplaceBlock())
            mod.registerBlock(BounceBlock())

            mod.compile()

            # Verify project structure
            self.assertTrue(os.path.exists(mod.project_dir))
            self.assertTrue(
                os.path.exists(os.path.join(mod.project_dir, "build.gradle"))
            )

            # Find and verify TutorialBlocks.java exists
            blocks_java = None
            for root, dirs, files in os.walk(mod.project_dir):
                for f in files:
                    if f == "TutorialBlocks.java":
                        blocks_java = os.path.join(root, f)
                        break

            self.assertIsNotNone(blocks_java, "TutorialBlocks.java should be generated")

            with open(blocks_java, "r") as fh:
                content = fh.read()

            # Verify key action imports in real file
            self.assertIn("MobEffectInstance", content)
            self.assertIn("SoundEvents", content)
            self.assertIn("ServerLevel", content)
            self.assertIn("LightningBolt", content)
            self.assertIn("LivingEntity", content)
            self.assertIn("ServerTickEvents", content)
            self.assertIn("GameEvent", content)
            self.assertIn("BlockPos", content)

            # Verify balanced braces
            import re

            stripped = re.sub(r"//.*", "", content)
            stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
            stripped = re.sub(r'"(?:[^"\\]|\\.)*"', '""', stripped)
            opens = stripped.count("{")
            closes = stripped.count("}")
            self.assertEqual(opens, closes, "TutorialBlocks.java has unbalanced braces")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
