"""
Unit tests for the ItemGroup class.
"""

import unittest
from fabricpy.itemgroup import ItemGroup
from fabricpy.item import Item


class TestItemGroup(unittest.TestCase):
    """Test the ItemGroup class."""

    def test_item_group_creation_basic(self):
        """Test creating a basic item group."""
        group = ItemGroup(id="test_group", name="Test Group")
        
        self.assertEqual(group.id, "test_group")
        self.assertEqual(group.name, "Test Group")
        self.assertIsNone(group._icon_cls)

    def test_item_group_with_icon_class(self):
        """Test creating an item group with an icon class."""
        # Create a mock item class
        class MockItem:
            id = "testmod:icon_item"
        
        group = ItemGroup(id="icon_group", name="Icon Group", icon=MockItem)
        
        self.assertEqual(group.id, "icon_group")
        self.assertEqual(group.name, "Icon Group")
        self.assertEqual(group._icon_cls, MockItem)

    def test_item_group_set_icon_with_class(self):
        """Test setting an icon using a class."""
        class MockItem:
            id = "testmod:test_icon"
        
        group = ItemGroup(id="test_group", name="Test Group")
        group.set_icon(MockItem)
        
        self.assertEqual(group._icon_cls, MockItem)

    def test_item_group_set_icon_with_instance(self):
        """Test setting an icon using an instance."""
        class MockItem:
            def __init__(self):
                self.id = "testmod:instance_icon"
        
        mock_instance = MockItem()
        
        group = ItemGroup(id="test_group", name="Test Group")
        group.set_icon(mock_instance)
        
        self.assertEqual(group._icon_cls, mock_instance)

    def test_item_group_icon_item_id_with_class(self):
        """Test getting icon item ID from a class."""
        class MockItem:
            id = "testmod:class_icon"
        
        group = ItemGroup(id="test_group", name="Test Group", icon=MockItem)
        
        self.assertEqual(group.icon_item_id, "testmod:class_icon")

    def test_item_group_icon_item_id_with_instance(self):
        """Test getting icon item ID from an instance."""
        class MockItem:
            def __init__(self):
                self.id = "testmod:instance_icon"
        
        mock_instance = MockItem()
        group = ItemGroup(id="test_group", name="Test Group")
        group.set_icon(mock_instance)
        
        self.assertEqual(group.icon_item_id, "testmod:instance_icon")

    def test_item_group_icon_item_id_none(self):
        """Test getting icon item ID when no icon is set."""
        group = ItemGroup(id="test_group", name="Test Group")
        
        self.assertIsNone(group.icon_item_id)

    def test_item_group_icon_item_id_no_id_attribute(self):
        """Test getting icon item ID when icon has no 'id' attribute."""
        class MockItemNoId:
            name = "No ID Item"
        
        group = ItemGroup(id="test_group", name="Test Group", icon=MockItemNoId)
        
        self.assertIsNone(group.icon_item_id)

    def test_item_group_equality(self):
        """Test item group equality comparison."""
        group1 = ItemGroup(id="same_id", name="Group 1")
        group2 = ItemGroup(id="same_id", name="Group 2")  # Different name, same ID
        group3 = ItemGroup(id="different_id", name="Group 3")
        
        # Groups with same ID should be equal
        self.assertEqual(group1, group2)
        
        # Groups with different IDs should not be equal
        self.assertNotEqual(group1, group3)
        
        # Group should not equal non-ItemGroup objects
        self.assertNotEqual(group1, "same_id")
        self.assertNotEqual(group1, 123)

    def test_item_group_hash(self):
        """Test item group hashing."""
        group1 = ItemGroup(id="hashable", name="Group 1")
        group2 = ItemGroup(id="hashable", name="Group 2")  # Same ID, different name
        group3 = ItemGroup(id="different", name="Group 3")
        
        # Groups with same ID should have same hash
        self.assertEqual(hash(group1), hash(group2))
        
        # Groups with different IDs should have different hashes
        self.assertNotEqual(hash(group1), hash(group3))
        
        # Should be usable as dict keys
        group_dict = {group1: "value1", group3: "value3"}
        self.assertEqual(group_dict[group2], "value1")  # group2 == group1

    def test_item_group_as_dict_key(self):
        """Test using ItemGroup objects as dictionary keys."""
        group1 = ItemGroup(id="key1", name="Key Group 1")
        group2 = ItemGroup(id="key2", name="Key Group 2")
        group3 = ItemGroup(id="key1", name="Different Name")  # Same ID as group1
        
        # Create dict with ItemGroup keys
        group_dict = {
            group1: "value1",
            group2: "value2"
        }
        
        # Should be able to access with equivalent groups
        self.assertEqual(group_dict[group3], "value1")  # group3 == group1
        self.assertEqual(group_dict[group2], "value2")
        
        # Should have 2 keys
        self.assertEqual(len(group_dict), 2)

    def test_item_group_complex_names(self):
        """Test item groups with complex names and IDs."""
        # Test with special characters in names
        group1 = ItemGroup(
            id="special_chars",
            name="Group with Special Characters: @#$%^&*()"
        )
        self.assertEqual(group1.name, "Group with Special Characters: @#$%^&*()")
        
        # Test with very long names
        long_name = "Very " * 50 + "Long Group Name"
        group2 = ItemGroup(id="long_name", name=long_name)
        self.assertEqual(group2.name, long_name)
        
        # Test with underscores and numbers in ID
        group3 = ItemGroup(id="test_group_123", name="Test Group 123")
        self.assertEqual(group3.id, "test_group_123")

    def test_item_group_with_real_item(self):
        """Test item group with actual Item instance as icon."""
        # Create a real Item instance
        icon_item = Item(
            id="testmod:group_icon",
            name="Group Icon Item"
        )
        
        group = ItemGroup(id="real_item_group", name="Real Item Group")
        group.set_icon(icon_item)
        
        self.assertEqual(group.icon_item_id, "testmod:group_icon")
        self.assertEqual(group._icon_cls, icon_item)


if __name__ == '__main__':
    unittest.main()
