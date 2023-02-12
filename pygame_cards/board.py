"""Game boards. 

Game boards allow for having cards and other things at specific places.
"""
from __future__ import annotations
import sys
import pygame

from pygame_cards.abstract import AbstractGraphic
from pygame_cards.set import CardsSet


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
        cardsets_rel_size: dict[CardsSet, tuple[float, float]]
        | tuple[int, int] = (200, 100),
        size: tuple[int, int] = (600, 400),
    ) -> None:
        self.size = size
        self.cardsets_rel_pos = cardsets_rel_pos
        self.cardsets_rel_size = cardsets_rel_size

    @property
    def background(self) -> pygame.Surface:
        # Transparent surface as default
        return pygame.Surface(self.size, pygame.SRCALPHA)

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
            self.logger.debug(f"{cardset}, {pos=}")
            surf.blit(cardset.graphics.surface, pos)
        return surf


class GameBoard:
    """Base class for game boards."""

    graphics: GameBoardGraphic

    cardsets: list[CardsSet]

    def __init__(self, cardsets: list[CardsSet] = []) -> None:
        self.cardsets = cardsets


if __name__ == "__main__":
    import logging
    from pygame_cards.classics import CardSets
    from pygame_cards.hands import VerticalPileGraphic

    logging.basicConfig()
    set_1 = CardSets.n52[:10]
    set_1.graphics = VerticalPileGraphic(set_1)
    set_2 = CardSets.n52[-10:]
    set_2.graphics = VerticalPileGraphic(set_2)

    board = GameBoard([set_1, set_2])
    board_graphics = GameBoardGraphic(
        cardsets_rel_pos={set_1: (0, 0.1), set_2: (0.5, 0.1)},
    )

    # Show the graphics surface in teh main pygame loop
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))

    pygame.display.set_caption("Game Board")
    board.graphics = board_graphics
    board.graphics.logger.setLevel(logging.DEBUG)
    board_graphics.game_board = board
    surf = board.graphics.surface()
    fps = 60
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
        screen.blit(surf, (0, 0))
        clock.tick(fps)

        pygame.display.flip()
