from __future__ import annotations
from typing import TYPE_CHECKING
from pygame.event import Event, custom_type

from pygame_cards.abstract import AbstractCard

if TYPE_CHECKING:
    from pygame_cards.set import CardsSet
# TODO: implement these events in a manager
# Graphics Events
CARD_DRAG_STARTED = custom_type()
CARD_DRAG_MOVED = custom_type()
CARD_DRAG_STOPPED = custom_type()

# The players drags a card from a set to another
CARD_MOVE_ATTEMPT = custom_type()
# Card moved from a set to another
CARD_MOVED = custom_type()
# Card hovered (for some time)
CARD_HOVERED = custom_type()

CARDSSET_CLICKED = custom_type()


def cardsset_clicked(set: CardsSet, card: AbstractCard | None):
    """When a cardset has been clicked by a user.

    The card clicked is also given. None if no card was under the click.
    """
    return Event(CARDSSET_CLICKED, {"set": set, "card": card})


if __name__ == "__main__":

    from pygame_cards.classics import CardSets

    e = cardsset_clicked(CardSets.n36)
    print(e)
