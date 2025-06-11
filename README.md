# fabricpy

![Codecov](https://img.shields.io/codecov/c/gh/danielkorkin/fabricpy) ![PyPI - Version](https://img.shields.io/pypi/v/fabricpy) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/danielkorkin/fabricpy/.github%2Fworkflows%2Ftest-and-coverage.yml) ![PyPI - License](https://img.shields.io/pypi/l/fabricpy) ![PyPI - Downloads](https://img.shields.io/pypi/dm/fabricpy) ![Read the Docs](https://img.shields.io/readthedocs/fabricpy)

Python Library that allows you to create Fabric Minecraft mods in Python! Write your mod logic in Python and automatically generate a complete, buildable Fabric mod project with Java source files, assets, and testing integration.

## Features

✨ **Easy Mod Creation**: Define items, blocks, and food with simple Python classes  
🔧 **Full Fabric Integration**: Generates complete mod projects compatible with Fabric Loader  
🧪 **Built-in Testing**: Automatically generates unit tests and game tests  
🎨 **Custom Creative Tabs**: Create your own creative inventory tabs  
📝 **Recipe Support**: Define crafting recipes with JSON  
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
    item_group=fabricpy.item_group.BUILDING_BLOCKS
)
mod.registerBlock(block)

# Compile and run
mod.compile()
mod.run()
```

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
