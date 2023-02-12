from __future__ import annotations
from abc import abstractproperty
from dataclasses import dataclass, field
import logging
import threading
from typing import TYPE_CHECKING, Type
import pygame
from pygame_cards import constants


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

    :param name: The name of the card
    :param u_id: A unique identifier for each card. Cards can be in
        two similar exemplar, but will have different u_ids.
    :param graphics_type: The type of graphics we want to use.
    :param logger: A :py:class:`logging.Logger` object.
        Useful for debugging purposes.

    """

    name: str

    u_id: int = field(init=False)
    logger: logging.Logger = field(init=False, repr=False)

    graphics_type: Type[AbstractCardGraphics] = field(
        init=False,
        compare=False,
        repr=False,
    )
    _graphics: AbstractCardGraphics = field(init=False, compare=False, repr=False)

    def __post_init__(self):
        # Get a thread safe unique ID for that card
        with _COUNTER_LOCK:
            global _CARDS_COUNTER
            self.u_id = _CARDS_COUNTER
            _CARDS_COUNTER += 1
        self.logger = logging.getLogger(f"pywonders.cards.{type(self).__name__}")

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

    The graphic is showed using the surface property, which is a pygame.Surface
    object.
    The size of the suface is also determined by the size property.
    The suface should always be rendered for the desired size.
    This helps showing cards well on screen with different sizes.

    In case one need graphics of different sizes for the same object the best
    is to create
    two instances of graphics for the same object for performance reasons
    (not having to recreate the surface every time).

    :param surface: The :py:class:`pygame.Surface` corresponding to the current graphic.
        This attribute must be implemented as a `cached property`.
        Whe the size of the graphic is changed, the cached surface is
        deleted and a new one is created.
    :param size: The size of the graphic.
        If you change that attribute, the surface will be recreated.
    :param logger: The logger for this class. Useful for debugging.

    """

    surface: pygame.Surface
    logger: logging.Logger
    size: tuple[int, int]

    def __init_subclass__(cls) -> None:
        # Assing a logger
        cls.logger = logging.getLogger(f"pygame_cards.graphics.{cls.__name__}")

    def clear_cache(self) -> None:
        """Clear the cache of this graphics.

        Usually you don't want to draw the same thing every time you
        will render a surface, so you will cache the surfaces.
        But sometimes the graphic will change and you will need to clear
        the cache of it.
        """

        # Remove the surface cache_property if exists
        self.__dict__.pop("surface", None)

    @abstractproperty
    def surface(self) -> pygame.Surface:
        raise NotImplementedError(
            f"'surface' is not implemented for {type(self).__name__}. Please use"
            " the @cached_property decorator."
        )

    @property
    def size(self) -> tuple[int, int]:
        return self._size

    @size.setter
    def size(self, size: tuple[int, int]) -> None:
        """Set the size of the graphic.

        :param size: The size of the graphic.
        """
        if size == self._size:
            return
        self._size = size
        self.clear_cache()


@dataclass
class AbstractCardGraphics(AbstractGraphic):
    """A base representation for what a card should look like."""

    card: AbstractCard
    size: tuple[int, int] = constants.CARD_SIZE

    @property
    def surface(self) -> pygame.Surface:
        """The surface of the card."""

        surf = pygame.Surface(self.size, pygame.SRCALPHA)

        rad = int(0.1 * min(*self.size))
        pygame.draw.rect(surf, "white", (0, 0, *self.size), 0, rad)

        return surf


class Manager:
    """Abstract class for cards manager."""

    logger: logging.Logger

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"pygame_cards.manager.{type(self).__name__}")
