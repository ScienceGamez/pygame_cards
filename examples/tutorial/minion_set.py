from minion_card import MinionCard
from pygame_cards.set import CardsSet


my_community_of_the_ring = CardsSet(
    [
        MinionCard("Bilbo", 5, 2, 2),
        MinionCard("Gandalf", 10, 6, 8),
        MinionCard("Sam", 7, 1, 2),
    ]
)

print(my_community_of_the_ring)
