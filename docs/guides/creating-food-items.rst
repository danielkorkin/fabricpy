Creating Food Items
=====================

Food items are special items that players can consume to restore hunger and saturation. fabricpy makes it easy to create food items with various nutritional properties and special effects.

Basic Food Item Creation
------------------------

Here's how to create a simple food item:

.. code-block:: python

   import fabricpy

   # Create a basic food item
   golden_apple = fabricpy.FoodItem(
       id="mymod:golden_apple",
       name="Golden Apple",
       nutrition=4,
       saturation=9.6
   )

Required Parameters
~~~~~~~~~~~~~~~~~~~

* **id**: The unique identifier for your food item (format: ``modid:itemname``)
* **name**: The display name shown to players
* **nutrition**: How many hunger points the food restores (half-drumsticks)
* **saturation**: How much saturation the food provides

Optional Parameters
~~~~~~~~~~~~~~~~~~~

* **item_group**: The creative tab (default: ``fabricpy.item_group.FOOD_AND_DRINK``)
* **texture_path**: Path to the item's texture file
* **recipe**: A RecipeJson object for crafting recipes
* **max_stack_size**: Maximum stack size (default: 64)
* **always_edible**: Whether the food can be eaten when hunger is full (default: False)

Understanding Food Properties
-----------------------------

Nutrition and Saturation
~~~~~~~~~~~~~~~~~~~~~~~~~

* **Nutrition**: The visible hunger points restored (each point = half a drumstick)
* **Saturation**: Hidden stat that delays hunger loss (higher = lasts longer)

.. code-block:: python

   # Low-tier food
   apple = fabricpy.FoodItem(
       id="mymod:red_apple",
       name="Red Apple", 
       nutrition=4,      # Restores 2 drumsticks
       saturation=2.4    # Low saturation
   )

   # High-tier food  
   golden_carrot = fabricpy.FoodItem(
       id="mymod:golden_carrot",
       name="Golden Carrot",
       nutrition=6,      # Restores 3 drumsticks
       saturation=14.4   # High saturation (lasts long)
   )

Special Food Properties
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Always edible (like golden apples)
   magical_bread = fabricpy.FoodItem(
       id="mymod:magical_bread",
       name="Magical Bread",
       nutrition=5,
       saturation=6.0,
       always_edible=True  # Can eat when full
   )

   # Quick consumption food
   energy_bar = fabricpy.FoodItem(
       id="mymod:energy_bar", 
       name="Energy Bar",
       nutrition=3,
       saturation=4.8
   )

   # High-nutrition food
   cooked_beef = fabricpy.FoodItem(
       id="mymod:premium_beef",
       name="Premium Beef",
       nutrition=8,
       saturation=12.8
   )

Advanced Food Examples
----------------------

Food with Custom Recipe
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a shaped recipe
   recipe = fabricpy.RecipeJson({
       "type": "minecraft:crafting_shaped",
       "pattern": [
           "GGG",
           "GAG", 
           "GGG"
       ],
       "key": {
           "G": "minecraft:gold_ingot",
           "A": "minecraft:apple"
       },
       "result": {"id": "mymod:golden_apple", "count": 1}
   })

   # Food item with recipe
   golden_apple = fabricpy.FoodItem(
       id="mymod:golden_apple",
       name="Golden Apple",
       nutrition=4,
       saturation=9.6,
       recipe=recipe,
       always_edible=True
   )

High-End Food Item
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Legendary food item
   ambrosia = fabricpy.FoodItem(
       id="mymod:ambrosia",
       name="Ambrosia",
       nutrition=20,         # Full hunger bar
       saturation=30.0,      # Maximum saturation  
       always_edible=True,
       max_stack_size=16,    # Limited stacking
       texture_path="textures/items/ambrosia.png"
   )

Food Categories by Use Case
---------------------------

Early Game Foods
~~~~~~~~~~~~~~~~

.. code-block:: python

   early_foods = [
       fabricpy.FoodItem(
           id="mymod:berry",
           name="Wild Berry",
           nutrition=2,
           saturation=1.2
       ),
       fabricpy.FoodItem(
           id="mymod:mushroom_stew",
           name="Mushroom Stew", 
           nutrition=6,
           saturation=7.2,
           max_stack_size=1  # Bowl items don't stack
       )
   ]

Mid Game Foods
~~~~~~~~~~~~~~

.. code-block:: python

   mid_foods = [
       fabricpy.FoodItem(
           id="mymod:honey_cake",
           name="Honey Cake",
           nutrition=7,
           saturation=8.4
       ),
       fabricpy.FoodItem(
           id="mymod:roasted_nuts",
           name="Roasted Nuts",
           nutrition=5,
           saturation=6.0
       )
   ]

End Game Foods  
~~~~~~~~~~~~~~

.. code-block:: python

   end_foods = [
       fabricpy.FoodItem(
           id="mymod:dragons_feast",
           name="Dragon's Feast",
           nutrition=12,
           saturation=20.0,
           always_edible=True,
           max_stack_size=4
       )
   ]

Complete Example
----------------

Here's a complete mod with various food items:

.. code-block:: python

   import fabricpy

   # Create mod
   mod = fabricpy.ModConfig(
       mod_id="foodie_mod",
       name="Foodie Mod", 
       version="1.0.0",
       description="Adds delicious foods to Minecraft",
       authors=["Chef Player"]
   )

   # Create food items
   foods = [
       # Basic foods
       fabricpy.FoodItem(
           id="foodie_mod:cheese",
           name="Cheese",
           nutrition=3,
           saturation=4.8,
           texture_path="textures/items/cheese.png"
       ),
       
       # Meat foods
       fabricpy.FoodItem(
           id="foodie_mod:bacon",
           name="Bacon",
           nutrition=4,
           saturation=6.4,
           texture_path="textures/items/bacon.png"
       ),
       
       # Special foods
       fabricpy.FoodItem(
           id="foodie_mod:energy_drink",
           name="Energy Drink", 
           nutrition=2,
           saturation=8.0,
           always_edible=True,
           max_stack_size=16,
           texture_path="textures/items/energy_drink.png"
       ),
       
       # High-tier food
       fabricpy.FoodItem(
           id="foodie_mod:gourmet_meal",
           name="Gourmet Meal",
           nutrition=10,
           saturation=16.0,
           always_edible=True,
           max_stack_size=1,
           texture_path="textures/items/gourmet_meal.png"
       )
   ]

   # Register all foods  
   for food in foods:
       mod.registerFoodItem(food)

   # Compile and run
   mod.compile()
   mod.run()

Food Value Guidelines
---------------------

Here are recommended nutrition/saturation values for different food tiers:

**Snacks (Tier 1)**
  * Nutrition: 1-3
  * Saturation: 0.6-3.6
  * Examples: Berries, nuts, crackers

**Meals (Tier 2)**  
  * Nutrition: 4-7
  * Saturation: 4.8-8.4
  * Examples: Bread, cooked meat, fruits

**Feast Foods (Tier 3)**
  * Nutrition: 8-12  
  * Saturation: 9.6-14.4
  * Examples: Cakes, stews, golden foods

**Legendary Foods (Tier 4)**
  * Nutrition: 13-20
  * Saturation: 15.6-30.0
  * Examples: Magical foods, end-game items

Best Practices
--------------

1. **Balance Nutrition and Saturation**
   
   * High nutrition = immediate hunger relief
   * High saturation = longer-lasting effect
   * Both high = premium food item

2. **Use Appropriate Properties**
   
   * Set ``always_edible=True`` for special/magical foods only

3. **Stack Size Considerations**
   
   * Bowl foods: ``max_stack_size=1``
   * Premium foods: ``max_stack_size=16`` or lower
   * Regular foods: ``max_stack_size=64`` (default)

Common Issues
-------------

* **Food not consumable**: Check nutrition value is > 0
* **Wrong hunger restoration**: Verify nutrition parameter (not saturation)
* **Can't eat when full**: Set ``always_edible=True`` if intended
* **Food too powerful**: Balance nutrition/saturation with vanilla foods

Next Steps
----------

* Learn about :doc:`custom-recipes` to add food crafting recipes
* Explore :doc:`creating-blocks` for food-related blocks like ovens
* See :doc:`vanilla-item-groups` for appropriate food categorization
