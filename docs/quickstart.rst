Quick Start Guide
=================

This guide will help you get started with FabricPy quickly.

Installation
------------

First, ensure you have Python 3.8+ installed, then install FabricPy:

.. code-block:: bash

   pip install fabricpy

External Requirements
---------------------

Before using FabricPy, you need to install these external dependencies:

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
- Use the `Crafting Recipe Generator <https://crafting.thedestruc7i0n.ca/>`_ to easily create crafting recipe JSON files with a visual interface
- Understand custom creative tabs (see the ItemGroup class in the API reference)
- Explore the :doc:`complete API reference <api>`
