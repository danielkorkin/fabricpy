# fabricpy

![Codecov](https://img.shields.io/codecov/c/gh/danielkorkin/fabricpy) ![PyPI - Version](https://img.shields.io/pypi/v/fabricpy) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/danielkorkin/fabricpy/.github%2Fworkflows%2Ftest-and-coverage.yml) ![PyPI - License](https://img.shields.io/pypi/l/fabricpy) ![Read the Docs](https://img.shields.io/readthedocs/fabricpy)

Python Library that allows you to create Fabric Minecraft mods in Python! Write your mod logic in Python and automatically generate a complete, buildable Fabric mod project with Java source files, assets, and testing integration.

## Features

✨ **Easy Mod Creation**: Define items, tools, blocks, and food with simple Python classes
🔧 **Full Fabric Integration**: Generates complete mod projects compatible with Fabric Loader  
⛏️ **Mining Configuration**: Hardness, resistance, tool types, mining levels, and per-tool speed overrides  
🧪 **Built-in Testing**: Automatically generates unit tests and game tests  
🎨 **Custom Creative Tabs**: Create your own creative inventory tabs  
📝 **Recipe Support**: Define crafting recipes with JSON  
🎲 **Loot Tables**: Native loot table support with builder methods for common drop patterns  
🚀 **One-Click Building**: Compile and run your mod directly from Python  

## Installation

Install fabricpy using pip:

```bash
pip install fabricpy
```

## External Requirements

Before using fabricpy, you need to install these external dependencies:

### 1. Java Development Kit (JDK)
* **Version Required**: JDK 17 or higher (recommended JDK 21)
* **Purpose**: Compiles the generated Minecraft Fabric mod code
* **Installation**:
    * **macOS**: `brew install openjdk@21` or download from [Oracle](https://www.oracle.com/java/technologies/downloads/)
    * **Windows**: Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or use `winget install Oracle.JDK.21`
    * **Linux**: `sudo apt install openjdk-21-jdk` (Ubuntu/Debian) or `sudo yum install java-21-openjdk-devel` (CentOS/RHEL)

### 2. Git
* **Version Required**: 2.0 or higher
* **Purpose**: Version control and cloning Fabric mod templates
* **Installation**:
    * **macOS**: `brew install git` or install Xcode Command Line Tools
    * **Windows**: Download from [git-scm.com](https://git-scm.com/)
    * **Linux**: `sudo apt install git` (Ubuntu/Debian) or `sudo yum install git` (CentOS/RHEL)

### 3. Gradle (Optional but recommended)
* **Version Required**: 8.0 or higher
* **Purpose**: Build system for Minecraft mods (auto-downloaded by Gradle Wrapper if not installed)
* **Installation**:
    * **macOS**: `brew install gradle`
    * **Windows**: `choco install gradle` or download from [gradle.org](https://gradle.org/)
    * **Linux**: `sudo apt install gradle` or download from [gradle.org](https://gradle.org/)

## Quick Start

```python
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

# Create a tool
pickaxe = fabricpy.ToolItem(
    id="mymod:ruby_pickaxe",
    name="Ruby Pickaxe",
    durability=500,
    mining_speed_multiplier=8.0,
    attack_damage=3.0,
    mining_level=2,
    enchantability=22,
    repair_ingredient="minecraft:ruby"
)
mod.registerItem(pickaxe)

# Create a food item
apple = fabricpy.FoodItem(
    id="mymod:golden_apple",
    name="Golden Apple", 
    nutrition=6,
    saturation=12.0,
    always_edible=True
)
mod.registerFoodItem(apple)

# Create a block
block = fabricpy.Block(
    id="mymod:ruby_block",
    name="Ruby Block",
    item_group=fabricpy.item_group.BUILDING_BLOCKS,
    loot_table=fabricpy.LootTable.drops_self("mymod:ruby_block")
)
mod.registerBlock(block)

# Compile and run
mod.compile()
mod.run()
```

## Examples

Additional example scripts can be found in the [`examples`](examples/) directory.

| Script | What it shows |
|---|---|
| `basic_mod.py` | Minimal mod — one item, one block, mod config |
| `food_items.py` | Food items with nutrition, smelting recipes, `always_edible` |
| `blocks_and_recipes.py` | Blocks with recipes, textures, click events, subclasses |
| `custom_item_group.py` | Custom creative tabs and assigning items to them |
| `tool_item.py` | Defining and registering a custom `ToolItem` |
| `loot_table.py` | Loot table patterns: self-drops, fortune, silk touch, entity & chest loot |
| `mining_blocks.py` | Mining config: hardness, tool types, mining levels, per-tool speeds |
| `full_mod.py` | Complete mod tying together every library feature |

## Advanced Features

### Custom Creative Tabs

```python
# Create a custom creative tab
custom_tab = fabricpy.ItemGroup(
    id="my_weapons",
    name="My Weapons"
)

# Use the custom tab
sword = fabricpy.Item(
    id="mymod:diamond_sword",
    name="Diamond Sword",
    item_group=custom_tab
)
```

### Crafting Recipes

```python
# Define a shaped recipe
recipe = fabricpy.RecipeJson({
    "type": "minecraft:crafting_shaped",
    "pattern": ["###", "#X#", "###"],
    "key": {
        "#": "minecraft:gold_ingot",
        "X": "minecraft:apple"
    },
    "result": {"id": "mymod:golden_apple", "count": 1}
})

# Attach recipe to item
apple = fabricpy.FoodItem(
    id="mymod:golden_apple",
    name="Golden Apple",
    recipe=recipe
)
```

**💡 Tip**: Use the [Crafting Recipe Generator](https://crafting.thedestruc7i0n.ca/) to easily create crafting recipe JSON files with a visual interface!

### Loot Tables

```python
# Block that drops itself
block = fabricpy.Block(
    id="mymod:ruby_block",
    name="Ruby Block",
    loot_table=fabricpy.LootTable.drops_self("mymod:ruby_block")
)

# Ore with fortune-affected drops
ore = fabricpy.Block(
    id="mymod:ruby_ore",
    name="Ruby Ore",
    loot_table=fabricpy.LootTable.drops_with_fortune(
        "mymod:ruby_ore", "mymod:ruby",
        min_count=1, max_count=2
    )
)

# Silk-touch-only glass
glass = fabricpy.Block(
    id="mymod:crystal_glass",
    name="Crystal Glass",
    loot_table=fabricpy.LootTable.drops_with_silk_touch("mymod:crystal_glass")
)

# Entity loot table
from fabricpy import LootPool, LootTable

zombie_loot = LootTable.entity([
    LootPool()
        .rolls(1)
        .entry("mymod:fang", weight=3)
        .entry("mymod:eye", weight=1)
])
mod.registerLootTable("custom_zombie", zombie_loot)
```

### Mining Tools & Speeds

Configure how blocks are mined, which tools are required, and per-tool speed overrides:

```python
# Ore that requires an iron pickaxe
ruby_ore = fabricpy.Block(
    id="mymod:ruby_ore",
    name="Ruby Ore",
    hardness=3.0,
    resistance=3.0,
    tool_type="pickaxe",
    mining_level="iron",
    loot_table=fabricpy.LootTable.drops_with_fortune(
        "mymod:ruby_ore", "mymod:ruby",
        min_count=1, max_count=3,
    )
)

# Block with per-tool speed overrides (pickaxe fast, shovel slower)
mixed_ore = fabricpy.Block(
    id="mymod:mixed_ore",
    name="Mixed Ore",
    hardness=4.0,
    resistance=4.0,
    requires_tool=True,
    mining_level="stone",
    mining_speeds={
        "pickaxe": 8.0,
        "shovel": 3.0,
    },
)

# Tough block that needs a diamond pickaxe
reinforced = fabricpy.Block(
    id="mymod:reinforced_block",
    name="Reinforced Block",
    hardness=25.0,
    resistance=600.0,
    tool_type="pickaxe",
    mining_level="diamond",
)
```

Valid tool types: `"pickaxe"`, `"axe"`, `"shovel"`, `"hoe"`, `"sword"`.
Valid mining levels: `"stone"`, `"iron"`, `"diamond"`.

### Testing Integration

fabricpy automatically generates comprehensive tests for your mod:

```bash
# Run unit tests
./gradlew test

# Run game tests (in-game testing)
./gradlew runGametest
```

## Documentation

📚 [Full Documentation](https://fabricpy.readthedocs.io/en/latest/)

## Code Coverage

📊 [Code Coverage Report](https://app.codecov.io/gh/danielkorkin/fabricpy/tree/main)

## Support

- 🐛 [Report Issues](https://github.com/danielkorkin/fabricpy/issues)
- 💬 [Discussions](https://github.com/danielkorkin/fabricpy/discussions)
- 📖 [Documentation](https://fabricpy.readthedocs.io/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- [@danielkorkin](https://www.github.com/danielkorkin)

---

**Made with ❤️ for the Minecraft modding community**
