"""Game boards.

Game boards allow for having cards and other things at specific places.
"""

from __future__ import annotations
from functools import cached_property
import sys
import pygame

from pygame_cards.abstract import AbstractGraphic
from pygame_cards.set import CardsSet
from pygame_cards import constants


class GameBoardGraphic(AbstractGraphic):
    """Represent the graphics of the game board."""

    game_board: GameBoard

    size: tuple[int, int]

    # Maps the cardsets to the position they should go
    cardsets_rel_pos: dict[CardsSet, tuple[float, float]]
    cardsets_rel_size: dict[CardsSet, tuple[float, float]]

    card_sizes: dict[CardsSet, tuple[int, int]] | tuple[int, int]

    def __init__(
        self,
        cardsets_rel_pos: dict[CardsSet, tuple[float, float]] = {},
        cardsets_rel_size: dict[CardsSet, tuple[float, float]] | tuple[int, int] = (
            0.2,
            0.8,
        ),
        size: tuple[int, int] = constants.BOARD_SIZE,
    ) -> None:
        """Initialize a game board.

        Different cardsets are places at different places on the board.

        :arg cardsets_rel_pos: Relative positions of the cardsets.
        :arg cardsets_rel_size: Relative size of the cardsets on the
            board.
        :arg size: The size of the boad in pixels.
        """
        self._size = size
        self.cardsets_rel_pos = cardsets_rel_pos
        self.cardsets_rel_size = cardsets_rel_size

    def clear_cache(self) -> None:
        super().clear_cache()
        self.__dict__.pop("background", None)

    @cached_property
    def background(self) -> pygame.Surface:
        # Transparent surface as default
        return pygame.Surface(self.size, pygame.SRCALPHA)

    @cached_property
    def surface(self) -> pygame.Surface:
        """Show the game board with the gards."""

        surf = self.background

        for cardset in self.game_board.cardsets:
            rel_pos = self.cardsets_rel_pos[cardset]
            pos = rel_pos[0] * self.size[0], rel_pos[1] * self.size[1]
            rel_size = (
                self.cardsets_rel_size[cardset]
                if isinstance(self.cardsets_rel_size, dict)
                else self.cardsets_rel_size
            )
            size = rel_size[0] * self.size[0], rel_size[1] * self.size[1]

            cardset.graphics.size = size
            self.logger.debug(f"{cardset}, {pos=}")
            surf.blit(cardset.graphics.surface, pos)
        return surf


class GameBoard:
    """Base class for game boards."""

    graphics: GameBoardGraphic

    cardsets: list[CardsSet]

    def __init__(self, cardsets: list[CardsSet] = []) -> None:
        self.cardsets = cardsets


class ColumnsBoardGraphic(GameBoardGraphic):
    """A game board organized in columns."""

    def __init__(
        self,
        game_board: GameBoard,
        size: tuple[int, int] = constants.BOARD_SIZE,
        space_ratio: float = constants.COLUMN_SPACING,
        horizontal_margins_ratio: float = constants.COLUMN_SPACING,
        vertical_margins_ratio: float = constants.COLUMN_SPACING,
        card_size_ratio: tuple[int | float, int | float] = constants.CARD_SIZE,
    ):
        """Create the graphics.

        The number of columns is determined by the number of cards sets
        in the game_board.
        The colums are spaced on the game board based on the required
        settings.
        Card size are also determined based on the
        """
        self.game_board = game_board
        self.size = size
        self.space_ratio = space_ratio
        self.horizontal_margins_ratio = horizontal_margins_ratio
        self.vertical_margins_ratio = vertical_margins_ratio
        self.card_size_ratio = card_size_ratio

    def clear_cache(self) -> None:
        """Clear the cache."""
        super().clear_cache()
        for prop in ["margins", "card_size"]:
            self.__dict__.pop(prop, None)

    @cached_property
    def margins(self) -> tuple[int, int]:
        """Margins for the sides of the board."""
        card_size = self.card_size

        return (
            card_size[0] * self.horizontal_margins_ratio,
            card_size[1] * self.vertical_margins_ratio,
        )

    @cached_property
    def card_size(self) -> tuple[int, int]:
        """Define the card size based on the layout of the board."""
        n_cols = len(self.game_board.cardsets)

        # look at all elements consisitng of the board
        ratio_sum = (
            n_cols + 2 * self.horizontal_margins_ratio + (n_cols - 1) * self.space_ratio
        )
        # a card has ratio 1
        card_width = self.size[0] * ratio_sum
        card_height = (card_width / self.card_size_ratio[0]) * self.card_size_ratio[1]

        return card_width, card_height


if __name__ == "__main__":
    import logging
    from pygame_cards.classics import CardSets
    from pygame_cards.hands import VerticalPileGraphic

    logging.basicConfig()
    logger = logging.getLogger("main")
    logger.setLevel(logging.DEBUG)

    set_1 = CardSets.n52[:10]
    logger.debug(f"{type(set_1)}")

    set_1.graphics = VerticalPileGraphic(set_1)
    set_2 = CardSets.n52[-10:]
    set_2.graphics = VerticalPileGraphic(set_2)
    set_2.graphics.logger.setLevel(logging.DEBUG)

    board = GameBoard([set_1, set_2])
    board_graphics = GameBoardGraphic(
        cardsets_rel_pos={set_1: (0, 0.1), set_2: (0.5, 0.1)},
        cardsets_rel_size={set_1: (0.2, 0.5), set_2: (0.1, 0.8)},
    )

    # Show the graphics surface in teh main pygame loop
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))

    pygame.display.set_caption("Game Board")
    board.graphics = board_graphics
    board.graphics.logger.setLevel(logging.DEBUG)
    board_graphics.game_board = board
    board_graphics.size = screen.get_size()

    surf = board.graphics.surface
    fps = 10
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
        screen.blit(surf, (0, 0))
        clock.tick(fps)

        pygame.display.flip()
