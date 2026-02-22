Quick Start Guide
=================

This guide will help you get started with fabricpy quickly.

Installation
------------

First, ensure you have Python 3.10+ installed, then install fabricpy:

.. code-block:: bash

   pip install fabricpy

External Requirements
---------------------

Before using fabricpy, you need to install these external dependencies:

1. Java Development Kit (JDK)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Version Required**: JDK 17 or higher (recommended JDK 21)
* **Purpose**: Compiles the generated Minecraft Fabric mod code
* **Installation**:
    * **macOS**: ``brew install openjdk@21`` or download from `Oracle <https://www.oracle.com/java/technologies/downloads/>`_
    * **Windows**: Download from `Oracle <https://www.oracle.com/java/technologies/downloads/>`_ or use ``winget install Oracle.JDK.21``
    * **Linux**: ``sudo apt install openjdk-21-jdk`` (Ubuntu/Debian) or ``sudo yum install java-21-openjdk-devel`` (CentOS/RHEL)

2. Git
~~~~~~

* **Version Required**: 2.0 or higher
* **Purpose**: Version control and cloning Fabric mod templates
* **Installation**:
    * **macOS**: ``brew install git`` or install Xcode Command Line Tools
    * **Windows**: Download from `git-scm.com <https://git-scm.com/>`_
    * **Linux**: ``sudo apt install git`` (Ubuntu/Debian) or ``sudo yum install git`` (CentOS/RHEL)

3. Gradle (Optional but recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Version Required**: 8.0 or higher
* **Purpose**: Build system for Minecraft mods (auto-downloaded by Gradle Wrapper if not installed)
* **Installation**:
    * **macOS**: ``brew install gradle``
    * **Windows**: ``choco install gradle`` or download from `gradle.org <https://gradle.org/>`_
    * **Linux**: ``sudo apt install gradle`` or download from `gradle.org <https://gradle.org/>`_

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
       description="My first fabricpy mod",
       authors=["Your Name"]
   )

   # Create a simple item
   ruby = fabricpy.Item(
       id="tutorial_mod:ruby",
       name="Ruby",
       item_group=fabricpy.item_group.INGREDIENTS
   )

   # Create a tool item
   ruby_pickaxe = fabricpy.ToolItem(
       id="tutorial_mod:ruby_pickaxe",
       name="Ruby Pickaxe",
       durability=500,
       mining_speed_multiplier=8.0,
       attack_damage=3.0,
       mining_level=2,
       enchantability=22,
       repair_ingredient="tutorial_mod:ruby",
       item_group=fabricpy.item_group.TOOLS,
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
       item_group=fabricpy.item_group.BUILDING_BLOCKS,
       loot_table=fabricpy.LootTable.drops_self("tutorial_mod:ruby_block"),
   )

   # Register all items and blocks
   mod.registerItem(ruby)
   mod.registerItem(ruby_pickaxe)
   mod.registerFoodItem(ruby_apple)
   mod.registerBlock(ruby_block)

   # Compile and run the mod
   mod.compile()
   mod.run()

Next Steps
----------

- Learn about creating recipes (see the RecipeJson class in the API reference)
- Use the `Crafting Recipe Generator <https://crafting.thedestruc7i0n.ca/>`_ to easily create crafting recipe JSON files with a visual interface
- Define loot tables for your blocks (see the :doc:`guides/loot-tables` guide)
- Understand custom creative tabs (see the ItemGroup class in the API reference)
- Explore the :doc:`complete API reference <api>`

Examples
--------

Example scripts can be found in the ``examples`` directory.

.. literalinclude:: ../examples/basic_mod.py
   :caption: Minimal mod — one item, one block
   :language: python

.. literalinclude:: ../examples/food_items.py
   :caption: Food items with nutrition, smelting, and always\_edible
   :language: python

.. literalinclude:: ../examples/blocks_and_recipes.py
   :caption: Blocks with recipes, textures, and click events
   :language: python

.. literalinclude:: ../examples/custom_item_group.py
   :caption: Custom creative tabs
   :language: python

.. literalinclude:: ../examples/tool_item.py
   :caption: Defining a custom ToolItem
   :language: python

.. literalinclude:: ../examples/loot_table.py
   :caption: Loot table patterns (self-drops, fortune, silk touch, entity & chest)
   :language: python

.. literalinclude:: ../examples/full_mod.py
   :caption: Complete mod — all features combined
   :language: python
