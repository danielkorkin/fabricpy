Sending Messages to Players
==========================

fabricpy provides helper functions in :mod:`fabricpy.message` for sending
feedback to players from generated Java code. These helpers return Java
statements that can be inserted into event handlers like block click callbacks.

.. code-block:: python

    from fabricpy.message import send_message, send_action_bar_message
    import fabricpy

    class MessageBlock(fabricpy.Block):
        def __init__(self):
            super().__init__(id="mymod:message_block", name="Message Block")

        def on_left_click(self):
            return send_message("Hi!")

        def on_right_click(self):
            return send_action_bar_message("Watch out!")

Both helpers take the message text and optionally the name of the player
variable in scope. The click handlers automatically return
``ActionResult.SUCCESS`` for you, so only the messaging statements are needed.

* ``send_message`` sends a normal chat message.
* ``send_action_bar_message`` displays text in the player's action bar.

See :file:`examples/message_block.py` for the complete example.
