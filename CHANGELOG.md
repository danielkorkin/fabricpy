# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-22

### Added
- **Block Actions & Hooks**: Event-driven block interaction system
  - Three block event hooks: `on_left_click` (attack via `AttackBlockCallback`), `on_right_click` (use via `UseBlockCallback`), `on_break` (after destruction via `PlayerBlockBreakEvents.AFTER`)
  - Declarative style via constructor parameters (`left_click_event`, `right_click_event`, `break_event`) or subclass method overrides
  - Multiple actions can be composed by returning a list from any hook method
- **`fabricpy.actions` module**: 16 ready-made Java code-snippet helpers for gameplay effects in block hooks
  - `replace_block` — swap a block for a different one
  - `teleport_player` — move the player to absolute or relative coordinates
  - `launch_player` — apply velocity impulse / knockback
  - `apply_effect` — grant a potion / status effect (`MobEffects` constants)
  - `play_sound` — play a sound at the block position (`SoundEvents` constants)
  - `summon_lightning` — strike lightning (server-side `ServerLevel` guard)
  - `drop_item` — drop item(s) at the block position
  - `place_fire` / `extinguish_area` — fire manipulation
  - `give_xp` / `remove_xp` — experience point changes
  - `damage_nearby` / `heal_nearby` — area-of-effect damage/healing
  - `delayed_action` — schedule code to run after a tick delay
  - `sculk_event` — emit a game event for sculk sensors
- **`fabricpy.message` module**: Message helper functions for player communication
  - `send_message` — send a chat message to the player
  - `send_action_bar_message` — send an action-bar overlay message
  - `console_print` — print to the server console (`System.out.println`)
- **Tool Items**: `ToolItem` class extending `Item` with tool-specific properties
  - `durability`, `mining_speed_multiplier`, `attack_damage`, `mining_level`, `enchantability`, `repair_ingredient`
  - Example script `examples/tool_item.py` demonstrating tool creation
- Example scripts `examples/block_actions.py` and `examples/block_hooks.py` demonstrating all action helpers and hook styles
- Block actions test suite: 70 unit tests, 30 compilation tests, and 4 Gradle build tests covering all action helpers and hook combinations
- Block actions documentation guide (`docs/guides/block-actions.rst`) with full action reference
- **Mining Configuration**: Full block mining support wrapping Fabric natively
  - `hardness` / `resistance` — control break time and blast durability
  - `tool_type` — tag blocks as mineable by a specific tool (`"pickaxe"`, `"axe"`, `"shovel"`, `"hoe"`, `"sword"`)
  - `mining_level` — minimum tool tier for drops (`"stone"`, `"iron"`, `"diamond"`)
  - `requires_tool` — whether correct tool must be used for the block to drop items (auto-inferred from `tool_type`)
  - `mining_speeds` — per-tool speed overrides via a generated `CustomMiningBlock` Java class that overrides `getDestroyProgress()`
  - Automatic generation of Minecraft block tags (`mineable/<tool>.json`, `needs_<level>_tool.json`)
- `VALID_TOOL_TYPES` and `VALID_MINING_LEVELS` constants exported from `fabricpy`
- Example script `examples/mining_blocks.py` demonstrating all mining configurations
- Comprehensive E2E test suite (`tests/test_e2e.py`) with 52 tests:
  - 27 compile-only tests validating project structure, Java correctness, mining tags, and edge cases
  - 15 real Gradle build tests (`./gradlew build`) covering every feature combination
  - 9 mocked client-run tests for `build()` / `run()` workflows
  - 1 `runClient --dry-run` test verifying the full task graph resolves
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
- Block class now supports event hook parameters (`left_click_event`, `right_click_event`, `break_event`) and overridable methods (`on_left_click`, `on_right_click`, `on_break`)
- Updated Block class to accept optional `loot_table` parameter
- `ModConfig.compile()` now writes loot table JSON files to `data/<mod_id>/loot_table/`
- `ModConfig.compile()` now generates Fabric event callback registrations for block hooks

### Fixed
- Generated `ItemRegistrationTest.java` no longer produces duplicate `foodComponent` variable declarations when multiple food items are registered
- Generated `RecipeValidationTest.java` now uses `RecipeType.CRAFTING` (correct Minecraft 1.21 Yarn mapping) instead of invalid `RecipeType.CRAFTING_SHAPED`

### Documentation
- Added Block Actions guide (`docs/guides/block-actions.rst`) with full action reference and examples for all 16 action helpers
- Added example scripts for block hooks (declarative + subclass styles) and block actions (all helpers)
- Added Mining Configuration section to Creating Blocks guide with hardness/resistance, tool types, mining levels, and per-tool speed examples
- Updated full mod example with mining-configured ore blocks
- Updated README with mining tools & speeds section and examples table entry
- Updated quickstart guide with mining ore block example
- New "Loot Tables" guide in docs with complete API walkthrough
- Updated Block guide with loot table examples for ores and storage blocks
- Updated quickstart guide with loot table usage
- Updated README with loot table feature and examples
- Added `fabricpy.loottable`, `fabricpy.actions`, `fabricpy.message`, and `fabricpy.toolitem` modules to API reference

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
