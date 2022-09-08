"""This is the first game we implement."""
import sys
import pygame
from examples.tutorial.minion_card_graphics import MinionCardGraphics
from pygame_cards.back import CARD_BACK
from pygame_cards.hands import AlignedHand
from pygame_cards.manager import CardSetRights, CardsManager

from minion_set import MY_COMMUNITY_OF_THE_RING
from pygame_cards.set import CardsSet

pygame.init()


screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
# screen = pygame.display.set_mode((400, 300))
size = width, height = screen.get_size()
print(size)


manager = CardsManager()


# Creates your card set
my_cards = MY_COMMUNITY_OF_THE_RING.copy()


card_size = (width / 7, height / 3 - 20)
card_set_size = (width / 2, height / 3)
my_cards_graphics = AlignedHand(
    my_cards,
    card_set_size,
    card_size=card_size,
    graphics_type=MinionCardGraphics,
)
# Finally add the set to the manager
manager.add_set(
    my_cards_graphics,
    # Position on the screen
    (width / 4, height - my_cards_graphics.size[1]),
)

ennemy_cards = CardsSet([CARD_BACK, CARD_BACK, CARD_BACK])
ennemy_cards_graphics = AlignedHand(
    ennemy_cards, card_set_size, card_size=card_size
)
manager.add_set(
    ennemy_cards_graphics,
    # Place them in front on the screen
    (width / 4, 0),
    # Remove the possibility to interact with enemy cards
    CardSetRights(
        draggable_in=False, draggable_out=False, highlight_hovered_card=False
    ),
)

battle_ground = CardsSet()
battle_ground_graphics = AlignedHand(
    battle_ground,
    card_size=(1.2 * card_size[0], 1.2 * card_size[1]),
    size=(1.2 * card_set_size[0], 1.2 * card_set_size[1]),
    max_cards=2,
)
manager.add_set(
    battle_ground_graphics,
    (
        (width - battle_ground_graphics.size[0]) / 2,
        (height - battle_ground_graphics.size[1]) / 2,
    ),
    # Remove the possibility to remove cards
    CardSetRights(draggable_in=True, draggable_out=False),
)


pygame.display.flip()

clock = pygame.time.Clock()

annimation_tick_left = 0


def enemy_plays_cards():
    """Make the enemy play his card"""
    card_taken = ennemy_cards_graphics.cardset[0]
    ennemy_cards_graphics.remove_card(card_taken)
    battle_ground_graphics.append_card(card_taken)


enemy_plays_cards()

while 1:
    screen.fill("black")
    time_delta = clock.tick(60) / 1000.0

    if annimation_tick_left > 0:
        # Show a win annimation

        if annimation_tick_left == 1:
            # Give back the cards from each player
            opp_card = battle_ground[0]
            ennemy_cards_graphics.append_card(opp_card)
            battle_ground_graphics.remove_card(opp_card)

            # My card was played second
            my_card = battle_ground[0]
            my_cards_graphics.append_card(my_card)
            battle_ground_graphics.remove_card(my_card)

            enemy_plays_cards()

        annimation_tick_left -= 1

    if len(battle_ground) == 2 and annimation_tick_left == 0:
        annimation_tick_left = 10

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sys.exit()
        manager.process_events(event)

    manager.update(time_delta)
    manager.draw(screen)
    pygame.display.flip()
