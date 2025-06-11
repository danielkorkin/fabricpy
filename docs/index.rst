.. fabricpy documentation master file, created by
   sphinx-quickstart on Tue Jun 10 17:15:08 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

fabricpy documentation
======================

FabricPy is a lightweight helper library for writing Fabric mods in Python. It provides a simple, Pythonic interface for creating Minecraft Fabric mods without needing to write Java directly.

Features
--------

* **Item Registration**: Easy creation of custom items and food items
* **Block Registration**: Simple block creation with automatic BlockItem generation  
* **Recipe Support**: Built-in recipe JSON handling for crafting, smelting, etc.
* **Creative Tabs**: Support for both vanilla and custom creative inventory tabs
* **Automatic Compilation**: Generates complete Fabric mod projects from Python code
* **Google Docstrings**: Comprehensive documentation with examples

Quick Start
-----------

Here's a simple example of creating a mod with FabricPy:

.. code-block:: python

   import fabricpy

   # Create mod configuration
   mod = fabricpy.ModConfig(
       mod_id="mymod",
       name="My Awesome Mod", 
       version="1.0.0",
       description="Adds cool items to Minecraft",
       authors=["Your Name"]
   )

   # Create and register an item
   item = fabricpy.Item(
       id="mymod:cool_sword",
       name="Cool Sword",
       item_group=fabricpy.item_group.COMBAT
   )
   mod.registerItem(item)

   # Compile and run
   mod.compile()
   mod.run()

Helpful Tools
-------------

* `Crafting Recipe Generator <https://crafting.thedestruc7i0n.ca/>`_ - Visual interface for creating crafting recipe JSON files

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   
.. toctree::
   :maxdepth: 2
   :caption: API Documentation:

   api
   
.. toctree::
   :maxdepth: 2
   :caption: Module Details:

   fabricpy

