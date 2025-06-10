"""
Unit tests for the item_group module (vanilla item group constants).
"""

import unittest
from fabricpy import item_group


class TestItemGroupConstants(unittest.TestCase):
    """Test the vanilla item group constants."""

    def test_all_constants_exist(self):
        """Test that all expected vanilla item group constants exist."""
        expected_constants = [
            'BUILDING_BLOCKS',
            'NATURAL',
            'FUNCTIONAL',
            'REDSTONE',
            'TOOLS',
            'COMBAT',
            'FOOD_AND_DRINK',
            'INGREDIENTS',
            'SPAWN_EGGS'
        ]
        
        for constant in expected_constants:
            self.assertTrue(hasattr(item_group, constant),
                          f"Missing constant: {constant}")

    def test_constant_values(self):
        """Test that constants have the expected string values."""
        self.assertEqual(item_group.BUILDING_BLOCKS, "BUILDING_BLOCKS")
        self.assertEqual(item_group.NATURAL, "NATURAL")
        self.assertEqual(item_group.FUNCTIONAL, "FUNCTIONAL")
        self.assertEqual(item_group.REDSTONE, "REDSTONE")
        self.assertEqual(item_group.TOOLS, "TOOLS")
        self.assertEqual(item_group.COMBAT, "COMBAT")
        self.assertEqual(item_group.FOOD_AND_DRINK, "FOOD_AND_DRINK")
        self.assertEqual(item_group.INGREDIENTS, "INGREDIENTS")
        self.assertEqual(item_group.SPAWN_EGGS, "SPAWN_EGGS")

    def test_constants_are_strings(self):
        """Test that all constants are strings."""
        constants = [
            item_group.BUILDING_BLOCKS,
            item_group.NATURAL,
            item_group.FUNCTIONAL,
            item_group.REDSTONE,
            item_group.TOOLS,
            item_group.COMBAT,
            item_group.FOOD_AND_DRINK,
            item_group.INGREDIENTS,
            item_group.SPAWN_EGGS
        ]
        
        for constant in constants:
            self.assertIsInstance(constant, str,
                                f"Constant {constant} is not a string")

    def test_constants_are_uppercase(self):
        """Test that all constants follow UPPER_CASE naming convention."""
        constants = [
            item_group.BUILDING_BLOCKS,
            item_group.NATURAL,
            item_group.FUNCTIONAL,
            item_group.REDSTONE,
            item_group.TOOLS,
            item_group.COMBAT,
            item_group.FOOD_AND_DRINK,
            item_group.INGREDIENTS,
            item_group.SPAWN_EGGS
        ]
        
        for constant in constants:
            self.assertEqual(constant, constant.upper(),
                           f"Constant {constant} is not uppercase")

    def test_no_spaces_in_constants(self):
        """Test that constants don't contain spaces (use underscores instead)."""
        constants = [
            item_group.BUILDING_BLOCKS,
            item_group.NATURAL,
            item_group.FUNCTIONAL,
            item_group.REDSTONE,
            item_group.TOOLS,
            item_group.COMBAT,
            item_group.FOOD_AND_DRINK,
            item_group.INGREDIENTS,
            item_group.SPAWN_EGGS
        ]
        
        for constant in constants:
            self.assertNotIn(' ', constant,
                           f"Constant {constant} contains spaces")

    def test_constants_uniqueness(self):
        """Test that all constants have unique values."""
        constants = [
            item_group.BUILDING_BLOCKS,
            item_group.NATURAL,
            item_group.FUNCTIONAL,
            item_group.REDSTONE,
            item_group.TOOLS,
            item_group.COMBAT,
            item_group.FOOD_AND_DRINK,
            item_group.INGREDIENTS,
            item_group.SPAWN_EGGS
        ]
        
        unique_constants = set(constants)
        self.assertEqual(len(constants), len(unique_constants),
                        "Some constants have duplicate values")

    def test_module_docstring(self):
        """Test that the module has a proper docstring."""
        self.assertIsNotNone(item_group.__doc__)
        self.assertIn("creative", item_group.__doc__.lower())


if __name__ == '__main__':
    unittest.main()
