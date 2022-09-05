from abc import abstractmethod, abstractproperty
from dataclasses import dataclass
from enum import auto
from functools import cached_property
import logging
from math import cos, sin, sqrt
import math
from time import sleep
import pygame
from pygame_cards.abstract import AbstractCard
from pygame_cards.utils import AutoName
from pygame_cards.abstract import AbstractGraphic
from pygame_cards.effects import outer_halo
from pygame_cards.set import CardsSet


class CardOverlap(AutoName):
    left = auto()
    right = auto()


@dataclass
class CardsetGraphic(AbstractGraphic):
    """A base graphic fro any card holder.

    :attr cardset: The set of card that is shown.
    :attr size: A tuple with the size of the requested card in this graphic.
    :attr card_size: A tuple with the size of the cards in this graphic.
    :attr card_border_radius: The radius of the cards in this card set.
    :attr max_cards: The max number of card that can be contained in this
        graphic. If 0, this is unlimited.
    """

    cardset: CardsSet

    # Defualt hand size
    size: tuple[int, int] = (900, 240)
    card_size: tuple[int, int] = (135, 200)
    card_border_radius: int = 20

    max_cards: int = 0

    graphics_type: type | None = None

    def __post_init__(self):

        for card in self.cardset:
            # Enforce the type
            if self.graphics_type:
                card.graphics_type = self.graphics_type
            # Enforce the card size
            card.graphics.size = self.card_size
        self._raised_with_hovered_warning = False

    @abstractproperty
    def surface(self) -> pygame.Surface:
        raise NotImplementedError(
            f"property 'surface' in {type(self).__name__}"
        )

    @abstractmethod
    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard | None:
        """Return the card at the given pixel position

        :arg pos: The position inside the CardsetGraphic surface.
        """
        raise NotImplementedError(
            f"'get_card_at' in Class {type(self).__name__}"
        )

    def remove_card(self, card: AbstractCard) -> None:
        """Remove a card from the cardset."""

        self.cardset.remove(card)
        self.clear_cache()

    def append_card(self, card: AbstractCard) -> None:
        """Append a card to the cardset."""

        self.cardset.append(card)
        card.graphics.size = self.card_size
        card.graphics.clear_cache()
        self.clear_cache()

    def with_hovered(self, card: AbstractCard | None) -> pygame.Surface:
        """Show the hand with the card hovered."""
        if not self._raised_with_hovered_warning:
            logging.warning(
                f"Not implemented `with_hovered()` in {type(self).__name__}",
            )
            self._raised_with_hovered_warning = True
        return self.surface


@dataclass
class BaseHand(CardsetGraphic):
    """A base class for a hand.

    Usually in a hand the cards are shown on next to the other.

    :attr overlap_hide: The card to hide if to cards are one
        over each other. By default the card overlap on the right,
        which is the standard in card games.
        This also implies that the cards are located at the opposite side
        of their overlap.


    """

    overlap_hide: CardOverlap = CardOverlap.right


@dataclass
class AlignedHand(BaseHand):
    """A hand of card with all the cards aligned.

    :attr offset_position: The offset of the position between the cards.

        * 0, means the cards are directly next to each other.
        * Positive offset, means the card will be further
            away from each other.
        * Negative, means cards will be closer
            to each other.

    """

    offset_position: float = 20

    @cached_property
    def surface(self) -> pygame.Surface:
        """The surface of the hand."""
        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        x_positions, offset = self.calculate_x_positions()

        for i, (card, x_pos) in enumerate(zip(self.cardset, x_positions)):
            self.logger.debug(f"{card}")
            card_surf = card.graphics.surface
            card_surf = pygame.transform.scale(card_surf, self.card_size)

            self.logger.debug(f"{card=},{x_pos=}")
            surf.blit(card_surf, (x_pos, self.calculate_y_position()))

        return surf

    def remove_card(self, card: AbstractCard) -> None:
        super().remove_card(card)

    def calculate_y_position(self) -> int:
        return self.size[1] / 2 - self.card_size[1] / 2

    def calculate_x_positions(self) -> tuple[list[float], float]:
        """Calculate the x position of the cards.

        :return (x_positions, offset_value):
            The x_positions is the positions of each card.
            The offset_value is the value used to make the
            spacing between the cards.
        """
        # calculate dimenstions required for the displayed surf
        offset = self.offset_position
        total_x = (
            len(self.cardset) * self.card_size[0]
            + (len(self.cardset) - 1) * offset
        )

        if total_x > self.size[0]:
            self.logger.warning(
                "Too many cards for hands size, rescaling will apply."
            )
            offset = (self.size[0] - len(self.cardset) * self.card_size[0]) / (
                len(self.cardset) - 1
            )
        x_positions = [
            i * self.card_size[0] + (i + 1) * offset
            for i in range(len(self.cardset))
        ]
        # Revert the position in case of another overlap
        x_positions = [
            x_pos
            if self.overlap_hide == CardOverlap.right
            else self.size[0] - self.card_size[0] - x_pos
            for x_pos in x_positions
        ]
        return x_positions, offset

    def with_hovered(
        self, card: AbstractCard | None, radius: float = 20, **kwargs
    ) -> pygame.Surface:
        if card is None:
            return pygame.Surface((0, 0))
        index = self.cardset.index(card)
        self.logger.debug(f"{index=}")
        x_posistions, _ = self.calculate_x_positions()
        x_pos = x_posistions[index]

        card.graphics.size = self.card_size
        highlighted_surf = outer_halo(
            card.graphics.surface, radius=radius, **kwargs
        )
        # assume the center will be on it
        out_surf = pygame.Surface(self.size, pygame.SRCALPHA)
        highlighted_surf = pygame.transform.scale(
            highlighted_surf,
            (self.card_size[0] + 2 * radius, self.card_size[1] + 2 * radius),
        )
        out_surf.blit(
            highlighted_surf,
            (x_pos - radius, self.calculate_y_position() - radius),
        )
        out_surf.blit(
            card.graphics.surface,
            (x_pos, self.calculate_y_position()),
        )
        return out_surf

    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard | None:
        """Return the card at the given pixel position

        :arg pos: The position inside the CardsHand surface.
        """
        s = self.surface.get_size()
        if not (pos[0] < s[0] and pos[1] < s[1]):
            self.logger.error(f"get_card_at:{pos=} not in {s}.")
            return None

        x_positions, offset = self.calculate_x_positions()
        self.logger.debug(f"get_card_at:{x_positions=}, {self.overlap_hide=}")

        # TODO: make this work
        for card_index, x_pos in enumerate(x_positions):
            if pos[0] < x_pos or pos[0] > x_pos + self.card_size[0]:
                self.logger.debug(
                    f"get_card_at: {card_index=} is not Between the card boundaries"
                )
                continue
            if (
                self.overlap_hide == CardOverlap.right
                # Check that is not under the next card
                and pos[0] - x_pos > self.card_size[0] + self.offset_position
            ) or (
                self.overlap_hide == CardOverlap.left
                and pos[0] - x_pos < self.offset_position
            ):
                self.logger.debug(
                    f"get_card_at: {card_index=} is  going to be under the next card"
                )
                continue
            if x_pos - pos[0] > self.card_size[0] + offset:
                self.logger.debug(f"get_card_at:{pos=} is in offset.")
                continue  # Between two cards, in the offset

            self.logger.debug(f"get_card_at:{pos=} found index {card_index}.")
            return self.cardset[card_index]

        return None


@dataclass
class RoundedHand(BaseHand):
    """A hand of card with all the cards aligned on an arc of a circle.

    This will produced an hand of card where cards are clipped insided
    the size of the hand.


    :attr angle: The angle in which the cards are constrained
        (Unit: Degrees)
        If 0, the cards are all aligned.
        If not zero, the cards will be placed on an arc of a circle
        with the given angle.

    """

    angle: float = 90
    # Change the defualt size
    size: tuple[float, float] = (700, 400)

    def _max_card_h(self) -> float:
        """Return the maximum height that a card can do in surface."""
        return sqrt(
            self.card_size[0] * self.card_size[0]
            + self.card_size[1] * self.card_size[1]
        )

    @cached_property
    def surface(self) -> pygame.Surface:
        """The surface of the hand."""
        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        if self.angle == 0 or len(self.cardset) == 0:
            # Special cases, show aligned
            angles = [0] * len(self.cardset)
        else:
            angle_step = self.angle / (len(self.cardset) - 1)
            self.logger.debug(f"{angle_step=}")
            # from the center, angle = 0, which is the central card and ref point.
            angles = [
                -self.angle / 2 + i * angle_step
                for i in range(len(self.cardset))
            ]
        # Radius of the circle around the cards (from center to card centers)
        # Trust me, I am an engineer
        card_diagonal = sqrt(self.card_size[0] ** 2 + self.card_size[1] ** 2)
        radius = min(
            # Constraint for width
            (self.size[0] - card_diagonal)
            / 2
            / sin(math.radians(self.angle / 2)),
            # Constraint for heigth
            (self.size[1] - self.card_size[1] - card_diagonal / 2)
            / (1 - cos(math.radians(self.angle / 2))),
        )
        self.logger.debug(f"{radius = }")
        # TODO: correct the angle if the radius is smaller than a threshold

        # The center of the circle where cards centers are located
        center_pos = (
            self.size[0] / 2,
            # Direclty under the middle card at radius dist
            self.size[1] - radius - self.card_size[1] / 2,
        )

        self.logger.debug(f"{angles=}")
        rotated_surfs = [
            pygame.transform.rotate(
                pygame.transform.scale(card.graphics.surface, self.card_size),
                -angle,
            )
            for card, angle in zip(self.cardset, angles)
        ]
        # Position the cards with their offset from the center
        card_positions = [
            (
                center_pos[0]
                + sin(math.radians(a)) * (radius)
                - (card_surf.get_size()[0] / 2),
                # Reverse the position in the y axis
                self.size[1]
                - center_pos[1]
                - cos(math.radians(a))
                * (
                    radius
                    - sqrt(
                        (card_surf.get_size()[0] / 2) ** 2
                        + (card_surf.get_size()[1] / 2) ** 2
                    )
                )
                - card_surf.get_size()[1],
            )
            for a, card_surf in zip(angles, rotated_surfs)
        ]
        self.logger.debug(f"{card_positions=}")

        for card_surf, card_pos in zip(rotated_surfs, card_positions):

            surf.blit(
                card_surf,
                card_pos,
            )

        self._radius = radius
        self._center_pos = center_pos
        self._card_diagonal = card_diagonal
        self._angles = angles

        return surf

    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard | None:
        # We think pos1 from bottom instead of top
        if (
            pos[0] < 0
            or pos[1] < 0
            or pos[0] > self.size[0]
            or pos[1] > self.size[1]
        ):
            self.logger.debug(f"{pos=} ut of bound")
            return None

        pos = (pos[0], self.size[1] - pos[1])
        self.logger.debug(f"Converted {pos=}")
        self.logger.debug(f"Center {self._center_pos=}")

        dist_to_center = sqrt(
            (pos[0] - self._center_pos[0]) ** 2
            + (pos[1] - self._center_pos[1]) ** 2
        )
        self.logger.debug(f"{dist_to_center=}")
        if (
            dist_to_center > self._radius + self._card_diagonal / 2
            or dist_to_center < self._radius - self._card_diagonal / 2
        ):
            self.logger.debug(f"{pos=} is not in radius range")
            return None

        for card, angle in zip(reversed(self.cardset), reversed(self._angles)):
            # Reverse because cards at the end are over the previous
            self.logger.debug(f"Check {card=} with {angle=}")
            card_center = (
                (
                    self._center_pos[0]
                    + sin(math.radians(angle)) * self._radius
                ),
                (
                    self._center_pos[1]
                    + cos(math.radians(angle)) * self._radius
                ),
            )
            dist_to_card_center = sqrt(
                (pos[0] - card_center[0]) ** 2 + (pos[1] - card_center[1]) ** 2
            )
            # Cosine theorem to find angle (center, card, pos)
            # {\displaystyle a^{2}=c^{2}+b^{2}-2bc\cos \alpha }.
            a = math.acos(
                (
                    dist_to_center**2
                    - dist_to_card_center**2
                    - self._radius**2
                )
                / (-2 * dist_to_card_center * self._radius)
            )
            # Distance to the line from the center to the center of the card
            dist_to_line = sin(a) * dist_to_card_center
            self.logger.debug(f"Calculated {dist_to_line=}")
            if dist_to_line < self.card_size[0] / 2:
                return card
        return None


@dataclass
class PlayingHand(BaseHand):
    """A representation of the hand of the player.

    This will show the cards how the player wants it.

    Currently only works with size and card_size being specified.
    TODO: optimize by caching the variables.
    """

    @abstractmethod
    def hovered(self, card: AbstractCard) -> pygame.Surface:
        """Show the hand with the card hovered."""

    @abstractmethod
    def with_going_to_play(self, card: AbstractCard) -> pygame.Surface:
        """Show the hand with the card that is going to be played.

        This can be used for asking a confimation to the user,
        or for aking a way to play the card.
        """


if __name__ == "__main__":

    # This will visualize the cards

    import sys
    import pygame
    from pygame_cards.classics import CardSets as ClassicCardSet

    logging.basicConfig()

    pygame.init()

    size = width, height = 1500, 700

    screen = pygame.display.set_mode(size)

    card_set = CardsSet(ClassicCardSet.n52[:4])

    graphics_aligned = AlignedHand(card_set)
    graphics_aligned_overlap = AlignedHand(card_set, offset_position=-29)
    graphics_rounded = RoundedHand(card_set + card_set + card_set)
    graphics_rounded2 = RoundedHand(card_set + card_set)

    graphics_aligned.logger.setLevel(logging.DEBUG)
    graphics_aligned_overlap.logger.setLevel(logging.DEBUG)
    graphics_rounded.logger.setLevel(logging.DEBUG)
    graphics_rounded2.logger.setLevel(logging.DEBUG)

    screen.blit(graphics_aligned.surface, (200, 0))
    screen.blit(graphics_aligned_overlap.surface, (200, 200))
    screen.blit(graphics_rounded.surface, (200, 400))
    screen.blit(graphics_rounded2.surface, (200, 750))

    pygame.display.flip()

    while 1:
        pos = pygame.mouse.get_pos()
        hoverd_card = graphics_aligned.get_card_at((pos[0] - 200, pos[1] - 0))
        screen.blit(
            graphics_aligned.with_hovered(hoverd_card, fill_inside=False),
            (200, 0),
        )
        pygame.display.update()
        sleep(1)
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()
