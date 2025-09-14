"""Message helper functions for generated Fabric mods.

These helpers return Java code snippets that send messages to players. They are
intended for use in event handlers such as block click callbacks.

Example:
    >>> from fabricpy.message import send_message
    >>> block = fabricpy.Block(
    ...     id="mymod:example",
    ...     name="Example",
    ...     left_click_event=send_message("Hello!")
    ... )
"""
from __future__ import annotations

__all__ = ["send_message", "send_action_bar_message"]


def send_message(message: str, player_var: str = "player") -> str:
    """Return Java code to send a chat message to a player.

    Args:
        message: The text to display to the player.
        player_var: Name of the player variable in scope. Defaults to ``"player"``.

    Returns:
        str: Java statement that sends the message.
    """
    escaped = message.replace('"', '\\"')
    return f'{player_var}.sendMessage(Text.literal("{escaped}"), false);'


def send_action_bar_message(message: str, player_var: str = "player") -> str:
    """Return Java code to send an action bar message to a player.

    Args:
        message: The text to display to the player.
        player_var: Name of the player variable in scope. Defaults to ``"player"``.

    Returns:
        str: Java statement that sends the message to the action bar.
    """
    escaped = message.replace('"', '\\"')
    return f'{player_var}.sendMessage(Text.literal("{escaped}"), true);'
