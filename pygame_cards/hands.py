from enum import auto
from functools import cached_property
import logging
from math import cos, sin, sqrt
import math

import pygame

from pygame_cards.abstract import AbstractCard
from pygame_cards.utils import AutoName
from pygame_cards.effects import outer_halo
from pygame_cards.set import CardsSet, CardsetGraphic
from pygame_cards import constants


class CardOverlap(AutoName):
    """How card overlap in the hand."""

    left = auto()
    right = auto()


class BaseHand(CardsetGraphic):
    """A base class for a hand.

    Usually in a hand the cards are shown on next to the other.

    :param overlap_hide: The card to hide if to cards are one
        over each other. By default the card overlap on the right,
        which is the standard in card games.
        This also implies that the cards are located at the opposite side
        of their overlap.


    """

    def __init__(
        self,
        *args,
        overlap_hide: CardOverlap = CardOverlap.right,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.overlap_hide = overlap_hide


class AlignedHand(BaseHand):
    """A hand of card with all the cards aligned.

    :param card_spacing: The offset proportion of the position between the cards.

        * 0, means the cards are directly next to each other.
        * Positive offset, means the card will be further
            away from each other.
        * Negative, means cards will be closer
            to each other.

    """

    def __init__(
        self,
        *args,
        card_spacing: float = constants.COLUMN_SPACING,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.card_spacing = card_spacing

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
        offset = self.card_spacing * self.card_size[0]
        total_x = (
            len(self.cardset) * self.card_size[0] + (len(self.cardset) - 1) * offset
        )

        if total_x > self.size[0]:
            self.logger.warning("Too many cards for hands size, rescaling will apply.")
            offset = (self.size[0] - len(self.cardset) * self.card_size[0]) / (
                len(self.cardset) - 1
            )
        x_positions = [
            i * self.card_size[0] + i * offset for i in range(len(self.cardset))
        ]
        # Revert the position in case of another overlap
        x_positions = [
            (
                x_pos
                if self.overlap_hide == CardOverlap.right
                else self.size[0] - self.card_size[0] - x_pos
            )
            for x_pos in x_positions
        ]
        self.logger.debug(f"{x_positions=}")

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
        highlighted_surf = outer_halo(card.graphics.surface, radius=radius, **kwargs)
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
        s = self.surface.get_size()
        if not (pos[0] < s[0] and pos[1] < s[1]):
            self.logger.error(f"get_card_at({pos=}) not in {s}.")
            return None

        x_positions, offset = self.calculate_x_positions()
        self.logger.debug(f"get_card_at({pos=}): {x_positions=}, {self.overlap_hide=}")

        # TODO: make this work
        for card_index, x_pos in enumerate(x_positions):
            if pos[0] < x_pos or pos[0] > x_pos + self.card_size[0]:
                self.logger.debug(
                    f"get_card_at({pos=}):: {card_index=} is not Between the card"
                    " boundaries"
                )
                continue
            if (
                self.overlap_hide == CardOverlap.right
                # Check that is not under the next card
                and pos[0] - x_pos
                > self.card_size[0] + self.card_spacing * self.card_size[0]
            ) or (
                self.overlap_hide == CardOverlap.left
                and pos[0] - x_pos < self.card_spacing * self.card_size[0]
            ):
                self.logger.debug(
                    f"get_card_at({pos=}):: {card_index=} is  going to be under the"
                    " next card"
                )
                continue
            if x_pos - pos[0] > self.card_size[0] + offset:
                self.logger.debug(f"get_card_at({pos=}): is in offset.")
                continue  # Between two cards, in the offset

            self.logger.debug(f"get_card_at({pos=}): found index {card_index}.")
            return self.cardset[card_index]

        return None

    def get_card_positions(self) -> dict[AbstractCard, tuple[int, int]]:
        y = self.calculate_y_position()
        xs, _ = self.calculate_x_positions()

        return {card: (x, y) for card, x in zip(self.cardset, xs)}


class RoundedHand(BaseHand):
    """A hand of card with all the cards aligned on an arc of a circle.

    This will produced an hand of card where cards are clipped insided
    the size of the hand.


    :param angle: The angle in which the cards are constrained
        (Unit: Degrees)
        If 0, the cards are all aligned.
        If not zero, the cards will be placed on an arc of a circle
        with the given angle.

    """

    def __init__(
        self,
        *args,
        angle: float = 90,
        **kwargs,
    ):
        if not "size" in kwargs:
            # Change the defualt size
            kwargs["size"] = (700, 400)

        super().__init__(*args, **kwargs)
        self.angle = angle

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
                -self.angle / 2 + i * angle_step for i in range(len(self.cardset))
            ]
        # Radius of the circle around the cards (from center to card centers)
        # Trust me, I am an engineer
        card_diagonal = sqrt(self.card_size[0] ** 2 + self.card_size[1] ** 2)
        radius = min(
            # Constraint for width
            (self.size[0] - card_diagonal) / 2 / sin(math.radians(self.angle / 2)),
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
        if pos[0] < 0 or pos[1] < 0 or pos[0] > self.size[0] or pos[1] > self.size[1]:
            self.logger.debug(f"{pos=} ut of bound")
            return None

        pos = (pos[0], self.size[1] - pos[1])
        self.logger.debug(f"Converted {pos=}")
        self.logger.debug(f"Center {self._center_pos=}")

        dist_to_center = sqrt(
            (pos[0] - self._center_pos[0]) ** 2 + (pos[1] - self._center_pos[1]) ** 2
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
                (self._center_pos[0] + sin(math.radians(angle)) * self._radius),
                (self._center_pos[1] + cos(math.radians(angle)) * self._radius),
            )
            dist_to_card_center = sqrt(
                (pos[0] - card_center[0]) ** 2 + (pos[1] - card_center[1]) ** 2
            )
            # Cosine theorem to find angle (center, card, pos)
            # {\displaystyle a^{2}=c^{2}+b^{2}-2bc\cos \alpha }.
            a = math.acos(
                (dist_to_center**2 - dist_to_card_center**2 - self._radius**2)
                / (-2 * dist_to_card_center * self._radius)
            )
            # Distance to the line from the center to the center of the card
            dist_to_line = sin(a) * dist_to_card_center
            self.logger.debug(f"Calculated {dist_to_line=}")
            if dist_to_line < self.card_size[0] / 2:
                return card
        return None

    def get_card_positions(self) -> dict[AbstractCard, tuple[int, int]]:
        # use aligned hand as a proxy
        self.card_spacing = constants.COLUMN_SPACING
        y = AlignedHand.calculate_y_position(self)
        xs, _ = AlignedHand.calculate_x_positions(self)

        self.logger.warning(
            f"'get_card_positions' is not perfectly correct implemented yet"
        )

        return {card: (x, y) for card, x in zip(self.cardset, xs)}


class Pile(CardsetGraphic):
    """A pile has only its last/s card/s that can be selected.

    :param rel_offset: The offset between cards. Relative to the card size.

    """

    def __init__(
        self,
        *args,
        rel_offset: float = 0.2,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.rel_offset = rel_offset

    def _get_card_index_at(self, pos: tuple[int, int]) -> int | None:
        """Return the index of the card located at the current position."""
        raise NotImplementedError(f"Must implement in {type(self).__name__}")

    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard | None:
        idx = self._get_card_index_at(pos)

        return None if idx is None else self.cardset[idx]

    def get_cards_at(self, pos: tuple[int, int]) -> CardsSet | None:
        """Return the card set at the given pixel position

        :arg pos: The position inside the CardsetGraphic surface.
        """
        idx = self._get_card_index_at(pos)

        return None if idx is None else self.cardset[idx:]


class VerticalPileGraphic(Pile):
    """Show a column in cards aligned.

    Cards are shown from first one to the last one on the bottom.

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        if not "size" in kwargs:
            # Change the defualt size
            kwargs["size"] = (175, 400)

        super().__init__(*args, **kwargs)

    def clear_cache(self) -> None:
        # Remove the surface cache_property if exists
        self.__dict__.pop("y_positions", None)
        super().clear_cache()

    @property
    def size(self) -> tuple[int, int]:
        return super().size

    @size.setter
    def size(self, size: tuple[int, int]) -> None:
        super(VerticalPileGraphic, VerticalPileGraphic).size.__set__(self, size)
        # Cards are too large for the new pile size
        if self.card_size[0] > self.size[0]:
            width = self.size[0]
            # Keep the same ratio
            height = width / self.card_size[0] * self.card_size[1]

            self.card_size = (width, height)
            self.logger.debug(f"setting card size to {self.card_size=}")

    @cached_property
    def surface(self) -> pygame.Surface:
        # Create the surface
        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        # Calculate how we position the cards
        n_cards = len(self.cardset)
        if n_cards == 0:
            return surf

        self.logger.debug(f"{self.size=}, {self.card_size=}")

        x_position = (self.size[0] - self.card_size[0]) / 2

        # Add the cards on the surface
        surf.blits(
            [
                (card.graphics.surface, (x_position, y))
                for card, y in zip(self.cardset, self.y_positions)
            ],
        )

        return surf

    @cached_property
    def y_positions(self) -> list[int]:
        n_cards = len(self.cardset)
        max_offset = self.rel_offset * self.card_size[1]

        expected_h = n_cards * max_offset + self.card_size[1]
        h_space = (
            (self.size[1] - self.card_size[1]) / n_cards
            if expected_h > self.size[1]
            else max_offset
        )
        return [i * h_space for i in range(n_cards)]

    def _get_card_index_at(self, pos: tuple[int, int]) -> int | None:
        """Return the index of the card located at the current position."""
        if not self.cardset:
            # No cards case
            return None
        # Iterate over the cards and position to find the correct card

        for card_idx in range(len(self.cardset)):
            if pos[1] < self.y_positions[card_idx]:
                return card_idx - 1
        if pos[1] < self.y_positions[-1] + self.card_size[1]:
            # Last card is on top
            return len(self.cardset) - 1
        return None

    def get_card_positions(self) -> dict[AbstractCard, tuple[int, int]]:
        x_position = (self.size[0] - self.card_size[0]) / 2

        return {
            card: (x_position, y) for card, y in zip(self.cardset, self.y_positions)
        }


class HorizontalPileGraphic(Pile):
    """Show a cards horizontally aligned.

    Cards are shown from first one to the last one on the bottom.

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        if not "size" in kwargs:
            # Change the defualt size
            kwargs["size"] = (350, 240)

        super().__init__(*args, **kwargs)

    def clear_cache(self) -> None:
        # Remove the surface cache_property if exists
        self.__dict__.pop("x_positions", None)
        super().clear_cache()

    @cached_property
    def surface(self) -> pygame.Surface:
        # Create the surface
        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        # Calculate how we position the cards
        n_cards = len(self.cardset)
        if n_cards == 0:
            return surf

        y_position = (self.size[1] - self.card_size[1]) / 2

        # Add the cards on the surface
        surf.blits(
            [
                (card.graphics.surface, (x, y_position))
                for card, x in zip(self.cardset, self.x_positions)
            ],
        )

        return surf

    @cached_property
    def x_positions(self) -> list[int]:
        n_cards = len(self.cardset)
        # Get the offset between cards in pixels
        offset = self.rel_offset * self.card_size[0]

        expected_h = n_cards * offset + self.card_size[0]
        h_space = (
            (self.size[0] - self.card_size[0]) / n_cards
            if expected_h > self.size[0]
            else offset
        )
        return [i * h_space for i in range(n_cards)]

    def _get_card_index_at(self, pos: tuple[int, int]) -> int | None:
        """Return the index of the card located at the current position."""
        if not self.cardset:
            # No cards case
            return None
        # Iterate over the cards and position to find the correct card

        for card_idx in range(len(self.cardset)):
            if pos[0] < self.x_positions[card_idx]:
                return card_idx - 1
        if pos[0] < self.x_positions[-1] + self.card_size[0]:
            # Last card is on top
            return len(self.cardset) - 1
        return None

    def get_card_positions(self) -> dict[AbstractCard, tuple[int, int]]:
        y_position = (self.size[1] - self.card_size[1]) / 2

        return {
            card: (x, y_position) for card, x in zip(self.cardset, self.x_positions)
        }


if __name__ == "__main__":
    # This will visualize the cards

    import sys
    import pygame
    from pygame_cards.classics import CardSets as ClassicCardSet

    logging.basicConfig()

    pygame.init()

    size = width, height = 1500, 1200

    screen = pygame.display.set_mode(size)

    card_set = CardsSet(ClassicCardSet.n52[:4])

    graphics_aligned = AlignedHand(card_set)
    graphics_aligned_overlap = AlignedHand(card_set, card_spacing=-0.15)
    graphics_rounded = RoundedHand(card_set + card_set + card_set)
    graphics_rounded2 = RoundedHand(card_set + card_set)

    # graphics_aligned.logger.setLevel(logging.DEBUG)
    graphics_aligned_overlap.logger.setLevel(logging.DEBUG)
    # graphics_rounded.logger.setLevel(logging.DEBUG)
    # graphics_rounded2.logger.setLevel(logging.DEBUG)

    screen.blit(graphics_aligned.surface, (200, 0))
    screen.blit(graphics_aligned_overlap.surface, (200, 200))
    screen.blit(graphics_rounded.surface, (200, 400))
    screen.blit(graphics_rounded2.surface, (200, 750))

    pygame.display.flip()

    clock = pygame.time.Clock()
    fps = 4

    while 1:
        pos = pygame.mouse.get_pos()
        hoverd_card = graphics_aligned.get_card_at((pos[0] - 200, pos[1] - 0))
        screen.blit(
            graphics_aligned.with_hovered(hoverd_card, fill_inside=True),
            (200, 0),
        )
        pygame.display.update()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
