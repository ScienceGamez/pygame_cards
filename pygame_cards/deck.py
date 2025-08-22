from functools import cached_property
from pathlib import Path
from numpy import linspace

import pygame
from pygame_emojis import load_svg

from pygame_cards.abstract import AbstractCard
from pygame_cards.effects import outer_border, outer_halo
from pygame_cards.hands import CardsetGraphic
from pygame_cards.set import CardsSet
from pygame_cards.utils import DEFAULT_CARDBACK


class CardBackOwner(CardsetGraphic):
    """Graphic that can be used for any cardset that will show some card backs.

    Support setting card backs using the path to  files or using
    directly a pygame surface.

    This is intended to be inherited from if you need to have card backs
    in a custom CardsetGraphic.
    """

    def __init__(
        self, *args, card_back: Path | str | pygame.Surface = DEFAULT_CARDBACK, **kwargs
    ):
        """Create the cardset graphic.

        :arg card_back: The path to the image file or a pygame surface.
            If a path is given, the image will be loaded from the file.
            For improving the graphics, we recommend using a svg file as
            they can be loaded for the desired size directly.

        """
        super().__init__(*args, **kwargs)

        self.card_back = card_back

    @property
    def card_back(self) -> pygame.Surface:
        """The card back that should be shown."""
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
            elif Path(card_back).is_file():
                _card_back = pygame.image.load(card_back)
            else:
                raise FileNotFoundError(card_back)
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
            outer_border(_card_back, radius=self.card_border_radius, inplace=True)

        self._card_back = _card_back


class Deck(CardBackOwner):
    """Graphics for a deck.

    A deck simply shows its back.
    """

    def __init__(
        self,
        *args,
        visible: bool = False,
        **kwargs,
    ):
        if not "size" in kwargs:
            # Change the defualt size
            kwargs["size"] = (160, 230)

        super().__init__(*args, **kwargs)
        self.visible = visible

        # Assign a default max size assuming the deck is full
        # This is needed to show how big the pile is
        if self.max_cards == 0:
            self.max_cards = len(self.cardset)

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
                card.graphics.surface if self.visible else self.card_back,
                (x, y),
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

    def draw_cards(self, n_cards: int = 1) -> CardsSet:
        cards = self.cardset.draw(n_cards)
        self.clear_cache()
        return cards

    def get_card_positions(self) -> dict[AbstractCard, tuple[int, int]]:
        return {card: (0, 0) for card in self.cardset}


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
