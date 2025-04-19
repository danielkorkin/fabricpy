# fabricpy/itemgroup.py
"""
Python representation of a custom Fabric ItemGroup (creative tab).

Example
-------
>>> grp = ItemGroup(id="new_foods", name="New Foods")
>>> grp.set_icon(MyFoodItem)
>>> item.item_group = grp
"""

from __future__ import annotations
from typing import Type, Optional


class ItemGroup:
    def __init__(self, id: str, name: str, icon: Optional[Type] = None):
        """
        Parameters
        ----------
        id   : registry path, e.g. "new_foods"
        name : player‑visible title (used for language key)
        icon : class *or* instance of an item whose ItemStack is the tab icon
               (can be supplied later via `set_icon`)
        """
        self.id = id
        self.name = name
        self._icon_cls = icon  # type: ignore[attr-defined]

    # ------------------------------------------------------------------ #
    # public helpers                                                     #
    # ------------------------------------------------------------------ #

    def set_icon(self, item_cls_or_instance):
        """Define the item whose ItemStack will be displayed as the tab icon."""
        self._icon_cls = (
            item_cls_or_instance
            if not isinstance(item_cls_or_instance, type)
            else item_cls_or_instance
        )

    # attributes used by ModConfig code‑generator ---------------------- #

    @property
    def icon_item_id(self) -> str | None:
        """Returns the *registry id* of the icon item class, or None."""
        if hasattr(self._icon_cls, "id"):
            return getattr(self._icon_cls, "id")
        return None

    # comparison helpers so we can use ItemGroup objects as dict keys
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, ItemGroup) and other.id == self.id
