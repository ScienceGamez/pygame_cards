from minion_card import MinionCard
from pygame_cards.set import CardsSet


MY_COMMUNITY_OF_THE_RING = CardsSet(
    [
        MinionCard("Bilbo", 5, 2, 2),
        MinionCard("Gandalf", 10, 6, 8),
        MinionCard("Sam", 7, 1, 2),
    ]
)

print(MY_COMMUNITY_OF_THE_RING)
