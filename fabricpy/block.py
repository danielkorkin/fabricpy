# fabricpy/block.py
"""Block registration and definition for Fabric mods.

This module provides the Block class for defining custom blocks in Minecraft Fabric mods.
Blocks can have custom textures for both the block itself and its inventory item representation,
recipes for crafting, creative tab assignment, and full mining configuration including
hardness, blast resistance, required tools, mining levels, and per-tool speed overrides.
"""

#: Valid tool types that can be used for ``tool_type`` and
#: ``mining_speeds`` keys.
VALID_TOOL_TYPES = {"pickaxe", "axe", "shovel", "hoe", "sword"}

#: Valid mining-level strings for ``mining_level``.
VALID_MINING_LEVELS = {"stone", "iron", "diamond"}


class Block:
    """Represents a custom block in a Fabric mod.

    The Block class handles the definition of custom blocks including their properties,
    textures, recipes, and creative tab assignment. Blocks automatically generate
    corresponding BlockItems for inventory representation.

    Mining behaviour is fully configurable through ``hardness``, ``resistance``,
    ``tool_type``, ``mining_level``, ``requires_tool``, and ``mining_speeds``.

    Args:
        id: The registry identifier for the block (e.g., "mymod:copper_block").
            If None, must be set before compilation.
        name: The display name for the block shown in-game.
            If None, must be set before compilation.
        max_stack_size: Maximum number of block items that can be stacked together.
            Defaults to 64.
        block_texture_path: Path to the block's texture file for world rendering
            relative to mod resources. If None, a default texture will be used.
        inventory_texture_path: Path to the texture used for the block's item form
            in inventories. If None, falls back to block_texture_path.
        recipe: Recipe definition for crafting this block. Can be a RecipeJson
            instance or None for no recipe.
        item_group: Creative tab to place this block's item in. Can be an ItemGroup
            instance, a string constant from item_group module, or None.
            Typically BUILDING_BLOCKS for most blocks.
        left_click_event: Java code to execute when the block is left clicked.
        right_click_event: Java code to execute when the block is right clicked.
        loot_table: Loot table definition controlling what the block drops when
            broken. Can be a LootTable instance or None (defaults to dropping
            itself).
        tool_type: The primary tool required to mine this block efficiently.
            One of ``"pickaxe"``, ``"axe"``, ``"shovel"``, ``"hoe"``,
            ``"sword"``, or ``None`` (no specific tool required).
            Defaults to ``None``.
        hardness: How long the block takes to mine.  Lower values break faster.
            Vanilla reference values: dirt = 0.5, stone = 1.5, obsidian = 50.
            Defaults to ``None`` (uses stone-equivalent 1.5).
        resistance: Blast resistance against explosions.
            Vanilla reference values: stone = 6.0, obsidian = 1200.
            Defaults to ``None`` (uses stone-equivalent 6.0).
        mining_level: Minimum tool tier needed to mine the block and obtain
            drops.  One of ``"stone"``, ``"iron"``, ``"diamond"``, or
            ``None`` (any tier works).  Requires ``requires_tool=True``
            (or ``tool_type`` set) to be effective.  Defaults to ``None``.
        requires_tool: Whether the correct tool must be used for the block
            to drop items.  When ``None`` the value is inferred: ``True``
            if ``tool_type`` is set, ``False`` otherwise.
        mining_speeds: A mapping of tool type strings (e.g. ``"pickaxe"``,
            ``"shovel"``) to custom mining-speed multipliers for this block.
            When provided, a custom block class is generated that overrides
            the per-tool break speed, enabling fine-grained control over
            how fast each tool type mines the block.  The block is also
            automatically added to the ``mineable/<tool>`` tags for every
            key in the dict.  Defaults to ``None``.

    Attributes:
        id (str): The registry identifier for the block.
        name (str): The display name for the block.
        max_stack_size (int): Maximum stack size for the block item.
        block_texture_path (str): Path to the block's world texture file.
        inventory_texture_path (str): Path to the block's inventory texture file.
        recipe (RecipeJson): Recipe definition for crafting this block.
        item_group (ItemGroup | str): Creative tab assignment for the block item.
        left_click_event (str | None): Java code executed on left click.
        right_click_event (str | None): Java code executed on right click.
        loot_table (LootTable | None): Loot table for block drops (defaults to dropping itself).
        hardness (float | None): Block hardness (mining time).
        resistance (float | None): Blast resistance.
        mining_level (str | None): Minimum tool tier for drops.
        requires_tool (bool): Whether correct tool is required for drops.
        mining_speeds (dict[str, float] | None): Per-tool speed overrides.

    Example:
        Creating a basic block::

            block = Block(
                id="mymod:copper_block",
                name="Copper Block",
                block_texture_path="textures/blocks/copper_block.png",
                item_group=fabricpy.item_group.BUILDING_BLOCKS
            )

        Creating a block with mining configuration::

            block = Block(
                id="mymod:ruby_ore",
                name="Ruby Ore",
                hardness=3.0,
                resistance=3.0,
                tool_type="pickaxe",
                mining_level="iron",
                requires_tool=True,
            )

        Creating a block with per-tool mining speeds::

            block = Block(
                id="mymod:mixed_ore",
                name="Mixed Ore",
                hardness=4.0,
                resistance=4.0,
                mining_speeds={
                    "pickaxe": 8.0,
                    "shovel": 3.0,
                },
                requires_tool=True,
                mining_level="stone",
            )
    """

    def __init__(
        self,
        id: str | None = None,
        name: str | None = None,
        max_stack_size: int = 64,
        block_texture_path: str | None = None,
        inventory_texture_path: str | None = None,
        recipe: object | None = None,  # instance of RecipeJson or None
        item_group: object | str | None = None,
        left_click_event: str | None = None,
        right_click_event: str | None = None,
        loot_table: object | None = None,  # instance of LootTable or None
        tool_type: str
        | None = None,  # "pickaxe", "axe", "shovel", "hoe", "sword", or None
        hardness: float | None = None,
        resistance: float | None = None,
        mining_level: str | None = None,  # "stone", "iron", "diamond", or None
        requires_tool: bool | None = None,
        mining_speeds: dict[str, float] | None = None,
    ):
        """Initialize a new Block instance.

        Args:
            id: The registry identifier for the block.
            name: The display name for the block.
            max_stack_size: Maximum number of block items that can be stacked.
            block_texture_path: Path to the block's world texture file.
            inventory_texture_path: Path to the block's inventory texture file.
                Falls back to block_texture_path if not provided.
            recipe: Recipe definition for crafting this block.
            item_group: Creative tab to place this block's item in.
            left_click_event: Java code to execute when the block is left clicked.
                Prefer overriding :meth:`on_left_click` in a subclass.
            right_click_event: Java code to execute when the block is right clicked.
                Prefer overriding :meth:`on_right_click` in a subclass.
            loot_table: Loot table for block drops.
            tool_type: Primary tool type for efficient mining.
            hardness: Block hardness (mining time base).
            resistance: Blast resistance.
            mining_level: Minimum tool tier (``"stone"``, ``"iron"``, or
                ``"diamond"``).
            requires_tool: Whether correct tool is required for drops.
                Inferred from ``tool_type`` when ``None``.
            mining_speeds: Per-tool speed overrides as ``{tool: speed}``
                mapping.

        Raises:
            ValueError: If *tool_type*, *mining_level*, or any key in
                *mining_speeds* is not a recognised value.
        """
        # ── validation ------------------------------------------------ #
        if tool_type is not None and tool_type not in VALID_TOOL_TYPES:
            raise ValueError(
                f"tool_type must be one of {sorted(VALID_TOOL_TYPES)}, "
                f"got {tool_type!r}"
            )
        if mining_level is not None and mining_level not in VALID_MINING_LEVELS:
            raise ValueError(
                f"mining_level must be one of {sorted(VALID_MINING_LEVELS)}, "
                f"got {mining_level!r}"
            )
        if mining_speeds is not None:
            bad = set(mining_speeds) - VALID_TOOL_TYPES
            if bad:
                raise ValueError(
                    f"mining_speeds keys must be from {sorted(VALID_TOOL_TYPES)}, "
                    f"got invalid key(s): {sorted(bad)}"
                )

        self.id = id
        self.name = name
        self.max_stack_size = max_stack_size
        self.block_texture_path = block_texture_path
        # fall back to block texture if no inventory-specific texture provided
        self.inventory_texture_path = inventory_texture_path or block_texture_path
        self.recipe = recipe
        self.item_group = item_group
        self.left_click_event = left_click_event
        self.right_click_event = right_click_event
        self.loot_table = loot_table
        self.tool_type = tool_type
        self.hardness = hardness
        self.resistance = resistance
        self.mining_level = mining_level
        # Infer requires_tool: True when tool_type is set, False otherwise
        self.requires_tool = (
            requires_tool if requires_tool is not None else (tool_type is not None)
        )
        self.mining_speeds = dict(mining_speeds) if mining_speeds else None

    # ------------------------------------------------------------------ #
    # event hooks                                                        #
    # ------------------------------------------------------------------ #

    def on_left_click(self) -> str | None:  # noqa: D401
        """Java code executed when the block is left clicked.

        Subclasses can override this to return a string of Java statements. The
        default implementation returns the value of ``left_click_event`` passed
        to the constructor, enabling both declarative and imperative styles.
        ``ActionResult.SUCCESS`` is automatically returned, so the string should
        only contain the statements to run when the block is clicked.
        """

        return self.left_click_event

    def on_right_click(self) -> str | None:  # noqa: D401
        """Java code executed when the block is right clicked.

        Subclasses can override this to return a string of Java statements. The
        default implementation returns ``right_click_event`` from the
        constructor. ``ActionResult.SUCCESS`` is automatically returned, so only
        the desired statements should be provided.
        """

        return self.right_click_event
