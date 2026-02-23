Block Actions
=============

The :mod:`fabricpy.actions` module provides ready-made Java code snippets for
common gameplay effects that you can return from a block's event handlers
(``on_left_click``, ``on_right_click``, ``on_break``).

Every function returns a plain Python string containing one or more Java
statements.  Combine multiple actions by returning a **list** from your hook
method — the framework joins them automatically.

Quick Example
-------------

.. code-block:: python

   import fabricpy
   from fabricpy.actions import apply_effect, play_sound, give_xp

   class MagicBlock(fabricpy.Block):
       def __init__(self):
           super().__init__(
               id="mymod:magic_block",
               name="Magic Block",
               item_group=fabricpy.item_group.BUILDING_BLOCKS,
               loot_table=fabricpy.LootTable.drops_self("mymod:magic_block"),
           )

       def on_right_click(self):
           return [
               apply_effect("REGENERATION", 400, 1),
               play_sound("PLAYER_LEVELUP"),
               give_xp(50),
           ]

Replace Block
-------------

Swap the clicked block for a different one.

.. code-block:: python

   from fabricpy.actions import replace_block

   def on_right_click(self):
       return replace_block("DIAMOND_BLOCK")

.. autofunction:: fabricpy.actions.replace_block

Teleport Player
---------------

Move the player to absolute or relative coordinates.

.. code-block:: python

   from fabricpy.actions import teleport_player

   # Relative: teleport 10 blocks up
   def on_right_click(self):
       return teleport_player(0, 10, 0, relative=True)

   # Absolute: teleport to world spawn
   def on_left_click(self):
       return teleport_player(0, 64, 0)

.. autofunction:: fabricpy.actions.teleport_player

Launch Player
-------------

Apply a velocity impulse to the player (knock-back / launch upward).

.. code-block:: python

   from fabricpy.actions import launch_player

   # Launch upward
   def on_left_click(self):
       return launch_player(dy=2.5)

   # Launch in a direction
   def on_right_click(self):
       return launch_player(dx=1.0, dy=0.5, dz=1.0)

.. autofunction:: fabricpy.actions.launch_player

Apply Potion / Status Effect
-----------------------------

Grant a potion effect (by Vanilla ``MobEffects`` field name).

.. code-block:: python

   from fabricpy.actions import apply_effect

   # Speed II for 30 seconds (600 ticks)
   def on_right_click(self):
       return apply_effect("SPEED", 600, 1)

   # Night Vision for 1 minute (default amplifier 0)
   def on_left_click(self):
       return apply_effect("NIGHT_VISION", 1200)

.. autofunction:: fabricpy.actions.apply_effect

Play Sound
----------

Play a Vanilla sound event at the block position.

.. code-block:: python

   from fabricpy.actions import play_sound

   def on_right_click(self):
       return play_sound("ENDER_DRAGON_GROWL")

.. autofunction:: fabricpy.actions.play_sound

Summon Lightning
----------------

Strike lightning at the block position (server-side only).

.. code-block:: python

   from fabricpy.actions import summon_lightning

   def on_break(self):
       return summon_lightning()

.. autofunction:: fabricpy.actions.summon_lightning

Drop Items
----------

Spawn an item stack on the ground at the block position.

.. code-block:: python

   from fabricpy.actions import drop_item

   def on_left_click(self):
       return [
           drop_item("DIAMOND", count=3),
           drop_item("EMERALD"),
       ]

.. autofunction:: fabricpy.actions.drop_item

Place Fire / Extinguish Area
----------------------------

Set fire at the block position or remove fire blocks in a cube around it.

.. code-block:: python

   from fabricpy.actions import place_fire, extinguish_area

   def on_right_click(self):
       return place_fire()

   def on_break(self):
       return extinguish_area(radius=5)

.. autofunction:: fabricpy.actions.place_fire
.. autofunction:: fabricpy.actions.extinguish_area

Give / Remove XP
----------------

Add or subtract experience points from the player.

.. code-block:: python

   from fabricpy.actions import give_xp, remove_xp

   def on_right_click(self):
       return give_xp(100)

   def on_left_click(self):
       return remove_xp(50)

.. autofunction:: fabricpy.actions.give_xp
.. autofunction:: fabricpy.actions.remove_xp

Damage / Heal Nearby Entities
------------------------------

Affect all ``LivingEntity`` instances within a radius of the block.

.. code-block:: python

   from fabricpy.actions import damage_nearby, heal_nearby

   def on_right_click(self):
       return damage_nearby(8.0, radius=10.0)

   def on_break(self):
       return heal_nearby(4.0, radius=5.0)

.. autofunction:: fabricpy.actions.damage_nearby
.. autofunction:: fabricpy.actions.heal_nearby

Delayed Action (Timer)
----------------------

Schedule a block of Java code to run after a delay (in ticks, 20 = 1 second).

.. code-block:: python

   from fabricpy.actions import delayed_action, give_xp

   # Give XP 3 seconds after right-click
   def on_right_click(self):
       return delayed_action(give_xp(100), ticks=60)

.. autofunction:: fabricpy.actions.delayed_action

Sculk Sensor Game Event
------------------------

Emit a ``GameEvent`` that sculk sensors can detect.

.. code-block:: python

   from fabricpy.actions import sculk_event

   def on_break(self):
       return sculk_event("LIGHTNING_STRIKE")

.. autofunction:: fabricpy.actions.sculk_event

Composing Actions
-----------------

All action functions return plain Java strings.  Return them as a **list** to
combine multiple actions in a single handler:

.. code-block:: python

   from fabricpy.actions import (
       apply_effect, give_xp, play_sound, summon_lightning,
   )
   from fabricpy.message import send_message

   def on_right_click(self):
       return [
           send_message("Let the ritual begin!"),
           apply_effect("FIRE_RESISTANCE", 600),
           summon_lightning(),
           give_xp(50),
           play_sound("WITHER_SPAWN"),
       ]

All Java imports are detected automatically — you never need to manage them
yourself.

Full Example
------------

See :file:`examples/block_actions.py` for a complete runnable example
that demonstrates every action in a single mod.
