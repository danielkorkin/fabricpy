Custom Item Groups
==================

Custom item groups (creative tabs) allow you to organize your mod's items and blocks into dedicated creative inventory tabs. This provides better organization and makes it easier for players to find your mod's content.

Understanding Item Groups
-------------------------

Item groups are the tabs shown in the creative inventory:

* Each tab has an icon (usually an item from that category)
* Players can click tabs to browse different categories
* Vanilla has tabs like "Building Blocks", "Tools", "Combat", etc.
* Custom tabs appear alongside vanilla tabs

Basic Custom Item Group Creation
--------------------------------

Simple Custom Tab
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import fabricpy

   # Create a custom creative tab
   my_weapons = fabricpy.ItemGroup(
       id="my_weapons"
       name="My Weapons"
   )

   # Set an icon for the tab
   my_weapons.set_icon(MySwordItem)  # Use your sword item class as icon

Required Parameters
~~~~~~~~~~~~~~~~~~~

* **id**: Unique identifier for the item group (format: ``"group_name"``)
* **name**: Display name shown to players in the creative inventory

Optional Methods
~~~~~~~~~~~~~~~~

* **set_icon(item_class)**: Set the item displayed as the tab icon

Advanced Custom Item Group Examples
-----------------------------------

Food-Themed Tab
~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a food-themed tab
   custom_foods = fabricpy.ItemGroup(
       id="custom_foods"
       name="Custom Foods"
   )

   # Create a signature food item to use as icon
   golden_apple = fabricpy.FoodItem(
       id="mymod:golden_apple"
       name="Golden Apple"
       nutrition=6
       saturation=12.0
       item_group=custom_foods  # Assign to custom tab
   )

   # Set the food item as the tab icon
   custom_foods.set_icon(golden_apple)

Magic-Themed Tab
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a magic items tab
   magic_items = fabricpy.ItemGroup(
       id="magic_items", 
       name="Magic Items"
   )

   # Create magical items for this tab
   magic_wand = fabricpy.Item(
       id="mymod:magic_wand"
       name="Magic Wand"
       item_group=magic_items
       max_stack_size=1
   )

   # Use the wand as the tab icon
   magic_items.set_icon(magic_wand)

Tech/Machinery Tab
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a technology tab
   tech_items = fabricpy.ItemGroup(
       id="tech_items"
       name="Technology"
   )

   # Create tech items
   circuit_board = fabricpy.Item(
       id="mymod:circuit_board"
       name="Circuit Board", 
       item_group=tech_items
   )

   robot = fabricpy.Item(
       id="mymod:robot"
       name="Robot"
       item_group=tech_items
       max_stack_size=1
   )

   # Use the robot as icon
   tech_items.set_icon(robot)

Using Custom Item Groups
-------------------------

Assigning Items to Custom Tabs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create the custom tab
   gems_tab = fabricpy.ItemGroup(
       id="precious_gems"
       name="Precious Gems"
   )

   # Create items assigned to the custom tab
   gems = [
       fabricpy.Item(
           id="mymod:ruby"
           name="Ruby"
           item_group=gems_tab  # Assign to custom tab
       )
       fabricpy.Item(
           id="mymod:sapphire", 
           name="Sapphire"
           item_group=gems_tab
       )
       fabricpy.Item(
           id="mymod:emerald_shard"
           name="Emerald Shard", 
           item_group=gems_tab
       )
   ]

   # Set ruby as the tab icon
   gems_tab.set_icon(gems[0])  # Use first gem as icon

Mixed Content Tab
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Tab for various mod content
   mod_content = fabricpy.ItemGroup(
       id="my_mod_items"
       name="My Mod"
   )

   # Mix of different item types
   items = [
       fabricpy.Item(
           id="mymod:special_tool"
           name="Special Tool"
           item_group=mod_content
       )
       fabricpy.FoodItem(
           id="mymod:magic_bread"
           name="Magic Bread"
           nutrition=5
           saturation=6.0
           item_group=mod_content
       )
       fabricpy.Block(
           id="mymod:custom_block"
           name="Custom Block"
           item_group=mod_content  # BlockItems use this too
       )
   ]

   # Use the tool as icon
   mod_content.set_icon(items[0])

Complete Custom Item Group Example
----------------------------------

Here's a complete mod with multiple custom item groups:

.. code-block:: python

   import fabricpy

   # Create mod
   mod = fabricpy.ModConfig(
       mod_id="fantasy_mod"
       name="Fantasy Mod"
       version="1.0.0"
       description="Adds fantasy elements to Minecraft"
       authors=["Fantasy Creator"]
   )

   # Create custom item groups
   weapons_tab = fabricpy.ItemGroup(
       id="fantasy_weapons"
       name="Fantasy Weapons"
   )

   magic_tab = fabricpy.ItemGroup(
       id="magic_items", 
       name="Magic & Potions"
   )

   materials_tab = fabricpy.ItemGroup(
       id="fantasy_materials"
       name="Fantasy Materials"
   )

   # Create weapons for weapons tab
   weapons = [
       fabricpy.Item(
           id="fantasy_mod:crystal_sword"
           name="Crystal Sword"
           item_group=weapons_tab
           max_stack_size=1
       )
       fabricpy.Item(
           id="fantasy_mod:magic_bow"
           name="Magic Bow"
           item_group=weapons_tab
           max_stack_size=1
       )
       fabricpy.Item(
           id="fantasy_mod:flame_dagger"
           name="Flame Dagger", 
           item_group=weapons_tab
           max_stack_size=1
       )
   ]

   # Create magic items for magic tab
   magic_items = [
       fabricpy.Item(
           id="fantasy_mod:spell_book"
           name="Spell Book"
           item_group=magic_tab
           max_stack_size=1
       )
       fabricpy.FoodItem(
           id="fantasy_mod:mana_potion"
           name="Mana Potion"
           nutrition=0
           saturation=0
           always_edible=True
           item_group=magic_tab
           max_stack_size=16
       )
       fabricpy.Item(
           id="fantasy_mod:crystal_orb"
           name="Crystal Orb"
           item_group=magic_tab
           max_stack_size=8
       )
   ]

   # Create materials for materials tab
   materials = [
       fabricpy.Item(
           id="fantasy_mod:mythril_ingot"
           name="Mythril Ingot"
           item_group=materials_tab
       )
       fabricpy.Item(
           id="fantasy_mod:dragon_scale"
           name="Dragon Scale"
           item_group=materials_tab
           max_stack_size=32
       )
       fabricpy.Item(
           id="fantasy_mod:phoenix_feather"
           name="Phoenix Feather"
           item_group=materials_tab
           max_stack_size=16
       )
   ]

   # Set tab icons
   weapons_tab.set_icon(weapons[0])      # Crystal sword
   magic_tab.set_icon(magic_items[0])    # Spell book  
   materials_tab.set_icon(materials[0])  # Mythril ingot

   # Register all items
   for item in weapons + magic_items + materials:
       mod.registerItem(item)

   # Compile and run
   mod.compile()
   mod.run()

Item Group Organization Strategies
----------------------------------

By Function
~~~~~~~~~~~

.. code-block:: python

   # Organize by what items do
   function_groups = {
       "tools": fabricpy.ItemGroup(id="mod_tools", name="Mod Tools")
       "weapons": fabricpy.ItemGroup(id="mod_weapons", name="Mod Weapons"), 
       "armor": fabricpy.ItemGroup(id="mod_armor", name="Mod Armor")
       "consumables": fabricpy.ItemGroup(id="mod_consumables", name="Consumables")
   }

By Material
~~~~~~~~~~~

.. code-block:: python

   # Organize by material type
   material_groups = {
       "copper": fabricpy.ItemGroup(id="copper_items", name="Copper Items")
       "steel": fabricpy.ItemGroup(id="steel_items", name="Steel Items")
       "crystal": fabricpy.ItemGroup(id="crystal_items", name="Crystal Items")
   }

By Theme
~~~~~~~~

.. code-block:: python

   # Organize by theme/aesthetic
   theme_groups = {
       "medieval": fabricpy.ItemGroup(id="medieval_items", name="Medieval")
       "futuristic": fabricpy.ItemGroup(id="future_items", name="Futuristic")
       "magical": fabricpy.ItemGroup(id="magic_items", name="Magical")
   }

Best Practices for Custom Item Groups
-------------------------------------

1. **Logical Organization**
   
   * Group related items together
   * Don't create too many small tabs
   * Aim for 8-20 items per tab for good balance

2. **Clear Naming**
   
   * Use descriptive tab names: "Magic Tools" vs "Misc"
   * Keep names concise but informative
   * Consider your target audience

3. **Appropriate Icons**
   
   * Choose representative items as icons
   * Use the most iconic/recognizable item from the group
   * Prefer items with distinctive textures

4. **Tab Count Limits**
   
   * Don't create too many custom tabs (3-6 max recommended)
   * Consider using vanilla tabs for common items
   * Only create custom tabs when you have enough content

5. **Consistency**
   
   * Use consistent naming patterns: "Mod Tools", "Mod Weapons"
   * Maintain similar organization across related mods
   * Follow conventions established by popular mods

Common Patterns
---------------

Single Mod Tab
~~~~~~~~~~~~~~

.. code-block:: python

   # Single tab for all mod content
   mod_tab = fabricpy.ItemGroup(
       id="mymod_items"
       name="My Mod"
   )
   # Use your most iconic item as icon

Category-Based Tabs
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Multiple tabs by category
   tools_tab = fabricpy.ItemGroup(id="mymod_tools", name="Mod Tools")
   blocks_tab = fabricpy.ItemGroup(id="mymod_blocks", name="Mod Blocks") 
   food_tab = fabricpy.ItemGroup(id="mymod_food", name="Mod Food")

Material Progression Tabs
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Tabs representing material tiers
   bronze_tab = fabricpy.ItemGroup(id="bronze_age", name="Bronze Age")
   steel_tab = fabricpy.ItemGroup(id="steel_age", name="Steel Age")
   mythril_tab = fabricpy.ItemGroup(id="mythril_age", name="Mythril Age")

Common Issues
-------------

* **Tab not appearing**: Ensure ItemGroup is assigned to at least one item
* **Wrong icon**: Check that icon item is properly created and registered
* **Tab order**: Custom tabs appear after vanilla tabs (cannot be reordered)
* **Empty tabs**: Tabs with no items won't appear in creative mode

Integration with Vanilla
------------------------

When to Use Custom vs Vanilla Tabs:

**Use Vanilla Tabs When:**
* Your items fit naturally into existing categories
* You have few items of a particular type
* You want seamless integration with vanilla

**Use Custom Tabs When:**
* You have many themed items
* Your content deserves its own category
* You want prominent mod branding
* Items don't fit well in vanilla categories

Next Steps
----------

* Learn about :doc:`vanilla-item-groups` for using existing creative tabs
* Explore :doc:`creating-items` to populate your custom tabs
* See :doc:`creating-blocks` for adding blocks to custom tabs
