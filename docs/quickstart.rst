Quick Start Guide
=================

This guide will help you get started with FabricPy quickly.

Installation
------------

First, ensure you have Python 3.8+ installed, then install FabricPy:

.. code-block:: bash

   pip install fabricpy

Creating Your First Mod
------------------------

Here's a complete example of creating a simple mod:

.. code-block:: python

   import fabricpy

   # Create the mod configuration
   mod = fabricpy.ModConfig(
       mod_id="tutorial_mod",
       name="Tutorial Mod",
       version="1.0.0", 
       description="My first FabricPy mod",
       authors=["Your Name"]
   )

   # Create a simple item
   ruby = fabricpy.Item(
       id="tutorial_mod:ruby",
       name="Ruby",
       item_group=fabricpy.item_group.INGREDIENTS
   )

   # Create a food item
   ruby_apple = fabricpy.FoodItem(
       id="tutorial_mod:ruby_apple",
       name="Ruby Apple",
       nutrition=6,
       saturation=12.0,
       item_group=fabricpy.item_group.FOOD_AND_DRINK
   )

   # Create a block
   ruby_block = fabricpy.Block(
       id="tutorial_mod:ruby_block", 
       name="Ruby Block",
       item_group=fabricpy.item_group.BUILDING_BLOCKS
   )

   # Register all items and blocks
   mod.registerItem(ruby)
   mod.registerFoodItem(ruby_apple)
   mod.registerBlock(ruby_block)

   # Compile and run the mod
   mod.compile()
   mod.run()

Next Steps
----------

- Learn about creating recipes (see the RecipeJson class in the API reference)
- Understand custom creative tabs (see the ItemGroup class in the API reference)
- Explore the :doc:`complete API reference <api>`
