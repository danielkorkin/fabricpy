"""Custom creative tab (ItemGroup) creation for Fabric mods.

This module provides the ItemGroup class for creating custom creative tabs
in Minecraft. Custom ItemGroups allow you to organize your mod's items and
blocks into their own dedicated creative inventory tabs.

Example:
    Creating a custom creative tab::

        import fabricpy

        # Create a custom creative tab
        grp = fabricpy.ItemGroup(id="new_foods", name="New Foods")
        grp.set_icon(MyFoodItem)

        # Assign items to the custom tab
        item = fabricpy.Item(
            id="mymod:special_apple",
            name="Special Apple",
            item_group=grp
        )
"""

from __future__ import annotations

from typing import Optional, Type


class ItemGroup:
    """Represents a custom creative tab (ItemGroup) in a Fabric mod.

    ItemGroups are the tabs shown in the creative inventory that organize items
    and blocks by category. This class allows creation of custom tabs for mod content.

    Args:
        item_id: The registry identifier for the ItemGroup (e.g., "new_foods").
            This should be unique and follow mod naming conventions.
        name: The display name shown to players in the creative inventory.
            This is used as the language key for localization.
        icon: The item class or instance whose ItemStack will be displayed
            as the tab icon. Can be set later using set_icon().

    Attributes:
        item_id (str): The unique registry identifier for this ItemGroup.
        name (str): The display name/language key for this ItemGroup.
        icon (Optional[Type]): The item class used as the tab icon.

    Example:
        Creating a food-themed creative tab::

            # Create the ItemGroup
            food_group = ItemGroup(
                item_id="my_mod_foods",
                name="My Mod Foods"
            )

            # Set an icon (using an existing item class)
            food_group.set_icon(AppleItem)

            # Use in item definitions
            golden_apple = Item(
                id="mymod:golden_apple",
                name="Golden Apple",
                item_group=food_group
            )
    """

    def __init__(
        self,
        item_id: str = None,
        name: str = None,
        icon: Optional[Type] = None,
        id: str = None,
    ):
        """Initialize a new ItemGroup.

        Args:
            item_id: The registry identifier for the ItemGroup. Should be unique
                and follow standard mod naming conventions (lowercase, underscores).
                Can also be passed as 'id' for convenience.
            name: The display name shown in the creative inventory. This will be
                used as a language key for localization.
            icon: Optional item class to use as the tab icon. Can be set later
                using set_icon().
            id: Alias for item_id. Use either 'id' or 'item_id', not both.

        Raises:
            ValueError: If both id and item_id are provided.

        Example:
            Basic ItemGroup creation::

                tools_group = ItemGroup(item_id="my_tools", name="My Tools")
                # or equivalently:
                tools_group = ItemGroup(id="my_tools", name="My Tools")

            With initial icon::

                weapons_group = ItemGroup(
                    id="my_weapons",
                    name="My Weapons",
                    icon=MySwordItem
                )

        Note:
            While None values are technically allowed for error handling scenarios,
            proper usage requires both an ID and name for the ItemGroup to function
            correctly in mod compilation.
        """
        # Handle id/item_id parameter flexibility
        if id is not None and item_id is not None:
            raise ValueError(
                "Cannot specify both 'id' and 'item_id' parameters. Use one or the other."
            )

        if id is not None:
            self.item_id = id
        elif item_id is not None:
            self.item_id = item_id
        else:
            self.item_id = None  # Allow None for error handling tests

        self.name = name  # Allow None for error handling tests
        self.icon = icon
        self._icon_cls = icon  # Store icon in _icon_cls attribute as expected by tests

    @property
    def id(self) -> str:
        """Get the ItemGroup's ID.

        Returns:
            str: The registry identifier for this ItemGroup.

        Note:
            This is an alias for item_id to maintain compatibility with tests
            and existing code that expects an 'id' property.
        """
        return self.item_id

    @property
    def icon_item_id(self) -> str | None:
        """Get the item ID of the icon used for this ItemGroup.

        Extracts the item ID from the icon object, handling both class
        attributes and instance attributes.

        Returns:
            str | None: The item ID of the icon, or None if no icon is set
                or the icon has no ID attribute.

        Example:
            Getting the icon item ID::

                group = ItemGroup(id="weapons", name="Weapons")
                group.set_icon(MySwordItem)  # MySwordItem.id = "mymod:sword"
                print(group.icon_item_id)    # "mymod:sword"
        """
        if self._icon_cls is None:
            return None

        # Try to get ID from class or instance
        if hasattr(self._icon_cls, "id"):
            return getattr(self._icon_cls, "id")
        return None

    def set_icon(self, icon: Type) -> None:
        """Set the icon item for this ItemGroup.

        The icon appears on the creative inventory tab and should represent
        the category of items contained within the group.

        Args:
            icon: The item class whose ItemStack will be displayed as the tab icon.
                This should be a class that extends Item, FoodItem, or Block.

        Example:
            Setting a custom icon::

                magic_group = ItemGroup("magic_items", "Magic Items")
                magic_group.set_icon(MagicWandItem)

        Note:
            The icon item should be registered before the ItemGroup is used
            in mod compilation to ensure proper icon rendering.
        """
        self.icon = icon
        self._icon_cls = icon  # Store in _icon_cls as expected by tests

    def __eq__(self, other: object) -> bool:
        """Check equality with another ItemGroup.

        Two ItemGroups are considered equal if they have the same ID,
        regardless of their name or icon.

        Args:
            other: The object to compare with.

        Returns:
            bool: True if both objects are ItemGroups with the same ID.

        Example:
            Comparing ItemGroups::

                group1 = ItemGroup(id="weapons", name="Weapons")
                group2 = ItemGroup(id="weapons", name="Combat Items")
                print(group1 == group2)  # True (same ID)
        """
        if not isinstance(other, ItemGroup):
            return False
        return self.item_id == other.item_id

    def __hash__(self) -> int:
        """Generate a hash value for this ItemGroup.

        The hash is based on the ItemGroup's ID, ensuring that ItemGroups
        with the same ID have the same hash value.

        Returns:
            int: Hash value based on the item_id.

        Note:
            This allows ItemGroups to be used as dictionary keys and in sets.
        """
        return hash(self.item_id)
