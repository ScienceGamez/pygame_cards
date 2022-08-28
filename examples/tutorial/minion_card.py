# Import the abstact card class
from pygame_cards.abstract import AbstractCard

from dataclasses import dataclass


@dataclass
class MinionCard(AbstractCard):
    """A card that represent a minion.

    A minion has a health, an attack and a cost.
    """

    health: int
    attack: int
    cost: int

    description: str = ""


if __name__ == "__main__":

    card = MinionCard(
        name="Frodo the Hobbit",
        health=6,
        attack=2,
        cost=3,
        description=(
            "Frodo's name comes from the Old English name Fróda, "
            "meaning 'wise by experience'"
        ),
    )

    print(card)
