"""Block actions example — performing in-game actions from block hooks.

Demonstrates every action helper provided by ``fabricpy.actions``:

* **replace_block** — swap a block for a different one
* **teleport_player** — move the player (absolute or relative)
* **apply_effect** — give a potion / status effect
* **play_sound** — play a sound at the block position
* **summon_lightning** — strike lightning
* **drop_item** — drop item(s) on the ground
* **launch_player** — knockback / launch upward
* **place_fire / extinguish_area** — fire manipulation
* **give_xp / remove_xp** — experience point changes
* **damage_nearby / heal_nearby** — area-of-effect combat
* **delayed_action** — schedule code to run later
* **sculk_event** — emit a game event for sculk sensors

Each action returns a Java code snippet that is embedded into the
generated Fabric mod source.  Actions can be composed by returning
a list from a hook method — the framework joins them automatically.
"""

import fabricpy
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

# ── Mod setup ────────────────────────────────────────────────────────── #

mod = fabricpy.ModConfig(
    mod_id="actiondemo",
    name="Block Actions Demo",
    version="1.0.0",
    description="Demonstrates every block-hook action helper",
    authors=["Example Dev"],
    project_dir="block-actions-output",
)

# ── 1. Transmute Block — right-click turns it into diamond ───────────── #


class TransmuteBlock(fabricpy.Block):
    """Right-click to transmute into a diamond block."""

    def __init__(self):
        super().__init__(
            id="actiondemo:transmute_block",
            name="Transmute Block",
            item_group=fabricpy.item_group.BUILDING_BLOCKS,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:transmute_block"),
        )

    def on_right_click(self):
        return [
            replace_block("DIAMOND_BLOCK"),
            play_sound("ANVIL_LAND", volume=0.8, pitch=1.2),
            send_message("The block transmutes into diamond!"),
        ]


mod.registerBlock(TransmuteBlock())

# ── 2. Teleport Pad — step on (right-click) to teleport up ──────────── #


class TeleportPad(fabricpy.Block):
    """Right-click to teleport 10 blocks upward."""

    def __init__(self):
        super().__init__(
            id="actiondemo:teleport_pad",
            name="Teleport Pad",
            item_group=fabricpy.item_group.REDSTONE,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:teleport_pad"),
        )

    def on_right_click(self):
        return [
            teleport_player(0, 10, 0, relative=True),
            play_sound("ENDERMAN_TELEPORT"),
            send_message("Whoosh! Teleported 10 blocks up!"),
        ]


mod.registerBlock(TeleportPad())

# ── 3. Potion Block — right-click to gain speed + jump boost ─────────── #


class PotionBlock(fabricpy.Block):
    """Right-click for speed and jump boost effects."""

    def __init__(self):
        super().__init__(
            id="actiondemo:potion_block",
            name="Potion Block",
            item_group=fabricpy.item_group.FOOD_AND_DRINK,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:potion_block"),
        )

    def on_right_click(self):
        return [
            apply_effect("SPEED", duration=600, amplifier=1),
            apply_effect("JUMP_BOOST", duration=600, amplifier=2),
            play_sound("WITCH_DRINK"),
            send_message("You feel energised!"),
        ]


mod.registerBlock(PotionBlock())

# ── 4. Thunder Block — break to summon lightning ─────────────────────── #


class ThunderBlock(fabricpy.Block):
    """Breaking this block calls down a lightning strike."""

    def __init__(self):
        super().__init__(
            id="actiondemo:thunder_block",
            name="Thunder Block",
            item_group=fabricpy.item_group.BUILDING_BLOCKS,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:thunder_block"),
        )

    def on_break(self):
        return [
            summon_lightning(),
            play_sound("LIGHTNING_BOLT_THUNDER", volume=2.0),
            sculk_event("LIGHTNING_STRIKE"),
        ]


mod.registerBlock(ThunderBlock())

# ── 5. Loot Block — left-click to drop random treasure ───────────────── #


class LootBlock(fabricpy.Block):
    """Left-click to drop diamonds and emeralds."""

    def __init__(self):
        super().__init__(
            id="actiondemo:loot_block",
            name="Loot Block",
            item_group=fabricpy.item_group.BUILDING_BLOCKS,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:loot_block"),
        )

    def on_left_click(self):
        return [
            drop_item("DIAMOND", count=3),
            drop_item("EMERALD", count=1),
            play_sound("EXPERIENCE_ORB_PICKUP"),
            give_xp(25),
            send_message("Treasure spills out!"),
        ]


mod.registerBlock(LootBlock())

# ── 6. Bouncy Block — launches the player upward on left-click ───────── #


class BouncyBlock(fabricpy.Block):
    """Left-click to get launched into the sky."""

    def __init__(self):
        super().__init__(
            id="actiondemo:bouncy_block",
            name="Bouncy Block",
            item_group=fabricpy.item_group.REDSTONE,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:bouncy_block"),
        )

    def on_left_click(self):
        return [
            launch_player(dy=2.5),
            apply_effect("SLOW_FALLING", duration=100),
            play_sound("SLIME_JUMP", pitch=0.8),
        ]


mod.registerBlock(BouncyBlock())

# ── 7. Fire Block — right-click places fire, break extinguishes ──────── #


class FireBlock(fabricpy.Block):
    """Right-click to ignite, break to extinguish nearby fire."""

    def __init__(self):
        super().__init__(
            id="actiondemo:fire_block",
            name="Fire Block",
            item_group=fabricpy.item_group.BUILDING_BLOCKS,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:fire_block"),
        )

    def on_right_click(self):
        return [
            place_fire(),
            play_sound("FLINTANDSTEEL_USE"),
            send_message("Fire ignited!"),
        ]

    def on_break(self):
        return [
            extinguish_area(radius=5),
            play_sound("FIRE_EXTINGUISH", volume=1.5),
            send_message("Nearby fires extinguished!"),
        ]


mod.registerBlock(FireBlock())

# ── 8. XP Block — right-click grants XP, left-click drains XP ────────── #


class XPBlock(fabricpy.Block):
    """Right-click to gain XP, left-click to lose XP."""

    def __init__(self):
        super().__init__(
            id="actiondemo:xp_block",
            name="XP Block",
            item_group=fabricpy.item_group.BUILDING_BLOCKS,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:xp_block"),
        )

    def on_right_click(self):
        return [
            give_xp(100),
            play_sound("EXPERIENCE_ORB_PICKUP"),
            send_message("+100 XP!"),
        ]

    def on_left_click(self):
        return [
            remove_xp(50),
            play_sound("VILLAGER_NO"),
            send_message("-50 XP!"),
        ]


mod.registerBlock(XPBlock())

# ── 9. Battle Block — damages enemies nearby, heals allies ───────────── #


class BattleBlock(fabricpy.Block):
    """Right-click to damage nearby mobs, break to heal everyone."""

    def __init__(self):
        super().__init__(
            id="actiondemo:battle_block",
            name="Battle Block",
            item_group=fabricpy.item_group.COMBAT,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:battle_block"),
        )

    def on_right_click(self):
        return [
            damage_nearby(8.0, radius=10.0),
            play_sound("WITHER_BREAK_BLOCK"),
            send_message("A shockwave damages nearby enemies!"),
        ]

    def on_break(self):
        return [
            heal_nearby(6.0, radius=10.0),
            play_sound("BEACON_ACTIVATE"),
            send_message("A healing wave pulses outward!"),
        ]


mod.registerBlock(BattleBlock())

# ── 10. Delay Block — triggers a timed event after interact ──────────── #


class DelayBlock(fabricpy.Block):
    """Right-click to trigger a delayed lightning strike (3 seconds)."""

    def __init__(self):
        super().__init__(
            id="actiondemo:delay_block",
            name="Delay Block",
            item_group=fabricpy.item_group.REDSTONE,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:delay_block"),
        )

    def on_right_click(self):
        return [
            send_message("Lightning incoming in 3 seconds..."),
            play_sound("AMETHYST_BLOCK_CHIME"),
            delayed_action(
                summon_lightning(),
                ticks=60,  # 3 seconds
            ),
        ]


mod.registerBlock(DelayBlock())

# ── 11. Sculk Block — emits game events for sculk sensors ───────────── #


class SculkTriggerBlock(fabricpy.Block):
    """Interacting emits a game event detectable by sculk sensors."""

    def __init__(self):
        super().__init__(
            id="actiondemo:sculk_trigger",
            name="Sculk Trigger Block",
            item_group=fabricpy.item_group.REDSTONE,
            loot_table=fabricpy.LootTable.drops_self("actiondemo:sculk_trigger"),
        )

    def on_right_click(self):
        return [
            sculk_event("BLOCK_CHANGE"),
            play_sound("SCULK_CLICKING"),
            send_message("Sculk sensors have been alerted!"),
        ]

    def on_break(self):
        return [
            sculk_event("EXPLODE"),
            send_message("A massive sculk event ripples outward!"),
        ]


mod.registerBlock(SculkTriggerBlock())

# ── Compile ──────────────────────────────────────────────────────────── #

# Uncomment to generate the mod project:
mod.compile()
mod.run()
