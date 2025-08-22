"""pygame_cards custom events.

If you want to use them, don't use the int values, but instead import
the event from this module.
They are supposed to be used the same way as pygame events and are
dumped to the event loop.

.. code::

    from pygame_cards.events import CARD_CUSTOM_EVENT_YOU_WANT

Events have function corresponding to them that genereate the event
based on the card/cardsets concerned with the event.

Most of the events are fully handled by the :py:class:`CardsManager` .

"""

from __future__ import annotations
from typing import TYPE_CHECKING
from pygame.event import Event, custom_type

from pygame_cards.abstract import AbstractCard

if TYPE_CHECKING:
    from pygame_cards.set import CardsSet
    from pygame_cards.hands import CardsetGraphic

#: A card drag was started
CARD_DRAG_STARTED = custom_type()
#: The card being dragged was moved
CARD_DRAG_MOVED = custom_type()
#: The card being dragged was released
CARD_DRAG_STOPPED = custom_type()

#: The players drags a card from a set to another
CARD_MOVE_ATTEMPT = custom_type()
#: Card moved from a set to another (the attempt was allowed by the manager)
CARD_MOVED = custom_type()
#: Card hovered (for some time)
CARD_HOVERED = custom_type()
#: A cardset was clicked
CARDSSET_CLICKED = custom_type()


def cardsset_clicked(set: CardsSet, card: AbstractCard | None = None) -> Event:
    """When a cardset has been clicked by a user.

    The card clicked is also given. None if no card was under the click.
    """
    return Event(CARDSSET_CLICKED, {"set": set, "card": card})


def card_moved(
    card: AbstractCard, from_set: CardsetGraphic, to_set: CardsetGraphic
) -> Event:
    """When a card has been moved from one set to another."""
    return Event(
        CARD_MOVED,
        {
            "card": card,
            "from_set": from_set,
            "to_set": to_set,
        },
    )


if __name__ == "__main__":
    from pygame_cards.classics import CardSets

    e = cardsset_clicked(CardSets.n36)
    print(e)
