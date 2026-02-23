"""Block hooks example — reacting to player interaction and block destruction.

Demonstrates all three block event hooks provided by fabricpy:

* **on_left_click** (attack) — fires via Fabric's ``AttackBlockCallback``
* **on_right_click** (use / interact) — fires via Fabric's ``UseBlockCallback``
* **on_break** (after destruction) — fires via Fabric's ``PlayerBlockBreakEvents.AFTER``

Each hook can be set either declaratively (constructor parameter) or by
overriding the corresponding method in a Block subclass.
"""

import fabricpy
from fabricpy.message import console_print, send_action_bar_message, send_message

# ── Mod setup ────────────────────────────────────────────────────────── #

mod = fabricpy.ModConfig(
    mod_id="hookdemo",
    name="Block Hooks Demo",
    version="1.0.0",
    description="Demonstrates block event hooks",
    authors=["Example Dev"],
    project_dir="block-hooks-output",
)

# ── 1. Declarative style (constructor parameters) ────────────────────── #

# Pass Java code strings directly — quick and simple.
alert_block = fabricpy.Block(
    id="hookdemo:alert_block",
    name="Alert Block",
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_self("hookdemo:alert_block"),
    left_click_event=console_print("Alert block attacked!"),
    right_click_event=console_print("Alert block used!"),
    break_event=console_print("Alert block destroyed!"),
)
mod.registerBlock(alert_block)

# ── 2. Subclass style (method overrides) ─────────────────────────────── #

# Override methods for richer logic or to use the message helpers.


class MagicAltar(fabricpy.Block):
    """An altar block that reacts to every kind of player interaction."""

    def __init__(self):
        super().__init__(
            id="hookdemo:magic_altar",
            name="Magic Altar",
            item_group=fabricpy.item_group.FUNCTIONAL,
            loot_table=fabricpy.LootTable.drops_self("hookdemo:magic_altar"),
        )

    def on_left_click(self):
        """Send a chat message when the player punches the altar."""
        return send_message("The altar shudders from your strike!")

    def on_right_click(self):
        """Send an action-bar message when the player interacts."""
        return send_action_bar_message("The altar glows softly...")

    def on_break(self):
        """Notify the player after the altar is destroyed."""
        return send_message("The altar shatters and releases its magic!")


mod.registerBlock(MagicAltar())

# ── 3. Mixed style — some events declarative, some overridden ────────── #


class TrapBlock(fabricpy.Block):
    """A block that only reacts to being broken."""

    def __init__(self):
        super().__init__(
            id="hookdemo:trap_block",
            name="Trap Block",
            item_group=fabricpy.item_group.REDSTONE,
            loot_table=fabricpy.LootTable.drops_self("hookdemo:trap_block"),
            # Declarative: raw Java for the right-click event
            right_click_event=console_print("Nothing happens... yet."),
        )

    def on_break(self):
        """Override: run custom Java when the block is broken."""
        return send_message("BOOM! The trap block explodes!")


mod.registerBlock(TrapBlock())

# ── Compile ──────────────────────────────────────────────────────────── #

# Uncomment to generate the mod project:
# mod.compile()
# mod.run()
