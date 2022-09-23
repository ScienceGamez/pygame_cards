"""Sever for a card game.

:py:mod:`pygame_cards.server` works with the :py:mod:`pygame_cards.events`
module.
Events are sent to the server and the server updates the player
with the events from other players.

The server works as authority for the game state and checks
that the events are valid.

You can apply you own game rules inside the server.


"""
