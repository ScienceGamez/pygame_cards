"""In many card games players also use tokens.

pygame_cards also include suport for tokens.

* Token graphics for displaying a token
* ValuedToken is a token with a Value
* Token container which display piles of tokens
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

import pygame

from pygame_cards.abstract import AbstractGraphic

if TYPE_CHECKING:
    from pygame._common import _ColorValue


@dataclass
class RoundTokenGraphics(AbstractGraphic):
    """A graphic for a round token.

    :arg radius: The radius of the round token.
    """

    radius: int = 200

    def __post_init__(self):
        self._size = (self.radius * 2, self.radius * 2)


@dataclass
class SquaredTokenGraphics(AbstractGraphic):
    """A graphic for a square token.

    :arg edge: The edge size of the square token.
    :arg radius: The radius of the corner of the square token.
        Allows to round the corners of the Token.
    """

    edge: int = 100
    radius: int = 20

    def __post_init__(self):
        self._size = (self.edge, self.edge)


@dataclass
class Dice(SquaredTokenGraphics):
    """A dice from 2D top view.


    .. image:: images/dice.png

    :arg value: The value of the dice (from 1 to 6)
    :arg dot_radius: The size of the radius of the circles on the dice.
    :arg border_width: The width of the line defining
        the border of the dice.
    :arg background_color: The color of the background of the dice.
    :arg drawings_color: The color of the drawings on the dice
        (the dots and the border).

    """

    value: int = 1
    dot_radius: int = 10
    border_width: int = 0

    background_color: _ColorValue = "white"
    drawings_color: _ColorValue = "black"

    def set_value(self, value: int):
        """Set the value of the dice."""
        if value > 6 or value < 1:
            raise ValueError("Dice value must be between 1 and 6.")
        self.value = value
        self.clear_cache()

    def clear_cache(self) -> None:
        super().clear_cache()
        self.__dict__.pop("background", None)

    @cached_property
    def background(self) -> pygame.Surface:
        surf = pygame.Surface((self.edge, self.edge), pygame.SRCALPHA)
        pygame.draw.rect(
            surf,
            self.background_color,
            pygame.Rect(0, 0, self.edge, self.edge),
            border_radius=self.radius,
        )
        if self.border_width != 0:
            pygame.draw.rect(
                surf,
                self.drawings_color,
                rect=pygame.Rect(0, 0, self.edge, self.edge),
                width=int(self.border_width),
                border_radius=self.radius,
            )
        return surf

    @cached_property
    def surface(self) -> pygame.Surface:
        surf = self.background

        distance_to_border = self.radius + self.dot_radius

        if self.value == 1 or self.value == 3 or self.value == 5:
            # Central dot
            pygame.draw.circle(
                surf,
                self.drawings_color,
                (self.edge // 2, self.edge // 2),
                self.dot_radius,
            )
        if self.value > 1:
            # top right and bot left dots
            pygame.draw.circle(
                surf,
                self.drawings_color,
                (self.edge - distance_to_border, distance_to_border),
                self.dot_radius,
            )
            pygame.draw.circle(
                surf,
                self.drawings_color,
                (distance_to_border, self.edge - distance_to_border),
                self.dot_radius,
            )
        if self.value > 3:
            # top left and bot right dots
            pygame.draw.circle(
                surf,
                self.drawings_color,
                (
                    self.edge - distance_to_border,
                    self.edge - distance_to_border,
                ),
                self.dot_radius,
            )
            pygame.draw.circle(
                surf,
                self.drawings_color,
                (distance_to_border, distance_to_border),
                self.dot_radius,
            )

        if self.value == 6:
            # Mid right and left values
            pygame.draw.circle(
                surf,
                self.drawings_color,
                (distance_to_border, self.edge // 2),
                self.dot_radius,
            )
            pygame.draw.circle(
                surf,
                self.drawings_color,
                (self.edge - distance_to_border, self.edge // 2),
                self.dot_radius,
            )
        return surf


@dataclass
class PokerChipGraphics(RoundTokenGraphics):
    """A poker chip

    .. image:: images/poker_chip.png


    :arg color: The color of the token.
    :arg drawings_color: The color of the drawings on the token.
    :arg border_radius: The radius of the border
    :arg inner_line_width: The width of the line inside
    """

    color: _ColorValue = "blue"
    drawings_color: _ColorValue = "white"
    border_radius: int = 20
    inner_line_width: int = 10

    def __post_init__(self):
        super().__post_init__()
        assert self.border_radius < self.radius

    @cached_property
    def surface(self) -> pygame.Surface:
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color, (self.radius, self.radius), self.radius)
        # Draw the small lines in the inner circle
        inner_rect = pygame.Rect(
            self.border_radius,
            self.border_radius,
            2 * (self.radius - self.border_radius),
            2 * (self.radius - self.border_radius),
        )
        N_ARCS = 12
        for i in range(N_ARCS):
            angle = i * 2 * math.pi / N_ARCS
            pygame.draw.arc(
                surf,
                self.drawings_color,
                inner_rect,
                start_angle=angle,
                stop_angle=angle + math.pi / N_ARCS,
                width=10,
            )

        # Draw the big lines on the border
        outer_rect = pygame.Rect(0, 0, *self.size)
        offset = 2 * math.pi / N_ARCS / 2 / 2
        for i in range(N_ARCS // 2):
            angle = i * 2 * 2 * math.pi / N_ARCS - offset
            pygame.draw.arc(
                surf,
                self.drawings_color,
                outer_rect,
                start_angle=angle,
                stop_angle=angle + 2 * math.pi / N_ARCS,
                width=self.border_radius - self.inner_line_width,
            )

        # Add the dices on the sizes
        dice_edge = self.border_radius * 0.8
        dice = Dice(
            edge=dice_edge,
            radius=int(dice_edge * 0.1),
            dot_radius=dice_edge * 0.1,
            border_width=dice_edge * 0.05,
            background_color=self.color,
            drawings_color=self.drawings_color,
        )
        for i in range(6):
            angle = 2 * math.pi / 6 * i + offset
            dice.set_value(i + 1)
            dice_surf = pygame.transform.rotate(dice.surface, angle=math.degrees(angle))
            surf.blit(
                dice_surf,
                (
                    self.radius
                    + math.sin(angle) * (self.radius - self.border_radius / 2)
                    - dice_surf.get_size()[0] / 2,
                    self.radius
                    + math.cos(angle) * (self.radius - self.border_radius / 2)
                    - dice_surf.get_size()[1] / 2,
                ),
            )
        return surf


if __name__ == "__main__":
    pygame.init()

    screen = pygame.display.set_mode((800, 400))
    screen.fill("black")

    chip = PokerChipGraphics(radius=200, border_radius=60)
    screen.blit(chip.surface, (0, 0))
    running = True

    pygame.image.save(chip.surface, "docs/images/poker_chip.png")

    dice = Dice(edge=400, value=6, dot_radius=30, radius=40, background_color="orange")
    screen.blit(dice.surface, (400, 0))
    pygame.image.save(dice.surface, "docs/images/dice.png")

    pygame.display.flip()
    # Game loop
    # keep game running till running is true
    while running:
        # Check for event if user has pushed
        # any event in queue
        for event in pygame.event.get():
            # if event is of type quit then set
            # running bool to false
            if event.type == pygame.QUIT:
                running = False
