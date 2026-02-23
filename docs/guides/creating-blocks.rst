Creating Blocks
===============

Blocks are the building components of the Minecraft world. In fabricpy, creating blocks automatically generates both the block itself and its corresponding BlockItem for inventory use.

Basic Block Creation
--------------------

Here's how to create a simple block:

.. code-block:: python

   import fabricpy

   # Create a basic block
   ruby_block = fabricpy.Block(
       id="mymod:ruby_block",
       name="Ruby Block",
       item_group=fabricpy.item_group.BUILDING_BLOCKS
   )

Required Parameters
~~~~~~~~~~~~~~~~~~~

* **id**: The unique identifier for your block (format: ``modid:blockname``)
* **name**: The display name shown to players

Optional Parameters
~~~~~~~~~~~~~~~~~~~

* **item_group**: The creative tab for the BlockItem (default: ``fabricpy.item_group.BUILDING_BLOCKS``)
* **block_texture_path**: Path to the block's texture file
* **inventory_texture_path**: Path to the block's inventory item texture file
* **recipe**: A RecipeJson object for crafting recipes
* **loot_table**: A LootTable object controlling what the block drops when broken
* **max_stack_size**: Maximum stack size for the block item (default: 64)
* Override :py:meth:`fabricpy.block.Block.on_left_click` or
  :py:meth:`fabricpy.block.Block.on_right_click` in a subclass to run Java code
  when the block is clicked. Helpers like ``fabricpy.message.send_message`` and
  ``fabricpy.message.send_action_bar_message`` make it easy to talk with players.
  The framework appends ``return ActionResult.SUCCESS;`` for you, so your
  methods should only include the statements to execute.
* Override :py:meth:`fabricpy.block.Block.on_break` in a subclass (or pass
  ``break_event`` to the constructor) to run Java code **after** the block is
  broken. This fires server-side via Fabric's ``PlayerBlockBreakEvents.AFTER``
  event. The callback receives ``world``, ``player``, ``pos``, ``state`` (the
  block state before breaking), and ``entity`` (the ``BlockEntity``, may be
  ``null``).

Advanced Block Examples
-----------------------

Decorative Block with Custom Texture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Decorative block
   marble_block = fabricpy.Block(
       id="mymod:marble",
       name="Marble",
       block_texture_path="textures/blocks/marble.png",
       item_group=fabricpy.item_group.BUILDING_BLOCKS
   )

Ore Block
~~~~~~~~~

.. code-block:: python

   # Ore block with mining properties and fortune-affected loot table
   ruby_ore = fabricpy.Block(
       id="mymod:ruby_ore",
       name="Ruby Ore",
       block_texture_path="textures/blocks/ruby_ore.png",
       hardness=3.0,
       resistance=3.0,
       tool_type="pickaxe",
       mining_level="iron",
       item_group=fabricpy.item_group.NATURAL,
       loot_table=fabricpy.LootTable.drops_with_fortune(
           "mymod:ruby_ore", "mymod:ruby",
           min_count=1, max_count=2,
       )
   )

Storage Block
~~~~~~~~~~~~~

.. code-block:: python

   # Storage block with recipe
   recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shaped",
       "pattern": [
           "RRR",
           "RRR", 
           "RRR"
       ],
       "key": {
           "R": "mymod:ruby"
       },
       "result": {"id": "mymod:ruby_block", "count": 1}
   })

   ruby_storage = fabricpy.Block(
       id="mymod:ruby_block",
       name="Block of Ruby",
       recipe=recipe,
       loot_table=fabricpy.LootTable.drops_self("mymod:ruby_block"),
   )

Machine Block
~~~~~~~~~~~~~

.. code-block:: python

   # Machine/functional block
   smelter = fabricpy.Block(
       id="mymod:magic_smelter",
       name="Magic Smelter",
       block_texture_path="textures/blocks/magic_smelter.png",
       item_group=fabricpy.item_group.FUNCTIONAL
   )

Block with Click Events
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Block reacting to player interactions
   from fabricpy.message import send_message, send_action_bar_message

   class EventBlock(fabricpy.Block):
       def __init__(self):
           super().__init__(id="mymod:event_block", name="Event Block")

       def on_left_click(self):
           return send_message("left clicked")

       def on_right_click(self):
           return send_action_bar_message("right clicked")

       def on_break(self):
           return send_message("block destroyed!")

   event_block = EventBlock()

You can also use the constructor parameters for a declarative style:

.. code-block:: python

   block = fabricpy.Block(
       id="mymod:alert_block",
       name="Alert Block",
       left_click_event='System.out.println("attacked");',
       right_click_event='System.out.println("used");',
       break_event='System.out.println("broken");',
   )

See :file:`examples/message_block.py` for a runnable example.

Block with Loot Table
~~~~~~~~~~~~~~~~~~~~~

Loot tables control what drops when a block is broken. Use the ``loot_table``
parameter to attach one:

.. code-block:: python

   # Self-dropping block (most common)
   simple_block = fabricpy.Block(
       id="mymod:marble",
       name="Marble",
       loot_table=fabricpy.LootTable.drops_self("mymod:marble"),
   )

   # Ore with fortune scaling
   ore = fabricpy.Block(
       id="mymod:ruby_ore",
       name="Ruby Ore",
       loot_table=fabricpy.LootTable.drops_with_fortune(
           "mymod:ruby_ore", "mymod:ruby",
           min_count=1, max_count=2,
       ),
   )

   # Glass-style silk touch
   glass = fabricpy.Block(
       id="mymod:crystal_glass",
       name="Crystal Glass",
       loot_table=fabricpy.LootTable.drops_with_silk_touch("mymod:crystal_glass"),
   )

See :doc:`loot-tables` for the full guide on all available loot table patterns.

Mining Configuration
~~~~~~~~~~~~~~~~~~~~

Use the mining properties to control how blocks are mined, which tools
are effective, and whether the correct tool is required for drops.

**Hardness & Resistance**

``hardness`` controls how long the block takes to mine, while ``resistance``
controls blast durability.  When neither is specified fabricpy copies stone
defaults (hardness 1.5, resistance 6.0).

.. code-block:: python

   # A hard ore that resists explosions
   tough_ore = fabricpy.Block(
       id="mymod:tough_ore",
       name="Tough Ore",
       hardness=5.0,
       resistance=12.0,
   )

Reference values:

=============  =========  ==========
Block          Hardness   Resistance
=============  =========  ==========
Dirt           0.5        0.5
Stone          1.5        6.0
Iron Ore       3.0        3.0
Obsidian       50.0       1200.0
=============  =========  ==========

**Tool type & requiring a tool for drops**

Set ``tool_type`` to tag the block as mineable by a specific tool.  When
``tool_type`` is set, ``requires_tool`` defaults to ``True`` which means
the block drops nothing if broken by hand.

.. code-block:: python

   iron_ore = fabricpy.Block(
       id="mymod:iron_ore",
       name="Iron Ore",
       hardness=3.0,
       resistance=3.0,
       tool_type="pickaxe",
       # requires_tool is automatically True
   )

Valid tool types: ``"pickaxe"``, ``"axe"``, ``"shovel"``, ``"hoe"``,
``"sword"``.

**Mining level**

``mining_level`` sets the minimum tool tier required to mine the block.
Without the correct tier the block drops nothing (if ``requires_tool``
is enabled).

.. code-block:: python

   diamond_ore = fabricpy.Block(
       id="mymod:diamond_ore",
       name="Diamond Ore",
       hardness=3.0,
       resistance=3.0,
       tool_type="pickaxe",
       mining_level="iron",      # needs at least an iron pickaxe
   )

Valid mining levels: ``"stone"``, ``"iron"``, ``"diamond"``.

**Per-tool mining speeds**

``mining_speeds`` lets you assign custom speed multipliers for different
tool types on the same block.  This generates a ``CustomMiningBlock``
Java class that overrides the per-tool break speed, and automatically
tags the block as mineable by every listed tool.

.. code-block:: python

   mixed_ore = fabricpy.Block(
       id="mymod:mixed_ore",
       name="Mixed Ore",
       hardness=4.0,
       resistance=4.0,
       requires_tool=True,
       mining_level="stone",
       mining_speeds={
           "pickaxe": 8.0,       # fastest
           "shovel": 3.0,        # slower but still works
       },
   )

**Full mining example**

.. code-block:: python

   ruby_ore = fabricpy.Block(
       id="mymod:ruby_ore",
       name="Ruby Ore",
       hardness=3.0,
       resistance=3.0,
       tool_type="pickaxe",
       mining_level="iron",
       mining_speeds={
           "pickaxe": 8.0,
           "axe": 2.0,
       },
       loot_table=fabricpy.LootTable.drops_with_fortune(
           "mymod:ruby_ore", "mymod:ruby",
           min_count=1, max_count=3,
       ),
   )

See :file:`examples/mining_blocks.py` for a runnable demo.

Block Categories by Use Case
----------------------------

Building Blocks
~~~~~~~~~~~~~~~

.. code-block:: python

   building_blocks = [
       fabricpy.Block(
           id="mymod:stone_bricks",
           name="Polished Stone Bricks",
       ),
       fabricpy.Block(
           id="mymod:wooden_planks", 
           name="Oak Planks",
       )
   ]

Natural Blocks
~~~~~~~~~~~~~~

.. code-block:: python

   natural_blocks = [
       fabricpy.Block(
           id="mymod:crystal_ore",
           name="Crystal Ore",
           item_group=fabricpy.item_group.NATURAL
       ),
       fabricpy.Block(
           id="mymod:mystical_log",
           name="Mystical Log", 
           item_group=fabricpy.item_group.NATURAL
       )
   ]

Decorative Blocks
~~~~~~~~~~~~~~~~~

.. code-block:: python

   decorative_blocks = [
       fabricpy.Block(
           id="mymod:glowing_mushroom",
           name="Glowing Mushroom",
           item_group=fabricpy.item_group.DECORATIONS
       ),
       fabricpy.Block(
           id="mymod:crystal_glass",
           name="Crystal Glass",
           item_group=fabricpy.item_group.DECORATIONS
       )
   ]

Functional Blocks
~~~~~~~~~~~~~~~~~

.. code-block:: python

   functional_blocks = [
       fabricpy.Block(
           id="mymod:enchanting_altar",
           name="Enchanting Altar",
           item_group=fabricpy.item_group.FUNCTIONAL
       )
   ]

Complete Example
----------------

Here's a complete mod with various block types:

.. code-block:: python

   import fabricpy

   # Create mod
   mod = fabricpy.ModConfig(
       mod_id="blocks_mod",
       name="Blocks Mod",
       version="1.0.0", 
       description="Adds various blocks to Minecraft",
       authors=["Block Builder"]
   )

   # Create blocks
   blocks = [
       # Ore block
       fabricpy.Block(
           id="blocks_mod:titanium_ore",
           name="Titanium Ore",
           block_texture_path="textures/blocks/titanium_ore.png",
           item_group=fabricpy.item_group.NATURAL,
           loot_table=fabricpy.LootTable.drops_with_fortune(
               "blocks_mod:titanium_ore", "blocks_mod:raw_titanium",
               min_count=1, max_count=2,
           )
       ),
       
       # Storage block  
       fabricpy.Block(
           id="blocks_mod:titanium_block",
           name="Titanium Block",
           block_texture_path="textures/blocks/titanium_block.png",
           item_group=fabricpy.item_group.BUILDING_BLOCKS,
           loot_table=fabricpy.LootTable.drops_self("blocks_mod:titanium_block"),
       ),
       
       # Light source
       fabricpy.Block(
           id="blocks_mod:crystal_lamp",
           name="Crystal Lamp",
           block_texture_path="textures/blocks/crystal_lamp.png",
           item_group=fabricpy.item_group.FUNCTIONAL
       ),
       
       # Decorative
       fabricpy.Block(
           id="blocks_mod:marble_pillar",
           name="Marble Pillar", 
           block_texture_path="textures/blocks/marble_pillar.png",
           item_group=fabricpy.item_group.BUILDING_BLOCKS
       )
   ]

   # Register all blocks
   for block in blocks:
       mod.registerBlock(block)

   # Compile and run
   mod.compile()
   mod.run()

Block Property Guidelines
-------------------------

Here are recommended property values for different block types:

**Instant Break Blocks**
  * Hardness: 0.0
  * Examples: Tall grass, flowers, crops

**Soft Blocks**  
  * Hardness: 0.4-0.6
  * Examples: Leaves, wool, sponge

**Medium Blocks**
  * Hardness: 1.5-3.0  
  * Examples: Wood, stone, ores

**Hard Blocks**
  * Hardness: 5.0-25.0
  * Examples: Metal blocks, reinforced materials

**Ultra-Hard Blocks**
  * Hardness: 50.0+
  * Examples: Bedrock-like, end-game materials

**Light Levels**
  * 0: No light
  * 1-7: Dim lighting

Best Practices
--------------

1. **Texture Organization**
   
   * Keep block textures in ``textures/blocks/``
   * Use descriptive filenames
   * Maintain 16x16 resolution for vanilla consistency

2. **Creative Tab Assignment**
   
   * Building materials: ``BUILDING_BLOCKS``
   * Ores and natural: ``NATURAL``
   * Functional items: ``FUNCTIONAL`` 

3. **Stack Size Considerations**
   
   * Building blocks: ``max_stack_size=64`` (default)
   * Special blocks: ``max_stack_size=16`` or lower

Common Issues
-------------

* **Block not appearing**: Ensure block is registered with ``mod.registerBlock()``
* **Missing texture**: Check block_texture_path and file existence
* **BlockItem missing**: fabricpy automatically creates BlockItems - check creative tab

Next Steps
----------

* Learn about :doc:`loot-tables` to control what your blocks drop
* Learn about :doc:`custom-recipes` to add block crafting and smelting recipes
* Explore :doc:`creating-items` for tools that interact with blocks
* See :doc:`vanilla-item-groups` for appropriate block categorization
