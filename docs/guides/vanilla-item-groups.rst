Vanilla Item Groups
===================

Vanilla item groups are the built-in creative tabs that come with Minecraft. Using vanilla tabs helps your mod's items integrate seamlessly with the base game and makes them easier for players to find in familiar locations.

Available Vanilla Item Groups
-----------------------------

fabricpy provides access to all vanilla creative tabs through the ``fabricpy.item_group`` module:

Core Vanilla Tabs
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import fabricpy

   # Building and resource tabs
   building_blocks = fabricpy.item_group.BUILDING_BLOCKS
   natural = fabricpy.item_group.NATURAL
   functional = fabricpy.item_group.FUNCTIONAL

   # Tool and equipment tabs
   tools = fabricpy.item_group.TOOLS
   combat = fabricpy.item_group.COMBAT
   
   # Resource tabs
   ingredients = fabricpy.item_group.INGREDIENTS
   
   # Miscellaneous tabs
   food_and_drink = fabricpy.item_group.FOOD_AND_DRINK
   redstone = fabricpy.item_group.REDSTONE
   spawn_eggs = fabricpy.item_group.SPAWN_EGGS

Complete List of Vanilla Groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are all available vanilla item groups and their typical contents:

**BUILDING_BLOCKS**
  * Stone, wood, concrete, terracotta
  * Structural blocks for construction

**NATURAL**
  * Logs, dirt, ores, plants
  * Naturally occurring materials

**FUNCTIONAL**
  * Chests, furnaces, crafting tables
  * Blocks with game mechanics

**REDSTONE**
  * Redstone dust, repeaters, pistons
  * Redstone mechanics and components

**TOOLS**
  * Pickaxes, shovels, axes, hoes
  * Utility tools for gathering

**COMBAT**
  * Swords, bows, armor
  * Weapons and protective equipment

**FOOD_AND_DRINK**
  * Food items, potions
  * Consumable items

**INGREDIENTS**
  * Crafting components, materials
  * Items used to make other items

**SPAWN_EGGS**
  * Spawn eggs for entities
  * Entity summoning items

Using Vanilla Item Groups
-------------------------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   import fabricpy

   # Create items using vanilla tabs
   items = [
       fabricpy.Item(
           id="mymod:iron_hammer",
           name="Iron Hammer",
           item_group=fabricpy.item_group.TOOLS  # Tools tab
       ),
       
       fabricpy.Item(
           id="mymod:steel_sword",
           name="Steel Sword", 
           item_group=fabricpy.item_group.COMBAT  # Combat tab
       ),
       
       fabricpy.Item(
           id="mymod:ruby_gem",
           name="Ruby Gem",
           item_group=fabricpy.item_group.INGREDIENTS  # Ingredients tab
       )
   ]

Item Type Examples by Tab
-------------------------

Building Blocks Tab
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Blocks for construction
   building_items = [
       fabricpy.Block(
           id="mymod:marble_block",
           name="Marble Block",
           item_group=fabricpy.item_group.BUILDING_BLOCKS
       ),
       
       fabricpy.Block(
           id="mymod:steel_block", 
           name="Steel Block",
           item_group=fabricpy.item_group.BUILDING_BLOCKS
       ),
       
       fabricpy.Block(
           id="mymod:reinforced_concrete",
           name="Reinforced Concrete",
           item_group=fabricpy.item_group.BUILDING_BLOCKS
       )
   ]

Natural Tab
~~~~~~~~~~~

.. code-block:: python

   # Naturally occurring materials
   natural_items = [
       fabricpy.Block(
           id="mymod:copper_ore",
           name="Copper Ore",
           item_group=fabricpy.item_group.NATURAL
       ),
       
       fabricpy.Block(
           id="mymod:mystical_log",
           name="Mystical Log", 
           item_group=fabricpy.item_group.NATURAL
       ),
       
       fabricpy.Item(
           id="mymod:crystal_shard",
           name="Crystal Shard",
           item_group=fabricpy.item_group.NATURAL
       )
   ]

Tools Tab
~~~~~~~~~

.. code-block:: python

   # Utility tools
   tool_items = [
       fabricpy.Item(
           id="mymod:diamond_pickaxe",
           name="Diamond Pickaxe",
           item_group=fabricpy.item_group.TOOLS,
           max_stack_size=1
       ),
       
       fabricpy.Item(
           id="mymod:magic_shovel",
           name="Magic Shovel",
           item_group=fabricpy.item_group.TOOLS,
           max_stack_size=1,
       ),
       
       fabricpy.Item(
           id="mymod:multi_tool",
           name="Multi Tool",
           item_group=fabricpy.item_group.TOOLS,
           max_stack_size=1,
       )
   ]

Combat Tab
~~~~~~~~~~

.. code-block:: python

   # Weapons and armor
   combat_items = [
       fabricpy.Item(
           id="mymod:steel_sword",
           name="Steel Sword",
           item_group=fabricpy.item_group.COMBAT,
           max_stack_size=1
       ),
       
       fabricpy.Item(
           id="mymod:crossbow_enhanced",
           name="Enhanced Crossbow",
           item_group=fabricpy.item_group.COMBAT,
           max_stack_size=1,
       ),
       
       fabricpy.Item(
           id="mymod:plate_armor",
           name="Plate Armor",
           item_group=fabricpy.item_group.COMBAT,
           max_stack_size=1,
       )
   ]

Food and Drink Tab
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Consumable food items
   food_items = [
       fabricpy.FoodItem(
           id="mymod:energy_bar",
           name="Energy Bar",
           nutrition=5,
           saturation=6.0,
           item_group=fabricpy.item_group.FOOD_AND_DRINK
       ),
       
       fabricpy.FoodItem(
           id="mymod:healing_potion",
           name="Healing Potion",
           nutrition=0,
           saturation=0,
           always_edible=True,
           item_group=fabricpy.item_group.FOOD_AND_DRINK,
           max_stack_size=16
       ),
       
       fabricpy.FoodItem(
           id="mymod:gourmet_steak",
           name="Gourmet Steak", 
           nutrition=8,
           saturation=12.8,
           item_group=fabricpy.item_group.FOOD_AND_DRINK
       )
   ]

Ingredients Tab
~~~~~~~~~~~~~~~

.. code-block:: python

   # Crafting materials
   ingredient_items = [
       fabricpy.Item(
           id="mymod:steel_ingot",
           name="Steel Ingot",
           item_group=fabricpy.item_group.INGREDIENTS
       ),
       
       fabricpy.Item(
           id="mymod:magic_dust",
           name="Magic Dust",
           item_group=fabricpy.item_group.INGREDIENTS,
       ),
       
       fabricpy.Item(
           id="mymod:circuit_board",
           name="Circuit Board",
           item_group=fabricpy.item_group.INGREDIENTS
       )
   ]

Functional Tab
~~~~~~~~~~~~~~

.. code-block:: python

   # Functional blocks with mechanics
   functional_items = [
       fabricpy.Block(
           id="mymod:auto_smelter",
           name="Auto Smelter", 
           item_group=fabricpy.item_group.FUNCTIONAL
       ),
       
       fabricpy.Block(
           id="mymod:enchanting_altar",
           name="Enchanting Altar",
           item_group=fabricpy.item_group.FUNCTIONAL,
       ),
       
       fabricpy.Block(
           id="mymod:storage_crate",
           name="Storage Crate",
           item_group=fabricpy.item_group.FUNCTIONAL
       )
   ]

Decorations Tab
~~~~~~~~~~~~~~~

.. code-block:: python

   # Decorative items
   decoration_items = [
       fabricpy.Block(
           id="mymod:crystal_lamp",
           name="Crystal Lamp",
           item_group=fabricpy.item_group.DECORATIONS,
       ),
       
       fabricpy.Item(
           id="mymod:wall_banner",
           name="Wall Banner",
           item_group=fabricpy.item_group.DECORATIONS
       ),
       
       fabricpy.Block(
           id="mymod:decorative_pillar",
           name="Decorative Pillar",
           item_group=fabricpy.item_group.DECORATIONS
       )
   ]

Complete Vanilla Integration Example
====================================

Here's a complete mod that uses various vanilla tabs appropriately:

.. code-block:: python

   import fabricpy

   # Create mod
   mod = fabricpy.ModConfig(
       mod_id="integrated_mod",
       name="Integrated Mod",
       version="1.0.0", 
       description="Seamlessly integrates with vanilla Minecraft",
       authors=["Integration Expert"]
   )

   # Items organized by vanilla tabs
   all_items = [
       # Building materials
       fabricpy.Block(
           id="integrated_mod:marble_block",
           name="Marble Block",
           item_group=fabricpy.item_group.BUILDING_BLOCKS,
       ),
       
       fabricpy.Block(
           id="integrated_mod:granite_bricks",
           name="Granite Bricks", 
           item_group=fabricpy.item_group.BUILDING_BLOCKS,
       ),
       
       # Natural resources
       fabricpy.Block(
           id="integrated_mod:tin_ore",
           name="Tin Ore",
           item_group=fabricpy.item_group.NATURAL,
       ),
       
       # Crafting ingredients
       fabricpy.Item(
           id="integrated_mod:tin_ingot",
           name="Tin Ingot",
           item_group=fabricpy.item_group.INGREDIENTS
       ),
       
       fabricpy.Item(
           id="integrated_mod:bronze_ingot", 
           name="Bronze Ingot",
           item_group=fabricpy.item_group.INGREDIENTS
       ),
       
       # Tools
       fabricpy.Item(
           id="integrated_mod:bronze_pickaxe",
           name="Bronze Pickaxe",
           item_group=fabricpy.item_group.TOOLS,
           max_stack_size=1
       ),
       
       fabricpy.Item(
           id="integrated_mod:tin_shovel",
           name="Tin Shovel",
           item_group=fabricpy.item_group.TOOLS,
           max_stack_size=1
       ),
       
       # Combat items
       fabricpy.Item(
           id="integrated_mod:bronze_sword",
           name="Bronze Sword", 
           item_group=fabricpy.item_group.COMBAT,
           max_stack_size=1
       ),
       
       # Food items
       fabricpy.FoodItem(
           id="integrated_mod:tin_can_food",
           name="Canned Food",
           nutrition=6,
           saturation=7.2,
           item_group=fabricpy.item_group.FOOD_AND_DRINK
       ),
       
       # Functional blocks
       fabricpy.Block(
           id="integrated_mod:bronze_furnace", 
           name="Bronze Furnace",
           item_group=fabricpy.item_group.FUNCTIONAL,
       ),
       
       # Decorative items
       fabricpy.Block(
           id="integrated_mod:tin_lantern",
           name="Tin Lantern",
           item_group=fabricpy.item_group.DECORATIONS,
       )
   ]

   # Register all items
   for item in all_items:
       if hasattr(item, 'nutrition'):  # FoodItem
           mod.registerFoodItem(item)
       elif hasattr(item, 'block_texture_path'):  # Block  
           mod.registerBlock(item)
       else:  # Item
           mod.registerItem(item)

   # Compile and run
   mod.compile()
   mod.run()

Best Practices for Vanilla Tabs
-------------------------------

1. **Choose Appropriate Tabs**
   
   * Tools go in TOOLS tab, not MISCELLANEOUS
   * Building materials go in BUILDING_BLOCKS
   * Ores and natural materials go in NATURAL
   * Food items go in FOOD_AND_DRINK

2. **Follow Vanilla Conventions**
   
   * Study where similar vanilla items are placed
   * Maintain consistency with game expectations
   * Don't put items in unexpected locations

3. **Consider Player Experience**
   
   * Players expect to find tools in the tools tab
   * Building blocks should be with other building blocks
   * Keep related items together

4. **Balance Tab Population**
   
   * Don't overload any single tab
   * Spread items appropriately across tabs
   * Use MISCELLANEOUS sparingly

When to Use Vanilla vs Custom Tabs
----------------------------------

**Use Vanilla Tabs When:**
* Items fit naturally into existing categories
* You want seamless integration with vanilla
* You have few items of a particular type
* Your mod extends vanilla functionality

**Use Custom Tabs When:**
* You have many themed items (8+ items)
* Items form a cohesive collection
* You want prominent mod branding
* Items don't fit well in vanilla categories

Common Mistakes
---------------

* **Wrong tab choice**: Putting decorative blocks in TOOLS tab
* **Overusing MISCELLANEOUS**: Should be last resort
* **Ignoring item type**: Food items not in FOOD_AND_DRINK
* **Inconsistent placement**: Similar items in different tabs

Tab Reference Quick Guide
-------------------------

.. code-block:: python

   # Quick reference for common item types
   
   # Raw materials and ores
   item_group=fabricpy.item_group.NATURAL
   
   # Processed materials and components  
   item_group=fabricpy.item_group.INGREDIENTS
   
   # Structural blocks
   item_group=fabricpy.item_group.BUILDING_BLOCKS
   
   # Blocks with mechanics
   item_group=fabricpy.item_group.FUNCTIONAL
   
   # Aesthetic blocks
   item_group=fabricpy.item_group.DECORATIONS
   
   # Utility tools
   item_group=fabricpy.item_group.TOOLS
   
   # Weapons and armor
   item_group=fabricpy.item_group.COMBAT
   
   # Edible items
   item_group=fabricpy.item_group.FOOD_AND_DRINK

Next Steps
----------

* Learn about :doc:`custom-item-groups` for creating your own tabs
* Explore :doc:`creating-items` to understand item creation in detail
* See :doc:`creating-blocks` for block-specific considerations
