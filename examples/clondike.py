"""This is the first game we implement."""
from dataclasses import dataclass
from functools import cached_property
import sys
import pygame

from pygame_cards.back import CARD_BACK
from pygame_cards.hands import AlignedHand
from pygame_cards.manager import CardSetRights, CardsManager
from pygame_cards.hands import CardsetGraphic
from pygame_cards.deck import CardBackOwner, Deck

from pygame_cards.set import CardsSet
from pygame_cards.classics import CardSets
from pygame_cards.abstract import AbstractCard


pygame.init()


screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
# screen = pygame.display.set_mode((400, 300))
size = width, height = screen.get_size()


manager = CardsManager()


@dataclass
class ClondikePileGaphics(CardBackOwner):
    """Show a column in clondike.

    All cards are hidden but the last one is shown.

    :attr v_offset: The offset between cards in vertical.
    """

    v_offset: int = 20

    @cached_property
    def surface(self) -> pygame.Surface:

        # Create the surface
        surf = pygame.Surface(self.size)

        # Calculate how we position the cards
        n_cards = len(self.cardset)
        if n_cards == 0:
            return surf
        expected_h = n_cards * self.v_offset + self.card_size[1]
        h_space = (
            (self.size[1] - self.card_size[1]) / n_cards
            if expected_h > self.size[1]
            else self.v_offset
        )
        y_positions = [i * h_space for i in range(n_cards)]
        x_position = (self.size[0] - self.card_size[0]) / 2

        # Add the cards on the surface
        for y in y_positions[:-1]:
            surf.blit(self.card_back, (x_position, y))
        surf.blit(
            self.cardset[-1].graphics.surface, (x_position, y_positions[-1])
        )

        return surf

    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard:
        """Return the card at the given pixel position

        :arg pos: The position inside the CardsetGraphic surface.
        """
        if self.cardset:
            return self.cardset[-1]
        else:
            return None


card_set = CardSets.n52
card_set.shuffle()

N_PILES = 7

pile_size = (width / (N_PILES + 2), height * 0.8)
card_size = (pile_size[0] * 0.8, pile_size[1] / 3)

# Get the card set of each pile
piles_card_sets = []
piles_graphics = []
card_idx = 0
for pile in range(N_PILES):
    # Piles increase in size all the time
    next_card_idx = card_idx + pile + 1
    piles_card_sets.append(card_set[card_idx:next_card_idx])
    card_idx = next_card_idx
    piles_graphics.append(
        ClondikePileGaphics(piles_card_sets[-1], pile_size, card_size)
    )

    # Finally add the set to the manager
    manager.add_set(
        piles_graphics[-1],
        # Position on the screen
        (pile_size[0] * (pile + 1), height * 0.2),
        CardSetRights(
            draggable_in=True,
            draggable_out=True,
            highlight_hovered_card=True,
        ),
    )


pygame.display.flip()

clock = pygame.time.Clock()

annimation_tick_left = 0


while 1:
    screen.fill("black")
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sys.exit()
        manager.process_events(event)

    manager.update(time_delta)
    manager.draw(screen)
    pygame.display.flip()
