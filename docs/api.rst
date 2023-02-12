
API
===

.. automodule:: pygame_cards

Game Objects and Graphic Objects
--------------------------------

pygame_cards is object oriented in the sense that all the game elements
are implemented as python objects.

pygame_cards also aims in the future at being able to run on a server
and on clients, splitting the graphic part of the game and the logic
part.

For that reason, each game element has its own object and a corresponding
graphic object.
For example, a Card object will have a corresponding CardGraphic object.


The documentation sections will contain for each type of game element
all the possible graphics implemented.



Abstract Graphics
^^^^^^^^^^^^^^^^^

The abstract graphic class is the parent for all graphics classes in
pygame_cards it contains the main elements required for compatibility
with pygame_cards.

.. autoclass:: pygame_cards.abstract.AbstractGraphic
    :members:



Cards
^^^^^

.. autoclass:: pygame_cards.abstract.AbstractCard
    :members:

Graphics
""""""""

.. autoclass:: pygame_cards.abstract.AbstractCardGraphics
    :members:

.. autoclass:: pygame_cards.back.CardBackGraphics
    :members:




Cards Set
^^^^^^^^^

.. autoclass:: pygame_cards.set.CardsSet
    :members:
    :inherited-members:

Graphics
""""""""

Hands and Piles are similiar but they have the main difference that
in a hand cards will always try to fill the space available.
Piles will try to arrange the cards nicely based on the offset, but
might not fill the space.
Piles will contract the cards if the space they try to fill is too small.

.. autoclass:: pygame_cards.set.CardsetGraphic
    :members:

.. autoclass:: pygame_cards.deck.CardBackOwner
    :members:

.. autoclass:: pygame_cards.deck.Deck
    :members:

.. autoclass:: pygame_cards.hands.BaseHand
    :members:

.. autoclass:: pygame_cards.hands.AlignedHand
    :members:

.. autoclass:: pygame_cards.hands.RoundedHand
    :members:

.. autoclass:: pygame_cards.hands.Pile
    :members:

.. autoclass:: pygame_cards.hands.VerticalPileGraphic
    :members:

.. autoclass:: pygame_cards.hands.HorizontalPileGraphic
    :members:



Boards
^^^^^^

Some game require players to interact with different pile/sets of cards.
For that reason pygame_cards implements a boards on which card sets can
be placed.

.. autoclass:: pygame_cards.board.GameBoard
    :members:

Graphics
""""""""

.. autoclass:: pygame_cards.board.GameBoardGraphic
    :members:

.. autoclass:: pygame_cards.board.ColumnsBoardGraphic
    :members:



Other Objects
^^^^^^^^^^^^^

.. automodule:: pygame_cards.tokens
    :members:

Game Managers
-------------

.. autoclass:: pygame_cards.abstract.Manager
    :members:


.. autoclass:: pygame_cards.manager.CardsManager
    :members:

.. autoclass:: pygame_cards.manager.CardSetRights
    :members:




Classic cards
-------------



.. automodule:: pygame_cards.classics
    :members:


Drawing Functions
-----------------

pygame_cards also comes with some functions to draw cards related objects.

.. automodule:: pygame_cards.effects
    :members:


Events
------

.. automodule:: pygame_cards.events
    :members:


Networking
----------

.. warning:: This is currently not implemented

.. automodule:: pygame_cards.defaults
    :members:

.. automodule:: pygame_cards.game


Utilities
---------

.. automodule:: pygame_cards.utils
    :members: