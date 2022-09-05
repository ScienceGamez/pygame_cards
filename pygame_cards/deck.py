from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from numpy import linspace

import pygame
import pygame_cards
from pygame_cards.abstract import AbstractCard
from pygame_cards.effects import outer_border, outer_halo
from pygame_cards.hands import CardsetGraphic

from pygame_emojis import load_svg

from pygame_cards.utils import DEFAULT_CARDBACK


@dataclass
class Deck(CardsetGraphic):
    """Graphics for a deck."""

    size: tuple[int, int] = (160, 230)
    _card_back: pygame.Surface = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self.card_back = DEFAULT_CARDBACK
        # Assign a default max size assuming the deck is full
        if self.max_cards == 0:
            self.max_cards = len(self.cardset)

    @property
    def card_back(self) -> pygame.Surface:
        """The card back that should be shonw from the deck."""
        return self._card_back

    @card_back.setter
    def card_back(
        self, card_back: Path | str | pygame.Surface, add_border: bool = True
    ):
        if isinstance(card_back, Path | str):
            if Path(card_back).suffix == ".svg":
                _card_back = pygame.Surface(self.card_size)
                _card_back.fill("white")
                _card_back.blit(load_svg(card_back, self.card_size), (0, 0))
            else:
                _card_back = pygame.image.load(card_back)
        elif isinstance(card_back, pygame.Surface):
            _card_back = card_back
        else:
            raise TypeError("card_back")

        if _card_back.get_size() != self.card_size:
            _card_back = pygame.transform.scale(_card_back, self.card_size)

        if self.card_border_radius:
            # Round the corners of the card
            # https://stackoverflow.com/a/63701005/15368670
            rect_image = pygame.Surface(self.card_size, pygame.SRCALPHA)
            pygame.draw.rect(
                rect_image,
                (255, 255, 255),
                (0, 0, *self.card_size),
                border_radius=self.card_border_radius,
            )
            _card_back = _card_back.copy().convert_alpha()
            _card_back.blit(rect_image, (0, 0), None, pygame.BLEND_RGBA_MIN)

        if add_border:
            outer_border(_card_back, inplace=True)

        self._card_back = _card_back

    @cached_property
    def surface(self) -> pygame.Surface:
        """Should make a pile of cards."""
        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        # Calculate positions for the cards
        x_positions = linspace(
            0,
            self.size[0] - self.card_size[0],
            self.max_cards or len(self.cardset),
            dtype=int,
        )
        y_positions = linspace(
            self.size[1] - self.card_size[1],
            0,
            self.max_cards or len(self.cardset),
            dtype=int,
        )

        # Blit all cards at their positions
        for card, x, y in zip(self.cardset, x_positions, y_positions):
            surf.blit(
                self.card_back,
                (x, y)
                # (
                #    (self.size[0] - self.card_size[0]) // 2,
                #    (self.size[1] - self.card_size[1]) // 2,
                # ),
            )
        return surf

    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard | None:
        if self.cardset:
            return self.cardset[-1]
        else:
            # Empty set
            return None


if __name__ == "__main__":

    # This will visualize the cards

    import sys
    import pygame
    from pygame_cards.classics import CardSets

    pygame.init()

    size = width, height = 1500, 1000

    screen = pygame.display.set_mode(size)

    set = CardSets.n52
    deck = Deck(set)
    deck_with_max = Deck(set, max_cards=100)

    if HALO := False:
        screen.blit(outer_halo(deck.surface), (200 - 20, 200 - 20))
        screen.blit(outer_halo(deck_with_max.surface), (600 - 20, 200 - 20))

    screen.blit(deck.surface, (200, 200))

    screen.blit(deck_with_max.surface, (600, 200))
    while 1:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            pygame.display.update()

        pygame.time.wait(100)
