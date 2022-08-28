from __future__ import annotations
from dataclasses import dataclass, field
import logging
import threading
from typing import TYPE_CHECKING, Type
import pygame


if TYPE_CHECKING:
    from pygame_cards.set import CardsSet


_CARDS_COUNTER = 0
_COUNTER_LOCK = threading.Lock()


@dataclass
class AbstractCard:
    """The minimum required for a class.

    When inheriting from this class, use the decorator:
    @dataclass(eq=False)
    such that you can inherit from the hash method, which is safely
    handled by the u_id attribute.

    :attr name: The name of the card
    :attr u_id: A unique identifier for each card. Cards can be in
        two similar exemplar, but will have different u_ids.
    """

    name: str

    u_id: int = field(init=False)
    logger: logging.Logger = field(init=False)

    graphics_type: Type[AbstractCardGraphics] = field(
        init=False, compare=False
    )
    _graphics: AbstractCardGraphics = field(init=False, compare=False)

    def __post_init__(self):
        # Get a thread safe unique ID for that card
        with _COUNTER_LOCK:
            global _CARDS_COUNTER
            self.u_id = _CARDS_COUNTER
            _CARDS_COUNTER += 1
        self.logger = logging.getLogger(
            f"pywonders.cards.{type(self).__name__}"
        )

    def __repr__(self) -> str:
        return f"Card({self.name})"

    def __hash__(self) -> int:
        return self.u_id

    @property
    def graphics(self) -> AbstractCardGraphics:
        """The graphics for the card."""
        if not hasattr(self, "_graphics"):
            if not hasattr(self, "graphics_type"):
                raise RuntimeError(
                    f"Cannot show graphics of {self}, "
                    "because not graphics_type was specified. "
                    f"Either set {self}.graphics or assign a default "
                    "'graphics_type' class."
                )
            else:
                self._graphics = self.graphics_type(self)

        return self._graphics

    @graphics.setter
    def graphics(self, graphics: AbstractCardGraphics):
        """Set the graphics for that card."""
        self._graphics = graphics

    def n_exemplar_in_set(self, set: CardsSet) -> int:
        """Check how many time a card is in a set."""
        test_set = [c for c in set if c.name == self.name]
        return len(test_set)


class AbstractGraphic:
    """An abstract class for all the graphics used in the game.

    :attr surface: The :py:class:`pygame.Surface`
        corresponding to the current graphic.

    """

    surface: pygame.Surface
    logger: logging.Logger

    def __init_subclass__(cls) -> None:
        # Assing a logger
        cls.logger = logging.getLogger(f"pywonders.graphics.{cls.__name__}")

    def clear_cache(self) -> None:
        """Clear the cache of this graphics.

        Usually you don't want to draw the same thing every time you
        will render a surface, so you will cache the surfaces.
        But sometimes the graphic will change and you will need to clear
        the cache of it.
        """

        # Remove the surface cache_property if exists
        self.__dict__.pop("surface", None)


@dataclass
class AbstractCardGraphics(AbstractGraphic):
    """A base representation for what the card should look like."""

    card: AbstractCard
    size: tuple[int, int] = 230, 350

    @property
    def surface(self) -> pygame.Surface:
        """The surface of the card."""

        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        rad = int(0.1 * min(*self.size))
        pygame.draw.rect(surf, "white", (0, 0, *self.size), 0, rad)

        return surf
