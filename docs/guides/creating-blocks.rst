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
* **max_stack_size**: Maximum stack size for the block item (default: 64)

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

   # Ore block with custom texture
   ruby_ore = fabricpy.Block(
       id="mymod:ruby_ore",
       name="Ruby Ore",
       block_texture_path="textures/blocks/ruby_ore.png", 
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
       recipe=recipe
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
           item_group=fabricpy.item_group.NATURAL
       ),
       
       # Storage block  
       fabricpy.Block(
           id="blocks_mod:titanium_block",
           name="Titanium Block",
           block_texture_path="textures/blocks/titanium_block.png",
           item_group=fabricpy.item_group.BUILDING_BLOCKS
       ),
       
       # Light source
       fabricpy.Block(
           id="blocks_mod:crystal_lamp",
           name="Crystal Lamp",
           block_texture_path="textures/blocks/crystal_lamp.png",
           item_group=fabricpy.item_group.DECORATIONS
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

* Learn about :doc:`custom-recipes` to add block crafting and smelting recipes
* Explore :doc:`creating-items` for tools that interact with blocks
* See :doc:`vanilla-item-groups` for appropriate block categorization
