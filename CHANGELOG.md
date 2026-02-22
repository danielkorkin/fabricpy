# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2025-06-12

### Added
- **Loot Tables**: Native loot table support via `LootTable` and `LootPool` classes
- `LootTable.drops_self()` — block drops itself when broken
- `LootTable.drops_item()` — block drops a different item (fixed or ranged count)
- `LootTable.drops_nothing()` — block drops nothing
- `LootTable.drops_with_silk_touch()` — silk-touch-sensitive drops (glass/ore style)
- `LootTable.drops_with_fortune()` — fortune-affected ore-style drops
- `LootTable.entity()` / `LootTable.chest()` — entity and chest loot tables
- `LootPool` fluent builder with `.rolls()`, `.entry()`, `.condition()`, `.function()` chaining
- `Block(loot_table=...)` parameter for attaching loot tables to blocks
- `ModConfig.registerLootTable()` for standalone entity/chest loot tables
- Automatic loot table JSON writing during `mod.compile()`
- Comprehensive test suite (53 tests) for all loot table functionality
- Loot table documentation guide with examples for all drop patterns
- Example script `examples/loot_table.py` demonstrating common patterns

### Changed
- Updated Block class to accept optional `loot_table` parameter
- `ModConfig.compile()` now writes loot table JSON files to `data/<mod_id>/loot_table/`

### Documentation
- New "Loot Tables" guide in docs with complete API walkthrough
- Updated Block guide with loot table examples for ores and storage blocks
- Updated quickstart guide with loot table usage
- Updated README with loot table feature and examples
- Added `fabricpy.loottable` module to API reference

## [0.1.3] - 2025-06-11

### Fixed
- Fixed package name inconsistency in generated test files that caused build failures
- Fixed error when calling .build() method
- Test generation now preserves underscores in mod_id for package names, consistent with main code generation
- Updated import statements in generated test files to use correct package structure
- Fixed gametest directory structure to match actual package naming convention

## [0.1.2] - 2025-06-11

### Fixed
- Fixed bug when generating gradle.properties file
- Resolved issues with property file formatting and structure

### Added
- Additional test coverage for gradle.properties generation
- More comprehensive testing for build configuration files

### Testing
- Enhanced test suite with additional edge cases
- Improved validation tests for generated configuration files

## [0.1.1] - 2025-06-11

### Added
- Comprehensive documentation guides for all fabricpy components
- Guide for creating items with examples and best practices
- Guide for creating food items with nutrition guidelines
- Guide for creating blocks with texture management
- Guide for custom recipes with all recipe types
- Guide for custom item groups with organization strategies
- Guide for vanilla item groups with integration examples
- Enhanced README with better feature descriptions and examples
- More detailed API documentation with usage examples

### Changed
- Improved consistency in naming conventions across the library
- Enhanced type hints and parameter documentation
- Updated testing framework with better coverage
- Refined documentation structure for better navigation
- Improved code examples in documentation with more realistic scenarios
- Better organization of test files with clearer descriptions

### Documentation
- Added complete guide series covering all major features
- Enhanced Sphinx documentation with better cross-references
- Improved code examples with step-by-step explanations
- Added troubleshooting sections to guides
- Better integration with Read the Docs

### Testing
- Enhanced test descriptions and documentation
- Improved test organization and categorization
- Better test coverage reporting
- More comprehensive integration tests

## [0.1.0] - 2025-06-10

### Added
- Initial release of fabricpy
- Support for creating Fabric Minecraft mods in Python
- Item, Block, and Food item creation
- Creative tab management
- Recipe JSON generation
- Comprehensive testing suite
- Documentation with Sphinx
- Code coverage reporting

### Features
- **Easy Mod Creation**: Define items, blocks, and food with simple Python classes
- **Full Fabric Integration**: Generates complete mod projects compatible with Fabric Loader
- **Built-in Testing**: Automatically generates unit tests and game tests
- **Custom Creative Tabs**: Create your own creative inventory tabs
- **Recipe Support**: Define crafting recipes with JSON
- **One-Click Building**: Compile and run your mod directly from Python

### Documentation
- Complete API documentation
- Quick start guide
- Examples and tutorials
- Read the Docs integration

### Testing
- Comprehensive test suite with pytest
- Code coverage reporting
- Integration tests
- Performance tests
