# fabricpy/loottable.py
"""Loot table definition and generation for Fabric mods.

This module provides the :class:`LootTable` class for defining loot tables that
control what items are dropped when blocks are broken, entities are killed,
or chests are opened in Minecraft.  It supports both raw JSON input and
convenient builder-style class methods for common patterns such as blocks
that drop themselves, silk-touch-only drops, and fortune-affected ore drops.

Loot table JSON files follow the Minecraft data-pack format and are written
to ``data/<mod_id>/loot_table/<category>/<name>.json`` during compilation.

Tested against **Minecraft 1.21+ / Fabric-API 0.141.3**.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence, Union


# ── condition / function / entry helpers ──────────────────────────────── #


def _survives_explosion() -> Dict[str, str]:
    """Return the ``minecraft:survives_explosion`` condition."""
    return {"condition": "minecraft:survives_explosion"}


def _silk_touch_condition() -> Dict[str, Any]:
    """Return a condition requiring Silk Touch on the tool."""
    return {
        "condition": "minecraft:match_tool",
        "predicate": {
            "predicates": {
                "minecraft:enchantments": [
                    {
                        "enchantments": "minecraft:silk_touch",
                        "levels": {"min": 1},
                    }
                ]
            }
        },
    }


def _inverted_condition(condition: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap *condition* in ``minecraft:inverted``."""
    return {
        "condition": "minecraft:inverted",
        "term": condition,
    }


def _set_count_function(min_count: int, max_count: int) -> Dict[str, Any]:
    """Return a ``minecraft:set_count`` function with a uniform range."""
    return {
        "function": "minecraft:set_count",
        "count": {
            "type": "minecraft:uniform",
            "min": min_count,
            "max": max_count,
        },
    }


def _apply_ore_bonus_function(enchantment: str = "minecraft:fortune") -> Dict[str, Any]:
    """Return an ``minecraft:apply_bonus`` function for ore-style fortune."""
    return {
        "function": "minecraft:apply_bonus",
        "enchantment": enchantment,
        "formula": "minecraft:ore_drops",
    }


def _explosion_decay_function() -> Dict[str, str]:
    """Return the ``minecraft:explosion_decay`` function."""
    return {"function": "minecraft:explosion_decay"}


def _item_entry(
    item_id: str,
    *,
    weight: int | None = None,
    quality: int | None = None,
    conditions: List[Dict[str, Any]] | None = None,
    functions: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Build a ``minecraft:item`` loot-table entry."""
    entry: Dict[str, Any] = {
        "type": "minecraft:item",
        "name": item_id,
    }
    if weight is not None:
        entry["weight"] = weight
    if quality is not None:
        entry["quality"] = quality
    if conditions:
        entry["conditions"] = conditions
    if functions:
        entry["functions"] = functions
    return entry


# ── pool builder ──────────────────────────────────────────────────────── #


class LootPool:
    """Fluent builder for a single loot-table pool.

    A pool specifies a set of entries, how many rolls to make, and optional
    conditions or functions applied to the whole pool.

    Example:
        Building a pool manually::

            pool = (
                LootPool()
                .rolls(1)
                .entry("mymod:ruby", weight=3)
                .entry("mymod:sapphire", weight=1)
                .condition({"condition": "minecraft:survives_explosion"})
                .build()
            )
    """

    def __init__(self) -> None:
        self._rolls: int | Dict[str, Any] = 1
        self._bonus_rolls: int | Dict[str, Any] = 0
        self._entries: List[Dict[str, Any]] = []
        self._conditions: List[Dict[str, Any]] = []
        self._functions: List[Dict[str, Any]] = []

    # ── setters (return self for chaining) ─────────────────────────── #

    def rolls(self, value: int | Dict[str, Any]) -> "LootPool":
        """Set the number of rolls for this pool.

        Args:
            value: A fixed integer or a number-provider dict (e.g.
                ``{"type": "minecraft:uniform", "min": 1, "max": 3}``).
        """
        self._rolls = value
        return self

    def bonus_rolls(self, value: int | Dict[str, Any]) -> "LootPool":
        """Set bonus rolls granted by luck.

        Args:
            value: A fixed integer or a number-provider dict.
        """
        self._bonus_rolls = value
        return self

    def entry(
        self,
        item_id: str,
        *,
        weight: int | None = None,
        quality: int | None = None,
        conditions: List[Dict[str, Any]] | None = None,
        functions: List[Dict[str, Any]] | None = None,
    ) -> "LootPool":
        """Add an ``minecraft:item`` entry to this pool.

        Args:
            item_id: Registry identifier of the item (e.g. ``"mymod:ruby"``).
            weight: Relative weight for random selection among entries.
            quality: Luck-based weight modifier.
            conditions: Entry-level conditions.
            functions: Entry-level item-modifier functions.
        """
        self._entries.append(
            _item_entry(
                item_id,
                weight=weight,
                quality=quality,
                conditions=conditions,
                functions=functions,
            )
        )
        return self

    def raw_entry(self, entry: Dict[str, Any]) -> "LootPool":
        """Add any pre-built entry dict (for ``minecraft:alternatives``, etc.)."""
        self._entries.append(entry)
        return self

    def condition(self, cond: Dict[str, Any]) -> "LootPool":
        """Add a pool-level condition."""
        self._conditions.append(cond)
        return self

    def function(self, func: Dict[str, Any]) -> "LootPool":
        """Add a pool-level item-modifier function."""
        self._functions.append(func)
        return self

    # ── build ──────────────────────────────────────────────────────── #

    def build(self) -> Dict[str, Any]:
        """Serialize this pool to a JSON-compatible dict."""
        pool: Dict[str, Any] = {
            "rolls": self._rolls,
        }
        if self._bonus_rolls:
            pool["bonus_rolls"] = self._bonus_rolls
        if self._entries:
            pool["entries"] = list(self._entries)
        if self._conditions:
            pool["conditions"] = list(self._conditions)
        if self._functions:
            pool["functions"] = list(self._functions)
        return pool


# ── main LootTable class ─────────────────────────────────────────────── #


class LootTable:
    """Wrapper for Minecraft loot-table JSON data.

    A ``LootTable`` holds a validated dictionary representation of a
    Minecraft loot table.  It can be created from raw JSON, a plain dict,
    or via convenient class-method builders for common patterns.

    The finished object is attached to a :class:`~fabricpy.block.Block`
    (via its ``loot_table`` attribute) or registered directly with
    :class:`~fabricpy.modconfig.ModConfig` for entity / chest loot tables.
    During :meth:`~fabricpy.modconfig.ModConfig.compile` the JSON file
    is written to the appropriate ``data/<mod_id>/loot_table/`` directory.

    Args:
        src: Loot-table data as a JSON string, a dictionary, or a list of
            ``LootPool`` builder objects.  When pools are passed the
            ``loot_type`` keyword is required.
        loot_type: The ``"type"`` field value (e.g. ``"minecraft:block"``,
            ``"minecraft:entity"``).  Required when *src* is a pool list;
            otherwise inferred from the dict/JSON.
        category: Sub-directory under ``loot_table/`` when written to disk
            (e.g. ``"blocks"``, ``"entities"``, ``"chests"``).
            Defaults to ``"blocks"``.

    Attributes:
        text (str): The JSON string representation of the loot table.
        data (dict[str, Any]): The parsed dictionary representation.
        category (str): Sub-directory for file output.

    Raises:
        ValueError: If the loot table is missing the ``"type"`` field.
        json.JSONDecodeError: If a string *src* is not valid JSON.

    Example:
        Creating a loot table from a dictionary::

            lt = LootTable({
                "type": "minecraft:block",
                "pools": [{
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item", "name": "mymod:my_block"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}]
                }]
            })

        Using a builder class method::

            lt = LootTable.drops_self("mymod:ruby_block")
    """

    # ── constructor ────────────────────────────────────────────────── #

    def __init__(
        self,
        src: str | Dict[str, Any] | List[LootPool],
        *,
        loot_type: str | None = None,
        category: str = "blocks",
    ) -> None:
        self.category = category

        if isinstance(src, list):
            # list of LootPool builders
            if loot_type is None:
                raise ValueError(
                    "loot_type is required when constructing a LootTable from pools"
                )
            self.data: Dict[str, Any] = {
                "type": loot_type,
                "pools": [p.build() if isinstance(p, LootPool) else p for p in src],
            }
            self.text: str = json.dumps(self.data, indent=2)
        elif isinstance(src, str):
            self.text = src.strip()
            self.data = json.loads(self.text)
        else:
            self.data = src
            self.text = json.dumps(src, indent=2)

        # validate presence of "type"
        if "type" not in self.data:
            raise ValueError("Loot table JSON must contain a 'type' field")

        lt = self.data["type"]
        if not isinstance(lt, str) or not lt.strip():
            raise ValueError("Loot table 'type' field must be a non-empty string")

    # ── convenience properties ─────────────────────────────────────── #

    @property
    def loot_type(self) -> str:
        """The ``type`` field of the loot table (e.g. ``"minecraft:block"``)."""
        return self.data["type"]

    @property
    def pools(self) -> List[Dict[str, Any]]:
        """Return the list of pool dicts."""
        return self.data.get("pools", [])

    # ── class-method builders ─────────────────────────────────────── #

    @classmethod
    def drops_self(cls, block_id: str) -> "LootTable":
        """Create a loot table where the block drops itself.

        This is the most common loot table pattern — the block simply drops
        one of itself when broken, subject to explosion protection.

        Args:
            block_id: Registry identifier of the block (e.g. ``"mymod:ruby_block"``).

        Returns:
            LootTable: A loot table configured for self-drops.

        Example:
            ::

                lt = LootTable.drops_self("mymod:ruby_block")
                block = Block(
                    id="mymod:ruby_block",
                    name="Ruby Block",
                    loot_table=lt,
                )
        """
        return cls(
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "rolls": 1,
                        "entries": [_item_entry(block_id)],
                        "conditions": [_survives_explosion()],
                    }
                ],
            },
            category="blocks",
        )

    @classmethod
    def drops_item(
        cls,
        block_id: str,
        item_id: str,
        count: int = 1,
        *,
        min_count: int | None = None,
        max_count: int | None = None,
    ) -> "LootTable":
        """Create a loot table where the block drops a specific item.

        Args:
            block_id: Registry identifier of the block being broken.
            item_id: The item to drop.
            count: Fixed number to drop (used when *min_count* / *max_count*
                are not provided).
            min_count: Minimum items dropped (uniform distribution).
            max_count: Maximum items dropped (uniform distribution).

        Returns:
            LootTable: A configured loot table.

        Example:
            ::

                lt = LootTable.drops_item(
                    "mymod:ruby_ore", "mymod:ruby", min_count=1, max_count=3,
                )
        """
        functions: List[Dict[str, Any]] = []
        if min_count is not None and max_count is not None:
            functions.append(_set_count_function(min_count, max_count))
        elif count != 1:
            functions.append(
                {
                    "function": "minecraft:set_count",
                    "count": count,
                }
            )
        functions.append(_explosion_decay_function())

        return cls(
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "rolls": 1,
                        "entries": [
                            _item_entry(
                                item_id, functions=functions if functions else None
                            ),
                        ],
                        "conditions": [_survives_explosion()],
                    }
                ],
            },
            category="blocks",
        )

    @classmethod
    def drops_nothing(cls) -> "LootTable":
        """Create an empty loot table (the block drops nothing).

        Returns:
            LootTable: A loot table with no pools.

        Example:
            ::

                lt = LootTable.drops_nothing()
        """
        return cls({"type": "minecraft:block", "pools": []}, category="blocks")

    @classmethod
    def drops_with_silk_touch(
        cls,
        block_id: str,
        silk_touch_item: str | None = None,
        *,
        no_silk_touch_item: str | None = None,
        no_silk_touch_count: int = 1,
    ) -> "LootTable":
        """Create a loot table with silk-touch behaviour.

        When mined **with** Silk Touch the *silk_touch_item* is dropped
        (defaults to *block_id*).  When mined **without** Silk Touch,
        *no_silk_touch_item* is dropped if provided, otherwise nothing.

        Args:
            block_id: Registry identifier of the block.
            silk_touch_item: Item dropped with Silk Touch.  Defaults to *block_id*.
            no_silk_touch_item: Item dropped without Silk Touch, or ``None``
                to drop nothing.
            no_silk_touch_count: How many of the no-silk-touch item to drop.

        Returns:
            LootTable: A configured loot table.

        Example:
            Glass-style — drops itself with silk touch, nothing otherwise::

                lt = LootTable.drops_with_silk_touch("mymod:crystal_glass")

            Ore-style — silk touch gives ore block, otherwise raw material::

                lt = LootTable.drops_with_silk_touch(
                    "mymod:ruby_ore",
                    no_silk_touch_item="mymod:ruby",
                    no_silk_touch_count=1,
                )
        """
        silk_item = silk_touch_item or block_id

        entries: List[Dict[str, Any]] = [
            _item_entry(silk_item, conditions=[_silk_touch_condition()]),
        ]
        if no_silk_touch_item:
            no_st_funcs: List[Dict[str, Any]] = []
            if no_silk_touch_count != 1:
                no_st_funcs.append(
                    {
                        "function": "minecraft:set_count",
                        "count": no_silk_touch_count,
                    }
                )
            no_st_funcs.append(_explosion_decay_function())
            entries.append(
                _item_entry(
                    no_silk_touch_item,
                    conditions=[_inverted_condition(_silk_touch_condition())],
                    functions=no_st_funcs if no_st_funcs else None,
                )
            )

        return cls(
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "rolls": 1,
                        "entries": [
                            {
                                "type": "minecraft:alternatives",
                                "children": entries,
                            }
                        ],
                    }
                ],
            },
            category="blocks",
        )

    @classmethod
    def drops_with_fortune(
        cls,
        block_id: str,
        item_id: str,
        *,
        min_count: int = 1,
        max_count: int = 1,
        silk_touch_drops_self: bool = True,
    ) -> "LootTable":
        """Create a fortune-affected loot table (ore-style drops).

        Mimics vanilla ore behaviour: without Silk Touch the block drops
        *item_id* with fortune scaling; with Silk Touch the block drops
        itself (if *silk_touch_drops_self* is ``True``).

        Args:
            block_id: Registry identifier of the block.
            item_id: Item dropped without Silk Touch (e.g. ``"mymod:ruby"``).
            min_count: Minimum base drop count.
            max_count: Maximum base drop count.
            silk_touch_drops_self: Whether Silk Touch drops the block itself.

        Returns:
            LootTable: A configured loot table.

        Example:
            ::

                lt = LootTable.drops_with_fortune(
                    "mymod:ruby_ore",
                    "mymod:ruby",
                    min_count=1,
                    max_count=2,
                )
        """
        item_funcs: List[Dict[str, Any]] = []
        if min_count != 1 or max_count != 1:
            item_funcs.append(_set_count_function(min_count, max_count))
        item_funcs.append(_apply_ore_bonus_function())
        item_funcs.append(_explosion_decay_function())

        no_silk_entry = _item_entry(
            item_id,
            conditions=[_inverted_condition(_silk_touch_condition())],
            functions=item_funcs,
        )

        children: List[Dict[str, Any]] = []
        if silk_touch_drops_self:
            children.append(_item_entry(block_id, conditions=[_silk_touch_condition()]))
        children.append(no_silk_entry)

        return cls(
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "rolls": 1,
                        "entries": [
                            {
                                "type": "minecraft:alternatives",
                                "children": children,
                            }
                        ],
                    }
                ],
            },
            category="blocks",
        )

    @classmethod
    def entity(
        cls,
        pools: List[LootPool | Dict[str, Any]],
    ) -> "LootTable":
        """Create an entity loot table from a list of pools.

        Args:
            pools: List of :class:`LootPool` builders or raw pool dicts.

        Returns:
            LootTable: A loot table with ``type`` set to ``minecraft:entity``.

        Example:
            ::

                lt = LootTable.entity([
                    LootPool()
                        .rolls(1)
                        .entry("mymod:monster_fang", weight=1)
                        .condition({"condition": "minecraft:survives_explosion"})
                ])
        """
        built = [p.build() if isinstance(p, LootPool) else p for p in pools]
        return cls(
            {"type": "minecraft:entity", "pools": built},
            category="entities",
        )

    @classmethod
    def chest(
        cls,
        pools: List[LootPool | Dict[str, Any]],
    ) -> "LootTable":
        """Create a chest loot table from a list of pools.

        Args:
            pools: List of :class:`LootPool` builders or raw pool dicts.

        Returns:
            LootTable: A loot table with ``type`` set to ``minecraft:chest``.

        Example:
            ::

                lt = LootTable.chest([
                    LootPool()
                        .rolls({"type": "minecraft:uniform", "min": 2, "max": 4})
                        .entry("mymod:golden_key", weight=5)
                        .entry("minecraft:diamond", weight=1)
                ])
        """
        built = [p.build() if isinstance(p, LootPool) else p for p in pools]
        return cls(
            {"type": "minecraft:chest", "pools": built},
            category="chests",
        )

    @classmethod
    def from_pools(
        cls,
        loot_type: str,
        pools: List[LootPool | Dict[str, Any]],
        *,
        category: str = "blocks",
    ) -> "LootTable":
        """Create a loot table from an arbitrary type and pool list.

        Args:
            loot_type: The ``"type"`` field (e.g. ``"minecraft:block"``).
            pools: List of pools (builder objects or dicts).
            category: Sub-directory for file output.

        Returns:
            LootTable: A fully configured loot table.
        """
        built = [p.build() if isinstance(p, LootPool) else p for p in pools]
        return cls(
            {"type": loot_type, "pools": built},
            category=category,
        )

    # ── representation ─────────────────────────────────────────────── #

    def __repr__(self) -> str:
        pool_count = len(self.pools)
        return (
            f"LootTable(type={self.loot_type!r}, "
            f"pools={pool_count}, category={self.category!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LootTable):
            return NotImplemented
        return self.data == other.data and self.category == other.category
