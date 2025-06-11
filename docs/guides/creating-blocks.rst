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
* **recipe**: A RecipeJson object for crafting recipes
* **hardness**: How long the block takes to break (default: 1.5)
* **resistance**: Explosion resistance (default: 6.0)
* **requires_tool**: Whether the block requires a tool to drop items (default: False)
* **light_level**: Light emission level 0-15 (default: 0)

Understanding Block Properties
------------------------------

Hardness and Resistance
~~~~~~~~~~~~~~~~~~~~~~~

* **Hardness**: Time to break the block (higher = slower)
* **Resistance**: Explosion damage resistance (higher = more resistant)

.. code-block:: python

   # Soft block (like dirt)
   soft_block = fabricpy.Block(
       id="mymod:soft_clay",
       name="Soft Clay",
       hardness=0.5,      # Easy to break
       resistance=0.5     # Low explosion resistance
   )

   # Hard block (like obsidian)
   hard_block = fabricpy.Block(
       id="mymod:reinforced_steel",
       name="Reinforced Steel", 
       hardness=50.0,     # Very hard to break
       resistance=1200.0, # High explosion resistance
       requires_tool=True # Must use tool
   )

Light Emission
~~~~~~~~~~~~~~

.. code-block:: python

   # Glowing block
   glowstone_block = fabricpy.Block(
       id="mymod:magic_crystal",
       name="Magic Crystal",
       light_level=15,    # Maximum brightness
       hardness=0.3,
       resistance=0.3
   )

   # Dim light block
   lantern_block = fabricpy.Block(
       id="mymod:dim_lantern", 
       name="Dim Lantern",
       light_level=7,     # Medium brightness
       hardness=1.0,
       resistance=1.0
   )

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
       hardness=2.0,
       resistance=6.0,
       requires_tool=True,
       item_group=fabricpy.item_group.BUILDING_BLOCKS
   )

Ore Block
~~~~~~~~~

.. code-block:: python

   # Ore block - harder to break, requires tool
   ruby_ore = fabricpy.Block(
       id="mymod:ruby_ore",
       name="Ruby Ore",
       block_texture_path="textures/blocks/ruby_ore.png", 
       hardness=3.0,      # Stone-like hardness
       resistance=3.0,
       requires_tool=True, # Must use pickaxe
       item_group=fabricpy.item_group.NATURAL
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
       hardness=5.0,
       resistance=6.0,
       requires_tool=True
   )

Machine Block
~~~~~~~~~~~~~

.. code-block:: python

   # Machine/functional block
   smelter = fabricpy.Block(
       id="mymod:magic_smelter",
       name="Magic Smelter",
       block_texture_path="textures/blocks/magic_smelter.png",
       hardness=3.5,
       resistance=3.5,
       requires_tool=True,
       light_level=13,    # Glows when active
       item_group=fabricpy.item_group.FUNCTIONAL
   )

Block Categories by Use Case
----------------------------

Building Blocks
~~~~~~~~~~~~~~~

.. code-block:: python

   building_blocks = [
       fabricpy.Block(
           id="mymod:stone_bricks",
           name="Polished Stone Bricks",
           hardness=2.0,
           resistance=6.0,
           requires_tool=True
       ),
       fabricpy.Block(
           id="mymod:wooden_planks", 
           name="Oak Planks",
           hardness=2.0,
           resistance=3.0
       )
   ]

Natural Blocks
~~~~~~~~~~~~~~

.. code-block:: python

   natural_blocks = [
       fabricpy.Block(
           id="mymod:crystal_ore",
           name="Crystal Ore",
           hardness=3.0,
           resistance=3.0,
           requires_tool=True,
           item_group=fabricpy.item_group.NATURAL
       ),
       fabricpy.Block(
           id="mymod:mystical_log",
           name="Mystical Log", 
           hardness=2.0,
           resistance=2.0,
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
           light_level=8,
           hardness=0.0,     # Instant break
           resistance=0.0,
           item_group=fabricpy.item_group.DECORATIONS
       ),
       fabricpy.Block(
           id="mymod:crystal_glass",
           name="Crystal Glass",
           hardness=0.3,
           resistance=0.3,
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
           hardness=5.0,
           resistance=1200.0,
           requires_tool=True,
           light_level=12,
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
           hardness=4.0,
           resistance=4.0,
           requires_tool=True,
           item_group=fabricpy.item_group.NATURAL
       ),
       
       # Storage block  
       fabricpy.Block(
           id="blocks_mod:titanium_block",
           name="Titanium Block",
           block_texture_path="textures/blocks/titanium_block.png",
           hardness=6.0,
           resistance=8.0,
           requires_tool=True,
           item_group=fabricpy.item_group.BUILDING_BLOCKS
       ),
       
       # Light source
       fabricpy.Block(
           id="blocks_mod:crystal_lamp",
           name="Crystal Lamp",
           block_texture_path="textures/blocks/crystal_lamp.png",
           light_level=15,
           hardness=1.0,
           resistance=1.0,
           item_group=fabricpy.item_group.DECORATIONS
       ),
       
       # Decorative
       fabricpy.Block(
           id="blocks_mod:marble_pillar",
           name="Marble Pillar", 
           block_texture_path="textures/blocks/marble_pillar.png",
           hardness=2.5,
           resistance=6.0,
           requires_tool=True,
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
  * 8-11: Medium lighting  
  * 12-15: Bright lighting

Best Practices
--------------

1. **Choose Appropriate Hardness**
   
   * Match similar vanilla blocks for consistency
   * Ore blocks: 3.0-5.0 hardness
   * Building blocks: 1.5-3.0 hardness
   * Decorative blocks: 0.3-2.0 hardness

2. **Set Tool Requirements**
   
   * Stone-like blocks: ``requires_tool=True``
   * Soft/decorative blocks: ``requires_tool=False``
   * Always consider mining progression

3. **Light Level Balance**
   
   * Don't make too many max brightness (15) blocks
   * Use medium levels (7-11) for atmosphere
   * Reserve level 15 for special/rare blocks

4. **Texture Organization**
   
   * Keep block textures in ``textures/blocks/``
   * Use descriptive filenames
   * Maintain 16x16 resolution for vanilla consistency

5. **Creative Tab Assignment**
   
   * Building materials: ``BUILDING_BLOCKS``
   * Ores and natural: ``NATURAL``
   * Functional items: ``FUNCTIONAL`` 
   * Decorative items: ``DECORATIONS``

Common Issues
-------------

* **Block not appearing**: Ensure block is registered with ``mod.registerBlock()``
* **Missing texture**: Check block_texture_path and file existence
* **Wrong mining behavior**: Verify hardness and requires_tool settings
* **BlockItem missing**: fabricpy automatically creates BlockItems - check creative tab

Next Steps
----------

* Learn about :doc:`custom-recipes` to add block crafting and smelting recipes
* Explore :doc:`creating-items` for tools that interact with blocks
* See :doc:`vanilla-item-groups` for appropriate block categorization
