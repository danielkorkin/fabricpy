Custom Recipes
==============

Recipes define how items and blocks can be crafted, smelted, or created through various game mechanics. fabricpy uses the RecipeJson class to handle Minecraft's recipe system with full support for all recipe types.

Understanding Recipe Types
--------------------------

Minecraft supports several recipe types:

* **Crafting Shaped**: Items arranged in specific patterns
* **Crafting Shapeless**: Items in any arrangement  
* **Smelting**: Single item + fuel in furnace
* **Blasting**: Single item + fuel in blast furnace
* **Smoking**: Food + fuel in smoker
* **Campfire Cooking**: Food cooked on campfire
* **Stonecutting**: Block cutting with stonecutter

Basic Recipe Creation
---------------------

Creating Shaped Recipes
~~~~~~~~~~~~~~~~~~~~~~~

Shaped recipes require items to be placed in specific positions:

.. code-block:: python

   import fabricpy

   # Simple sword recipe
   sword_recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shaped",
       "pattern": [
           " I ",
           " I ",
           " S "
       ],
       "key": {
           "I": "minecraft:iron_ingot",
           "S": "minecraft:stick"
       },
       "result": {"id": "mymod:iron_sword", "count": 1}
   })

Creating Shapeless Recipes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shapeless recipes allow items to be placed in any arrangement:

.. code-block:: python

   # Shapeless recipe for dye mixing
   purple_dye_recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shapeless", 
       "ingredients": [
           {"item": "minecraft:red_dye"},
           {"item": "minecraft:blue_dye"}
       ],
       "result": {"id": "minecraft:purple_dye", "count": 2}
   })

Creating Smelting Recipes
~~~~~~~~~~~~~~~~~~~~~~~~~

Smelting recipes process items in furnaces:

.. code-block:: python

   # Ore smelting recipe
   ingot_recipe = fabricpy.RecipeJson({
       "type": "minecraft:smelting",
       "ingredient": {"item": "mymod:copper_ore"},
       "result": {"id": "minecraft:copper_ingot", "count": 1},
       "experience": 0.7,
       "cookingtime": 200  # 10 seconds (200 ticks)
   })

Advanced Recipe Examples
------------------------

Complex Shaped Recipe
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Advanced crafting table recipe
   advanced_table_recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shaped",
       "pattern": [
           "DGD",
           "WTW",
           "WOW"
       ],
       "key": {
           "D": "minecraft:diamond",
           "G": "minecraft:gold_ingot", 
           "W": "minecraft:oak_planks",
           "T": "minecraft:crafting_table",
           "O": "minecraft:obsidian"
       },
       "result": {"id": "mymod:advanced_crafting_table", "count": 1}
   })

Multiple Output Recipe
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Recipe that produces multiple items
   gem_cutting_recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shapeless",
       "ingredients": [
           {"item": "mymod:raw_gem"},
           {"item": "minecraft:diamond"}
       ],
       "result": {"id": "mymod:cut_gem", "count": 4}
   })

Blasting Recipe
~~~~~~~~~~~~~~~

.. code-block:: python

   # Fast ore processing in blast furnace
   fast_steel_recipe = fabricpy.RecipeJson({
       "type": "minecraft:blasting",
       "ingredient": {"item": "mymod:iron_ore"},
       "result": {"id": "mymod:steel_ingot", "count": 1},
       "experience": 1.0,
       "cookingtime": 100  # 5 seconds (faster than smelting)
   })

Smoking Recipe
~~~~~~~~~~~~~~

.. code-block:: python

   # Food cooking in smoker
   cooked_fish_recipe = fabricpy.RecipeJson({
       "type": "minecraft:smoking", 
       "ingredient": {"item": "mymod:raw_tuna"},
       "result": {"id": "mymod:cooked_tuna", "count": 1},
       "experience": 0.35,
       "cookingtime": 100  # 5 seconds
   })

Campfire Cooking Recipe
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Campfire cooking recipe
   campfire_recipe = fabricpy.RecipeJson({
       "type": "minecraft:campfire_cooking",
       "ingredient": {"item": "mymod:raw_meat"},
       "result": {"id": "mymod:grilled_meat", "count": 1}, 
       "experience": 0.5,
       "cookingtime": 600  # 30 seconds
   })

Stonecutting Recipe
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Stonecutter recipe for efficient crafting
   stonecutter_recipe = fabricpy.RecipeJson({
       "type": "minecraft:stonecutting",
       "ingredient": {"item": "mymod:marble_block"},
       "result": {"id": "mymod:marble_stairs", "count": 1}
   })

Attaching Recipes to Items
--------------------------

Simple Attachment
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create recipe first
   recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shaped",
       "pattern": ["##", "##"],
       "key": {"#": "minecraft:iron_ingot"},
       "result": {"id": "mymod:iron_block", "count": 1}
   })

   # Attach to item/block
   iron_block = fabricpy.Block(
       id="mymod:iron_block",
       name="Iron Block",
       recipe=recipe
   )

Multiple Recipes for One Item
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Primary crafting recipe
   primary_recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shaped",
       "pattern": ["III", "III", "III"],
       "key": {"I": "minecraft:iron_ingot"}, 
       "result": {"id": "mymod:iron_block", "count": 1}
   })

   # Alternative smelting recipe
   smelting_recipe = fabricpy.RecipeJson({
       "type": "minecraft:smelting",
       "ingredient": {"item": "mymod:compressed_iron"},
       "result": {"id": "mymod:iron_block", "count": 1},
       "experience": 1.0,
       "cookingtime": 200
   })

   # Use primary recipe on the item
   iron_block = fabricpy.Block(
       id="mymod:iron_block", 
       name="Iron Block",
       recipe=primary_recipe
   )

   # Register alternative recipe separately through mod compilation

Recipe Categories by Use Case
-----------------------------

Tool and Weapon Recipes
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   tool_recipes = [
       # Pickaxe recipe
       fabricpy.RecipeJson({
           "type": "minecraft:crafting_shaped",
           "pattern": ["MMM", " S ", " S "],
           "key": {
               "M": "mymod:titanium_ingot",
               "S": "minecraft:stick"
           },
           "result": {"id": "mymod:titanium_pickaxe", "count": 1}
       }),
       
       # Sword recipe
       fabricpy.RecipeJson({
           "type": "minecraft:crafting_shaped", 
           "pattern": [" M ", " M ", " S "],
           "key": {
               "M": "mymod:titanium_ingot",
               "S": "minecraft:stick"
           },
           "result": {"id": "mymod:titanium_sword", "count": 1}
       })
   ]

Building Block Recipes
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   building_recipes = [
       # Storage block (9 ingots -> 1 block)
       fabricpy.RecipeJson({
           "type": "minecraft:crafting_shaped",
           "pattern": ["III", "III", "III"],
           "key": {"I": "mymod:silver_ingot"},
           "result": {"id": "mymod:silver_block", "count": 1}
       }),
       
       # Reverse recipe (1 block -> 9 ingots)
       fabricpy.RecipeJson({
           "type": "minecraft:crafting_shapeless",
           "ingredients": [{"item": "mymod:silver_block"}],
           "result": {"id": "mymod:silver_ingot", "count": 9}
       })
   ]

Food Recipes
~~~~~~~~~~~~

.. code-block:: python

   food_recipes = [
       # Complex food crafting
       fabricpy.RecipeJson({
           "type": "minecraft:crafting_shaped",
           "pattern": ["BWB", "MEM", "CCC"],
           "key": {
               "B": "minecraft:wheat",
               "W": "minecraft:water_bucket", 
               "M": "minecraft:milk_bucket",
               "E": "minecraft:egg",
               "C": "minecraft:cocoa_beans"
           },
           "result": {"id": "mymod:chocolate_cake", "count": 1}
       })
   ]

Processing Recipes
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   processing_recipes = [
       # Ore doubling in blast furnace
       fabricpy.RecipeJson({
           "type": "minecraft:blasting",
           "ingredient": {"item": "mymod:raw_titanium"},
           "result": {"id": "mymod:titanium_ingot", "count": 2},
           "experience": 2.0,
           "cookingtime": 150
       }),
       
       # Gem cutting with stonecutter
       fabricpy.RecipeJson({
           "type": "minecraft:stonecutting", 
           "ingredient": {"item": "mymod:raw_diamond"},
           "result": {"id": "minecraft:diamond", "count": 1}
       })
   ]

Complete Recipe Example
-----------------------

Here's a complete mod with various recipe types:

.. code-block:: python

   import fabricpy

   # Create mod
   mod = fabricpy.ModConfig(
       mod_id="recipes_mod",
       name="Recipes Mod",
       version="1.0.0",
       description="Demonstrates various recipe types",
       authors=["Recipe Master"]
   )

   # Create recipes
   recipes = {
       # Shaped crafting recipe
       "magic_wand": fabricpy.RecipeJson({
           "type": "minecraft:crafting_shaped",
           "pattern": [" D ", " S ", " S "],
           "key": {
               "D": "minecraft:diamond",
               "S": "minecraft:stick"
           },
           "result": {"id": "recipes_mod:magic_wand", "count": 1}
       }),
       
       # Smelting recipe
       "magic_ingot": fabricpy.RecipeJson({
           "type": "minecraft:smelting",
           "ingredient": {"item": "recipes_mod:magic_ore"},
           "result": {"id": "recipes_mod:magic_ingot", "count": 1},
           "experience": 1.5,
           "cookingtime": 300
       }),
       
       # Shapeless recipe  
       "magic_dust": fabricpy.RecipeJson({
           "type": "minecraft:crafting_shapeless",
           "ingredients": [
               {"item": "recipes_mod:magic_crystal"},
               {"item": "minecraft:redstone"}
           ],
           "result": {"id": "recipes_mod:magic_dust", "count": 4}
       })
   }

   # Create items with recipes
   items = [
       fabricpy.Item(
           id="recipes_mod:magic_wand",
           name="Magic Wand",
           recipe=recipes["magic_wand"],
           max_stack_size=1,
       ),
       
       fabricpy.Item(
           id="recipes_mod:magic_ingot", 
           name="Magic Ingot",
           recipe=recipes["magic_ingot"]
       ),
       
       fabricpy.Item(
           id="recipes_mod:magic_dust",
           name="Magic Dust",
           recipe=recipes["magic_dust"]
       )
   ]

   # Register items
   for item in items:
       mod.registerItem(item)

   # Compile and run
   mod.compile()
   mod.run()

Recipe Guidelines and Best Practices
------------------------------------

Cooking Times
~~~~~~~~~~~~~

* **Smelting**: 200 ticks (10 seconds) - standard
* **Blasting**: 100 ticks (5 seconds) - 2x faster
* **Smoking**: 100 ticks (5 seconds) - 2x faster  
* **Campfire**: 600 ticks (30 seconds) - 3x slower

Experience Values
~~~~~~~~~~~~~~~~~

* **Common ores**: 0.1-0.7 experience
* **Rare ores**: 1.0-2.0 experience
* **Food items**: 0.1-0.5 experience
* **Special materials**: 2.0+ experience

Pattern Design Tips
~~~~~~~~~~~~~~~~~~~

1. **Use logical layouts**: Sword = vertical line, pickaxe = T-shape
2. **Be consistent**: Similar tools should use similar patterns
3. **Consider resources**: Expensive items should require more materials
4. **Leave space**: Don't fill entire 3x3 grid unless necessary

Common Issues
-------------

* **Recipe not working**: Check JSON syntax and field names
* **Wrong output**: Verify result item ID matches registered item
* **Missing ingredients**: Ensure all key items exist in game
* **Cooking time issues**: Use ticks (20 ticks = 1 second)

Tips for Recipe Generators
---------------------------

Use online tools to create complex recipes:

* `Crafting Recipe Generator <https://crafting.thedestruc7i0n.ca/>`_ - Visual crafting interface
* `MinecraftJSON <https://www.minecraftjson.com/>`_ - Various JSON generators
* Always validate generated JSON before using in fabricpy

Next Steps
----------

* Learn about :doc:`creating-items` to create items that use your recipes
* Explore :doc:`creating-blocks` for block-related recipes
* See :doc:`custom-item-groups` to organize crafted items
