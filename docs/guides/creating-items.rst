Creating Items
==============

Items are the fundamental building blocks of any Minecraft mod. In fabricpy, creating items is straightforward and follows Minecraft's item system conventions.

Basic Item Creation
-------------------

Here's how to create a simple item:

.. code-block:: python

   import fabricpy

   # Create a basic item
   ruby = fabricpy.Item(
       id="mymod:ruby",
       name="Ruby",
       item_group=fabricpy.item_group.INGREDIENTS
   )

Required Parameters
~~~~~~~~~~~~~~~~~~~

* **id**: The unique identifier for your item (format: ``modid:itemname``)
* **name**: The display name shown to players

Optional Parameters
~~~~~~~~~~~~~~~~~~~

* **item_group**: The creative tab where the item appears (default: ``None``)
* **texture_path**: Path to the item's texture file
* **recipe**: A RecipeJson object for crafting recipes
* **max_stack_size**: Maximum stack size (default: 64)

Advanced Item Examples
----------------------

Item with Custom Texture
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Item with custom texture
   magic_wand = fabricpy.Item(
       id="mymod:magic_wand",
       name="Magic Wand",
       texture_path="textures/items/magic_wand.png",
       item_group=fabricpy.item_group.TOOLS,
       max_stack_size=1
   )

Item with Recipe
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a recipe first
   recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shaped",
       "pattern": [
           " D ",
           " S ",
           " S "
       ],
       "key": {
           "D": "minecraft:diamond",
           "S": "minecraft:stick"
       },
       "result": {"id": "mymod:diamond_sword", "count": 1}
   })

   # Item with recipe
   diamond_sword = fabricpy.Item(
       id="mymod:diamond_sword",
       name="Diamond Sword",
       recipe=recipe,
       item_group=fabricpy.item_group.COMBAT,
       max_stack_size=1
   )

Rare Item
~~~~~~~~~

.. code-block:: python

   # Legendary gem item
   legendary_gem = fabricpy.Item(
       id="mymod:legendary_gem",
       name="Legendary Gem",
       item_group=fabricpy.item_group.INGREDIENTS,
       max_stack_size=16
   )

Complete Example
----------------

Here's a complete example showing how to create multiple items and register them with a mod:

.. code-block:: python

   import fabricpy

   # Create mod configuration
   mod = fabricpy.ModConfig(
       mod_id="gems_mod",
       name="Gems Mod",
       version="1.0.0",
       description="Adds various gems to Minecraft",
       authors=["Your Name"]
   )

   # Create various items
   items = [
       fabricpy.Item(
           id="gems_mod:ruby",
           name="Ruby",
           item_group=fabricpy.item_group.INGREDIENTS,
           texture_path="textures/items/ruby.png"
       ),
       fabricpy.Item(
           id="gems_mod:sapphire", 
           name="Sapphire",
           item_group=fabricpy.item_group.INGREDIENTS,
           texture_path="textures/items/sapphire.png"
       ),
       fabricpy.Item(
           id="gems_mod:emerald_shard",
           name="Emerald Shard",
           item_group=fabricpy.item_group.INGREDIENTS,
           max_stack_size=32
       )
   ]

   # Register all items
   for item in items:
       mod.registerItem(item)

   # Compile and run
   mod.compile()
   mod.run()

Best Practices
--------------

1. **Naming Conventions**
   
   * Use lowercase item IDs with underscores: ``mymod:magic_sword``
   * Use descriptive display names: ``"Magic Sword"`` instead of ``"ms"``

2. **Texture Organization**
   
   * Keep textures in a dedicated folder: ``textures/items/``
   * Use descriptive filenames matching your item IDs
   * Use 16x16 pixel textures for consistency with vanilla Minecraft

3. **Creative Tab Assignment**
   
   * Choose appropriate vanilla tabs for similar items
   * Create custom item groups for themed collections
   * Don't put too many items in one custom tab

4. **Stack Sizes**
   
   * Tools and weapons: ``max_stack_size=1``
   * Building materials: ``max_stack_size=64`` (default)
   * Rare items: ``max_stack_size=16`` or lower

Common Issues
-------------

* **Item not appearing**: Check that the item is registered with ``mod.registerItem()``
* **Missing texture**: Ensure texture path is correct and file exists
* **Wrong creative tab**: Verify the item_group parameter
* **Name not displaying**: Check that the name parameter is set correctly

Next Steps
----------

* Learn about :doc:`creating-food-items` for edible items
* Explore :doc:`custom-recipes` to add crafting recipes
* See :doc:`custom-item-groups` for organizing items in custom tabs
