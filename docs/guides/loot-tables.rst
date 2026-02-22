Loot Tables
===========

Loot tables control what items drop when blocks are broken, entities are killed,
or chests are opened. fabricpy provides native loot table support through the
:class:`~fabricpy.loottable.LootTable` and :class:`~fabricpy.loottable.LootPool`
classes.

Basic Block Drops (drops itself)
--------------------------------

The most common case — a block that drops itself when mined:

.. code-block:: python

   import fabricpy

   lt = fabricpy.LootTable.drops_self("mymod:ruby_block")

   block = fabricpy.Block(
       id="mymod:ruby_block",
       name="Ruby Block",
       loot_table=lt,
   )

Dropping a Different Item
-------------------------

For blocks like ores that drop a different item:

.. code-block:: python

   # Drop 1–3 rubies when mined
   lt = fabricpy.LootTable.drops_item(
       "mymod:ruby_ore",
       "mymod:ruby",
       min_count=1,
       max_count=3,
   )

   ore = fabricpy.Block(
       id="mymod:ruby_ore",
       name="Ruby Ore",
       loot_table=lt,
   )

Dropping Nothing
----------------

Some blocks (like spawners) should not drop anything:

.. code-block:: python

   lt = fabricpy.LootTable.drops_nothing()

Silk Touch Behaviour
--------------------

Glass-style: drop itself only with Silk Touch, nothing otherwise:

.. code-block:: python

   lt = fabricpy.LootTable.drops_with_silk_touch("mymod:crystal_glass")

Ore-style: Silk Touch gives the ore block, otherwise the refined material:

.. code-block:: python

   lt = fabricpy.LootTable.drops_with_silk_touch(
       "mymod:ruby_ore",
       no_silk_touch_item="mymod:ruby",
       no_silk_touch_count=1,
   )

Fortune-Affected Drops
----------------------

Ore-style drops that scale with the Fortune enchantment. With Silk Touch the
block drops itself; without it the item is dropped with fortune bonus:

.. code-block:: python

   lt = fabricpy.LootTable.drops_with_fortune(
       "mymod:ruby_ore",
       "mymod:ruby",
       min_count=1,
       max_count=2,
   )

Entity & Chest Loot Tables
---------------------------

Loot tables are not limited to blocks. You can create entity and chest loot
tables and register them directly with `ModConfig`:

.. code-block:: python

   from fabricpy import LootTable, LootPool

   # Entity loot table
   zombie_lt = LootTable.entity([
       LootPool()
           .rolls(1)
           .entry("mymod:zombie_fang", weight=3)
           .entry("mymod:zombie_eye", weight=1)
   ])
   mod.registerLootTable("custom_zombie", zombie_lt)

   # Chest loot table with random roll count
   chest_lt = LootTable.chest([
       LootPool()
           .rolls({"type": "minecraft:uniform", "min": 2, "max": 5})
           .entry("mymod:golden_key", weight=5)
           .entry("minecraft:diamond", weight=1)
   ])
   mod.registerLootTable("dungeon_chest", chest_lt)

Building Custom Pools
---------------------

The :class:`~fabricpy.loottable.LootPool` class provides a fluent builder for
creating pools with weighted entries, conditions, and functions:

.. code-block:: python

   from fabricpy import LootPool, LootTable

   pool = (
       LootPool()
       .rolls(1)
       .entry("mymod:common_loot", weight=10)
       .entry("mymod:rare_loot", weight=1, quality=2)
       .condition({"condition": "minecraft:survives_explosion"})
   )

   lt = LootTable.from_pools("minecraft:block", [pool])

Raw JSON
--------

You can also pass raw JSON or a dict if you need full control:

.. code-block:: python

   lt = fabricpy.LootTable({
       "type": "minecraft:block",
       "pools": [
           {
               "rolls": 1,
               "entries": [
                   {"type": "minecraft:item", "name": "mymod:special_gem"}
               ],
               "conditions": [
                   {"condition": "minecraft:survives_explosion"}
               ]
           }
       ]
   })

Compilation
-----------

Loot table JSON files are written automatically during ``mod.compile()``.
Block loot tables go to ``data/<mod_id>/loot_table/blocks/``, entity tables to
``entities/``, and chest tables to ``chests/``.
