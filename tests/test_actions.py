"""
Unit tests for the actions module.

Tests every action helper function in ``fabricpy.actions`` to verify
that correct Java code snippets are generated with proper syntax,
variable names, and parameter handling.  Also tests list-based hook
composition via ``_normalize_hook``.
"""

import unittest

from fabricpy.block import _normalize_hook
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


class TestReplaceBlock(unittest.TestCase):
    """Test the replace_block action."""

    def test_basic_replace(self):
        code = replace_block("DIAMOND_BLOCK")
        self.assertEqual(
            code,
            "world.setBlockAndUpdate(pos, Blocks.DIAMOND_BLOCK.defaultBlockState());",
        )

    def test_replace_air(self):
        code = replace_block("AIR")
        self.assertIn("Blocks.AIR", code)

    def test_replace_uppercases_input(self):
        code = replace_block("gold_block")
        self.assertIn("Blocks.GOLD_BLOCK", code)

    def test_custom_variables(self):
        code = replace_block("STONE", pos_var="blockPos", world_var="level")
        self.assertIn("level.setBlockAndUpdate(blockPos,", code)


class TestTeleportPlayer(unittest.TestCase):
    """Test the teleport_player action."""

    def test_absolute_teleport(self):
        code = teleport_player(100, 200, 300)
        self.assertEqual(code, "player.teleportTo(100, 200, 300);")

    def test_relative_teleport(self):
        code = teleport_player(0, 10, 0, relative=True)
        self.assertIn("pos.getX() + 0", code)
        self.assertIn("pos.getY() + 10", code)
        self.assertIn("pos.getZ() + 0", code)

    def test_float_coordinates(self):
        code = teleport_player(0.5, 64.5, -0.5)
        self.assertIn("0.5", code)
        self.assertIn("64.5", code)
        self.assertIn("-0.5", code)

    def test_custom_player_var(self):
        code = teleport_player(0, 10, 0, player_var="serverPlayer")
        self.assertIn("serverPlayer.teleportTo(", code)

    def test_custom_pos_var_relative(self):
        code = teleport_player(1, 2, 3, relative=True, pos_var="blockPos")
        self.assertIn("blockPos.getX()", code)


class TestLaunchPlayer(unittest.TestCase):
    """Test the launch_player action."""

    def test_default_launch(self):
        code = launch_player()
        self.assertIn("player.push(0.0, 1.0, 0.0);", code)
        self.assertIn("player.hurtMarked = true;", code)

    def test_custom_velocity(self):
        code = launch_player(dx=3.0, dy=2.5, dz=-1.0)
        self.assertIn("player.push(3.0, 2.5, -1.0);", code)

    def test_custom_player_var(self):
        code = launch_player(dy=1.5, player_var="p")
        self.assertIn("p.push(", code)
        self.assertIn("p.hurtMarked = true;", code)


class TestApplyEffect(unittest.TestCase):
    """Test the apply_effect action."""

    def test_basic_effect(self):
        code = apply_effect("SPEED")
        self.assertEqual(
            code,
            "player.addEffect(new MobEffectInstance(MobEffects.SPEED, 200, 0));",
        )

    def test_custom_duration_amplifier(self):
        code = apply_effect("REGENERATION", duration=600, amplifier=2)
        self.assertIn("MobEffects.REGENERATION, 600, 2", code)

    def test_uppercases_input(self):
        code = apply_effect("night_vision")
        self.assertIn("MobEffects.NIGHT_VISION", code)

    def test_custom_player_var(self):
        code = apply_effect("JUMP_BOOST", player_var="target")
        self.assertIn("target.addEffect(", code)


class TestPlaySound(unittest.TestCase):
    """Test the play_sound action."""

    def test_basic_sound(self):
        code = play_sound("LIGHTNING_BOLT_THUNDER")
        self.assertIn("SoundEvents.LIGHTNING_BOLT_THUNDER", code)
        self.assertIn("SoundSource.BLOCKS", code)
        self.assertIn("1.0f, 1.0f", code)

    def test_custom_volume_pitch(self):
        code = play_sound("ANVIL_LAND", volume=2.0, pitch=0.5)
        self.assertIn("2.0f, 0.5f", code)

    def test_custom_source(self):
        code = play_sound("EXPERIENCE_ORB_PICKUP", source="PLAYERS")
        self.assertIn("SoundSource.PLAYERS", code)

    def test_custom_variables(self):
        code = play_sound("ANVIL_LAND", pos_var="bp", world_var="lvl")
        self.assertIn("lvl.playSound(null, bp,", code)


class TestSummonLightning(unittest.TestCase):
    """Test the summon_lightning action."""

    def test_basic_lightning(self):
        code = summon_lightning()
        self.assertIn("ServerLevel serverLevel", code)
        self.assertIn("LightningBolt bolt = new LightningBolt(", code)
        self.assertIn("EntityType.LIGHTNING_BOLT", code)
        self.assertIn("serverLevel.addFreshEntity(bolt)", code)

    def test_uses_pos_center(self):
        code = summon_lightning()
        self.assertIn("pos.getX() + 0.5", code)
        self.assertIn("pos.getZ() + 0.5", code)

    def test_custom_variables(self):
        code = summon_lightning(pos_var="blockPos", world_var="level")
        self.assertIn("level instanceof ServerLevel", code)
        self.assertIn("blockPos.getX()", code)


class TestDropItem(unittest.TestCase):
    """Test the drop_item action."""

    def test_basic_drop(self):
        code = drop_item("DIAMOND")
        self.assertEqual(
            code,
            "Block.popResource(world, pos, new ItemStack(Items.DIAMOND, 1));",
        )

    def test_drop_multiple(self):
        code = drop_item("EMERALD", count=5)
        self.assertIn("Items.EMERALD, 5", code)

    def test_uppercases_input(self):
        code = drop_item("gold_ingot", count=3)
        self.assertIn("Items.GOLD_INGOT", code)

    def test_custom_variables(self):
        code = drop_item("IRON_INGOT", pos_var="bp", world_var="lvl")
        self.assertIn("Block.popResource(lvl, bp,", code)


class TestPlaceFire(unittest.TestCase):
    """Test the place_fire action."""

    def test_fire_above(self):
        code = place_fire()
        self.assertIn("pos.above()", code)
        self.assertIn("Blocks.FIRE.defaultBlockState()", code)
        self.assertIn("isAir()", code)

    def test_fire_at_pos(self):
        code = place_fire(above=False)
        # Should not contain above() when placing at position
        lines = code.split("\n")
        # All references in the conditional should be just pos, not pos.above()
        self.assertNotIn("pos.above()", code)

    def test_custom_variables(self):
        code = place_fire(pos_var="bp", world_var="lvl")
        self.assertIn("lvl.getBlockState(bp.above())", code)


class TestExtinguishArea(unittest.TestCase):
    """Test the extinguish_area action."""

    def test_default_radius(self):
        code = extinguish_area()
        self.assertIn("dx = -3; dx <= 3", code)
        self.assertIn("Blocks.FIRE", code)
        self.assertIn("Blocks.AIR.defaultBlockState()", code)

    def test_custom_radius(self):
        code = extinguish_area(radius=5)
        self.assertIn("dx = -5; dx <= 5", code)

    def test_uses_offset(self):
        code = extinguish_area()
        self.assertIn("pos.offset(dx, dy, dz)", code)

    def test_custom_variables(self):
        code = extinguish_area(pos_var="bp", world_var="lvl")
        self.assertIn("bp.offset(dx, dy, dz)", code)
        self.assertIn("lvl.getBlockState(checkPos)", code)


class TestGiveXP(unittest.TestCase):
    """Test the give_xp action."""

    def test_basic_give(self):
        code = give_xp(100)
        self.assertEqual(code, "player.giveExperiencePoints(100);")

    def test_custom_player(self):
        code = give_xp(50, player_var="p")
        self.assertEqual(code, "p.giveExperiencePoints(50);")


class TestRemoveXP(unittest.TestCase):
    """Test the remove_xp action."""

    def test_basic_remove(self):
        code = remove_xp(50)
        self.assertEqual(code, "player.giveExperiencePoints(-50);")

    def test_negative_input_handled(self):
        # Even if a negative number is passed, abs() ensures it becomes negative
        code = remove_xp(-25)
        self.assertIn("-25", code)

    def test_custom_player(self):
        code = remove_xp(30, player_var="target")
        self.assertEqual(code, "target.giveExperiencePoints(-30);")


class TestDamageNearby(unittest.TestCase):
    """Test the damage_nearby action."""

    def test_basic_damage(self):
        code = damage_nearby(6.0)
        self.assertIn("LivingEntity.class", code)
        self.assertIn("new AABB(pos).inflate(5.0)", code)
        self.assertIn("e -> e != player", code)
        self.assertIn("e.hurt(", code)
        self.assertIn("6.0f", code)

    def test_custom_radius(self):
        code = damage_nearby(4.0, radius=10.0)
        self.assertIn("inflate(10.0)", code)

    def test_include_player(self):
        code = damage_nearby(6.0, exclude_player=False)
        self.assertIn("e -> true", code)

    def test_custom_variables(self):
        code = damage_nearby(6.0, pos_var="bp", world_var="lvl", player_var="p")
        self.assertIn("lvl.getEntitiesOfClass(", code)
        self.assertIn("new AABB(bp)", code)
        self.assertIn("e -> e != p", code)


class TestHealNearby(unittest.TestCase):
    """Test the heal_nearby action."""

    def test_basic_heal(self):
        code = heal_nearby(4.0)
        self.assertIn("LivingEntity.class", code)
        self.assertIn("new AABB(pos).inflate(5.0)", code)
        self.assertIn("e.heal(4.0f)", code)

    def test_custom_radius(self):
        code = heal_nearby(8.0, radius=15.0)
        self.assertIn("inflate(15.0)", code)
        self.assertIn("e.heal(8.0f)", code)

    def test_custom_variables(self):
        code = heal_nearby(4.0, pos_var="bp", world_var="lvl")
        self.assertIn("lvl.getEntitiesOfClass(", code)
        self.assertIn("new AABB(bp)", code)


class TestDelayedAction(unittest.TestCase):
    """Test the delayed_action action."""

    def test_basic_delay(self):
        inner = give_xp(100)
        code = delayed_action(inner, ticks=40)
        self.assertIn("ServerLevel _delayLevel", code)
        self.assertIn("ServerTickEvents.END_SERVER_TICK.register", code)
        self.assertIn("getTickCount() + 40", code)
        self.assertIn("giveExperiencePoints(100)", code)

    def test_default_ticks(self):
        code = delayed_action(give_xp(50))
        self.assertIn("getTickCount() + 20", code)

    def test_multiline_inner_code(self):
        inner = "\n".join([give_xp(100), play_sound("ANVIL_LAND")])
        code = delayed_action(inner, ticks=60)
        self.assertIn("giveExperiencePoints(100)", code)
        self.assertIn("SoundEvents.ANVIL_LAND", code)

    def test_custom_world_var(self):
        code = delayed_action(give_xp(10), world_var="level")
        self.assertIn("level instanceof ServerLevel", code)


class TestSculkEvent(unittest.TestCase):
    """Test the sculk_event action."""

    def test_basic_event(self):
        code = sculk_event("BLOCK_CHANGE")
        self.assertEqual(
            code,
            "world.gameEvent(player, GameEvent.BLOCK_CHANGE, pos);",
        )

    def test_uppercases_input(self):
        code = sculk_event("explode")
        self.assertIn("GameEvent.EXPLODE", code)

    def test_custom_variables(self):
        code = sculk_event("STEP", pos_var="bp", world_var="lvl", player_var="p")
        self.assertEqual(
            code,
            "lvl.gameEvent(p, GameEvent.STEP, bp);",
        )


class TestActionComposition(unittest.TestCase):
    """Test that actions can be composed together."""

    def test_list_of_actions(self):
        """Returning a list of actions is the idiomatic pattern."""
        actions = [
            replace_block("DIAMOND_BLOCK"),
            play_sound("ANVIL_LAND"),
            give_xp(50),
        ]
        # Each element is a string; the framework joins them.
        self.assertTrue(all(isinstance(a, str) for a in actions))
        combined = "\n".join(actions)
        self.assertIn("Blocks.DIAMOND_BLOCK", combined)
        self.assertIn("SoundEvents.ANVIL_LAND", combined)
        self.assertIn("giveExperiencePoints(50)", combined)

    def test_join_multiple_actions_legacy(self):
        """Legacy join pattern still works."""
        combined = "\n".join(
            [
                replace_block("DIAMOND_BLOCK"),
                play_sound("ANVIL_LAND"),
                give_xp(50),
            ]
        )
        self.assertIn("Blocks.DIAMOND_BLOCK", combined)
        self.assertIn("SoundEvents.ANVIL_LAND", combined)
        self.assertIn("giveExperiencePoints(50)", combined)

    def test_delayed_with_composed_actions(self):
        inner = "\n".join(
            [
                summon_lightning(),
                play_sound("LIGHTNING_BOLT_THUNDER"),
            ]
        )
        code = delayed_action(inner, ticks=60)
        self.assertIn("LightningBolt", code)
        self.assertIn("SoundEvents.LIGHTNING_BOLT_THUNDER", code)
        self.assertIn("getTickCount() + 60", code)


class TestNormalizeHook(unittest.TestCase):
    """Test the _normalize_hook utility for list-based hook returns."""

    def test_none_returns_none(self):
        self.assertIsNone(_normalize_hook(None))

    def test_string_passes_through(self):
        self.assertEqual(
            _normalize_hook("player.giveExperiencePoints(100);"),
            "player.giveExperiencePoints(100);",
        )

    def test_empty_string_returns_none(self):
        self.assertIsNone(_normalize_hook(""))

    def test_list_of_strings(self):
        result = _normalize_hook(
            [
                give_xp(100),
                play_sound("ANVIL_LAND"),
            ]
        )
        self.assertIn("giveExperiencePoints(100)", result)
        self.assertIn("SoundEvents.ANVIL_LAND", result)

    def test_single_item_list(self):
        result = _normalize_hook([give_xp(50)])
        self.assertEqual(result, "player.giveExperiencePoints(50);")

    def test_empty_list_returns_none(self):
        self.assertIsNone(_normalize_hook([]))

    def test_tuple_supported(self):
        result = _normalize_hook((give_xp(10), play_sound("ANVIL_LAND")))
        self.assertIn("giveExperiencePoints(10)", result)
        self.assertIn("SoundEvents.ANVIL_LAND", result)

    def test_list_with_nones_filtered(self):
        result = _normalize_hook([give_xp(10), None, play_sound("ANVIL_LAND")])
        self.assertIn("giveExperiencePoints(10)", result)
        self.assertIn("SoundEvents.ANVIL_LAND", result)

    def test_list_of_all_nones_returns_none(self):
        self.assertIsNone(_normalize_hook([None, None]))

    def test_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            _normalize_hook(42)


class TestBlockHookListReturn(unittest.TestCase):
    """Test that Block hooks accept and normalise list returns."""

    def test_subclass_on_right_click_list(self):
        from fabricpy.block import Block

        class MyBlock(Block):
            def __init__(self):
                super().__init__(id="test:myblock", name="My Block")

            def on_right_click(self):
                return [
                    give_xp(100),
                    play_sound("EXPERIENCE_ORB_PICKUP"),
                ]

        block = MyBlock()
        result = block.on_right_click()
        self.assertIsInstance(result, list)
        # The framework normalises at consumption time
        normalised = _normalize_hook(result)
        self.assertIn("giveExperiencePoints(100)", normalised)
        self.assertIn("SoundEvents.EXPERIENCE_ORB_PICKUP", normalised)

    def test_constructor_list_event(self):
        from fabricpy.block import Block

        block = Block(
            id="test:listblock",
            name="List Block",
            left_click_event=[
                give_xp(50),
                play_sound("ANVIL_LAND"),
            ],
        )
        result = block.on_left_click()
        self.assertIsInstance(result, str)
        self.assertIn("giveExperiencePoints(50)", result)
        self.assertIn("SoundEvents.ANVIL_LAND", result)

    def test_constructor_string_still_works(self):
        from fabricpy.block import Block

        block = Block(
            id="test:strblock",
            name="String Block",
            right_click_event='System.out.println("hello");',
        )
        self.assertEqual(block.on_right_click(), 'System.out.println("hello");')

    def test_constructor_none_still_works(self):
        from fabricpy.block import Block

        block = Block(id="test:none", name="None Block")
        self.assertIsNone(block.on_left_click())
        self.assertIsNone(block.on_right_click())
        self.assertIsNone(block.on_break())


if __name__ == "__main__":
    unittest.main()
