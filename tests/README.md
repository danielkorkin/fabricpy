# FabricPy Test Suite

This directory contains comprehensive unit tests for the fabricpy library, ensuring all features work correctly and reliably.

## Test Structure

The test suite is organized into the following modules:

### Core Component Tests
- **`test_items.py`** - Tests for the `Item` and `FoodItem` classes
- **`test_blocks.py`** - Tests for the `Block` class
- **`test_recipe.py`** - Tests for the `RecipeJson` class
- **`test_itemgroup.py`** - Tests for the `ItemGroup` class
- **`test_item_group_constants.py`** - Tests for vanilla item group constants
- **`test_modconfig.py`** - Tests for the `ModConfig` class (compilation system)

### Integration Tests
- **`test_integration.py`** - Comprehensive integration tests that test all components working together

## Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test Module
```bash
python tests/run_tests.py items        # Run item tests
python tests/run_tests.py blocks       # Run block tests
python tests/run_tests.py recipe       # Run recipe tests
python tests/run_tests.py itemgroup    # Run item group tests
python tests/run_tests.py modconfig    # Run mod config tests
python tests/run_tests.py integration  # Run integration tests
```

### Run Individual Test Classes
```bash
python -m unittest tests.test_items.TestItem
python -m unittest tests.test_items.TestFoodItem
python -m unittest tests.test_blocks.TestBlock
# etc.
```

### Run Specific Test Methods
```bash
python -m unittest tests.test_items.TestItem.test_item_creation_basic
python -m unittest tests.test_modconfig.TestModConfig.test_register_item
# etc.
```

## Test Coverage

The test suite covers all major features of fabricpy:

### Item System
- ✅ Basic item creation with various parameters
- ✅ Item ID namespacing (with and without mod prefix)
- ✅ Custom and vanilla item groups
- ✅ Recipe attachment to items
- ✅ Edge cases and validation

### Food Item System
- ✅ Food-specific properties (nutrition, saturation, always_edible)
- ✅ Inheritance from Item class
- ✅ Food items with recipes
- ✅ Various nutrition values and combinations

### Block System
- ✅ Basic block creation with various parameters
- ✅ Block and inventory texture handling (with fallback)
- ✅ Block recipes and item groups
- ✅ Block registration and management

### Recipe System
- ✅ Recipe creation from JSON strings and dictionaries
- ✅ Recipe validation (type field requirement)
- ✅ Result ID extraction (both 'id' and 'item' fields)
- ✅ Various recipe types (shaped, shapeless, smelting)
- ✅ Complex recipes with multiple ingredients

### Item Group System
- ✅ Custom ItemGroup creation and management
- ✅ Icon setting (classes and instances)
- ✅ Group equality and hashing (for use as dict keys)
- ✅ Vanilla item group constants
- ✅ Icon item ID extraction

### Mod Configuration System
- ✅ ModConfig creation with various parameters
- ✅ Item, food item, and block registration
- ✅ Custom item group detection
- ✅ Java constant name conversion
- ✅ Recipe file writing
- ✅ Metadata management
- ✅ Build and run system integration

### Integration Tests
- ✅ Complete mod creation workflow
- ✅ Recipe system integration
- ✅ Item group system integration
- ✅ Edge cases and error handling
- ✅ Module import verification

## Test Design Principles

The tests follow these principles:

1. **Comprehensive Coverage** - All public methods and features are tested
2. **Edge Case Testing** - Boundary conditions and error cases are covered
3. **Integration Testing** - Components are tested together to ensure proper interaction
4. **Isolation** - Tests use temporary directories and don't affect system state
5. **Mocking** - External dependencies (like git commands) are mocked appropriately
6. **Clear Assertions** - Tests have descriptive names and clear failure messages

## Test Categories

### Unit Tests
Test individual components in isolation:
- Item creation and properties
- Recipe parsing and validation
- ItemGroup functionality
- Java constant conversion

### Integration Tests
Test components working together:
- Complete mod setup workflows
- Recipe system with items and blocks
- Item group system with multiple groups
- Import system verification

### Edge Case Tests
Test boundary conditions and error handling:
- Invalid recipe formats
- Missing file scenarios
- Extreme parameter values
- Special character handling

## Adding New Tests

When adding new features to fabricpy, please add corresponding tests:

1. Create test methods in the appropriate test file
2. Follow the naming convention: `test_feature_description`
3. Include both positive and negative test cases
4. Add integration tests if the feature interacts with other components
5. Update this README if adding new test files

## Mock Strategy

The tests use Python's `unittest.mock` to mock external dependencies:

- **File System Operations** - Use temporary directories for isolation
- **Subprocess Calls** - Mock `subprocess.check_call` for git and gradle commands
- **External Files** - Create temporary files for testing file operations

## Error Handling Tests

The test suite includes comprehensive error handling tests:

- Missing required parameters
- Invalid recipe formats
- File system errors
- Build system failures
- Import errors

## Performance Considerations

The tests are designed to run quickly:

- Use temporary directories that are cleaned up automatically
- Mock expensive operations (git clone, gradle build)
- Focus on logic testing rather than actual file compilation
- Parallel test execution is supported

## Continuous Integration

The test suite is designed to work well with CI systems:

- No external dependencies beyond Python standard library
- Clean temporary file handling
- Proper exit codes for success/failure
- Detailed error reporting
- Optional coverage reporting support

## Test Data

The tests use realistic test data that mirrors actual Minecraft mod development:

- Valid Minecraft item/block IDs
- Realistic recipe patterns
- Appropriate nutrition values for food
- Standard item group configurations
- Common mod development scenarios
