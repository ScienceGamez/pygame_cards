from __future__ import annotations
from functools import cached_property
import itertools
import json
import logging
from pathlib import Path
import random
from typing import Type
from abc import abstractmethod, abstractproperty

import pygame
from pygame_cards.abstract import AbstractCard, AbstractGraphic
from pygame_cards.io.utils import to_json
from pygame_cards import constants

_CARDSET_ID_GENERATOR = itertools.count()


class CardsetGraphic(AbstractGraphic):
    """A base graphic for any card holder.

    This will show a card set on the screen.
    You should implement the :meth:`surface`.

    :param cardset: The set of card that is shown.
    :param size: A tuple with the size of the requested card in this graphic.
    :param card_size: A tuple with the size of the cards in this graphic.
    :param card_border_radius: The radius of the cards in this card set.
    :param max_cards: The max number of card that can be contained in this
        graphic. If 0, this is unlimited.
    """

    def __init__(
        self,
        cardset: CardsSet,
        size: tuple[int, int] = constants.CARDSET_SIZE,
        card_size: tuple[int, int] = constants.CARD_SIZE,
        card_border_radius_ratio: float = constants.CARD_BORDER_RADIUS_RATIO,
        graphics_type: type | None = None,
        max_cards: int = 0,
    ):
        self.cardset = cardset
        self._size = size
        self.card_size = card_size
        self.card_border_radius_ratio = card_border_radius_ratio
        self.max_cards = max_cards
        self.graphics_type = graphics_type

        for card in self.cardset:
            # Enforce the type
            if graphics_type:
                card.graphics_type = graphics_type
            # Enforce the card size
            card.graphics.size = self.card_size
        self._raised_with_hovered_warning = False

    def clear_cache(self) -> None:
        super().clear_cache()
        for prop in ["card_border_radius"]:
            self.__dict__.pop(prop, None)

    @property
    def card_size(self) -> tuple[int, int]:
        return self._card_size

    @card_size.setter
    def card_size(self, size: tuple[int, int]) -> None:
        self._card_size = size
        # apply the change to all the cards
        for card in self.cardset:
            card.graphics.size = self.card_size

    @cached_property
    def card_border_radius(self) -> int:
        return int(self.card_size[0] * self.card_border_radius_ratio)

    @abstractproperty
    def surface(self) -> pygame.Surface:
        raise NotImplementedError(f"property 'surface' in {type(self).__name__}")

    @abstractmethod
    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard | None:
        """Return the card at the given pixel position

        :arg pos: The position inside the CardsetGraphic surface.
        """
        raise NotImplementedError(f"'get_card_at' in Class {type(self).__name__}")

    @abstractmethod
    def get_cards_at(self, pos: tuple[int, int]) -> CardsSet | None:
        """Return a cardset at the given pixel position.

        This can be implemented for allowing moving multiple cards.
        You will still have to implement :py:meth:`get_card_at`.
        You will also need to set :py:attr:`drag_multiple_cards`
        to True.
        in :py:class:`CarsetRights`. The :py:class:`CardsManager`
        will then use this method for selection.

        :arg pos: The position inside the CardsetGraphic surface.
        """
        raise NotImplementedError(f"'get_cards_at' in Class {type(self).__name__}")

    def remove_card(self, card: AbstractCard) -> None:
        """Remove a card from the cardset."""

        self.cardset.remove(card)
        self.clear_cache()

    def pop_card(self, card_index: int) -> AbstractCard:
        """Remove a card from the cardset.

        :arg card_index: The index at which the card we want to
            pop is.
        :return card_at_index: The card at the desired index.
        """

        card = self.cardset.pop(card_index)
        self.clear_cache()
        return card

    def remove_all_cards(self) -> CardsSet:
        """Remove all cards from the cardset.

        :return cards: A cardset with all the cards remaining.
        """
        cardset = CardsSet()
        while self.cardset:
            card = self.cardset.pop(0)
            cardset.append(card)
        self.clear_cache()
        return cardset

    def append_card(self, card: AbstractCard) -> None:
        """Append a card to the cardset."""

        self.cardset.append(card)
        card.graphics.size = self.card_size
        card.graphics.clear_cache()
        self.clear_cache()

    def extend_cards(self, card_set: CardsSet) -> None:
        self.cardset.extend(card_set)
        for card in card_set:
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

    def get_card_positions(self) -> dict[AbstractCard, tuple[int, int]]:
        """Return the position of each card from the cardset."""
        raise NotImplementedError(
            f"'get_card_positions' in Class {type(self).__name__}"
        )


class CardsSet(list[AbstractCard]):
    """A list of cards.

    This class inherit diretly from the python list.
    This implies that any method from lists can be used.
    It represent the card set at the code or API level.
    If is meant to be used together with
    :py:class:`~pygame_cards.abstract.AbstractCardGraphics`
    for the graphics.
    """

    _graphics: CardsetGraphic | None = None

    def __init__(self, *args: AbstractCard) -> None:
        super().__init__(*args)
        self.u_id = next(_CARDSET_ID_GENERATOR)

    def __hash__(self) -> int:
        return hash(f"cs_{self.u_id}")

    def __repr__(self) -> str:
        return f"{type(self)}({super().__repr__()})"

    # override the [] method with slicing
    def __getitem__(self, index: int | slice) -> AbstractCard:
        if isinstance(index, int):
            return super().__getitem__(index)
        elif isinstance(index, slice):
            return type(self)(super().__getitem__(index))
        else:
            raise TypeError(f"Invalid index type: {type(index)}")

    # creation methods
    @classmethod
    def generate(cls) -> CardsSet:
        """Generate a cards set.

        This will create the cards set from different parameters.
        You can override this method in daughter classes.
        """
        raise NotImplementedError(
            "Specific cards sets generation can be implemented by "
            f"inheriting from {cls}."
        )

    @classmethod
    def join(cls, *cards_sets: CardsSet) -> CardsSet:
        new_set = CardsSet()
        for s in cards_sets:
            new_set.extend(s)
        return new_set

    def check_cards(self) -> bool:
        """Check whether only cards are given in this."""
        for c in self:
            if not isinstance(c, AbstractCard):
                return False
        return True

    # lookup methods
    def find_by_name(self, name: str) -> AbstractCard | None:
        """Find the first card matchin the name in the set.

        :return: The card requested or None if no card was found.
        """
        for card in self:
            if card.name == name:
                return card
        return None

    # playtime methods
    def shuffle(self):
        """Shuffle the cards in the set in a random order."""
        random.shuffle(self)

    def filter_by_era(self, era: int) -> CardsSet:
        """Filter the cards corresponding to the requested era."""
        return CardsSet([card for card in self if card.era == era])

    def filter_for_n_players(self, n_players: int) -> CardsSet:
        """Keep only the cards for the requested number of players.

        Remove the cards that are not supposed to be used
        by the number of players.
        :return: A new card set that contain only the specifed cards.
        """
        return CardsSet(
            [card for card in self if card.add_card_at_playercount <= n_players]
        )

    def draw(self, n_cards: int) -> CardsSet:
        """Draw the n first cards from the set.

        To draw the first card of the set you can use the :py:meth:`pop(0)` .

        :arg n_cards: The number of cards to draw.
            If -1, will draw all the cards
        """
        if n_cards == -1:
            n_cards = len(self)
        return CardsSet([self.pop(0) for _ in range(n_cards)])

    def distribute(
        self,
        n_sets: int,
        n_cards: int | None = None,
        *,
        shuffle: bool = True,
        equally: bool = True,
    ) -> list[CardsSet]:
        """Distribute the set in n sets.

        The cards are removed from this CardsSet.

        :arg n_sets: The number of set that should be done
        :arg n_cards: The number of cards that should be given to
            each set. If not specified, will distribute all the possible
            cards.
        :arg shuffle: Whether to shuffle the cards before distributing.
        :arg equally: Whether each set should contain the exact same
            number of cards. This is useful only
            if `n_cards` is not specified and
            if the cards cannot be all distrubuted equally.
            If True,
            the extra cards will be dropped.
            If False,
            the `m` extra cards are distrubted to the `m` first sets.
        """
        if shuffle:
            self.shuffle()

        cards_per_set = self._find_ncards_per_set(n_sets, n_cards)

        dist = [
            # Remove the cards
            self.draw(cards_per_set)
            for _ in range(n_sets)
        ]

        if not equally and not n_cards and (remaining_cards := (len(self) % n_sets)):
            for i in range(remaining_cards):
                dist[i].append(self.pop(0))

        return dist

    def _find_ncards_per_set(self, n_sets: int, n_cards: int | None):
        """Find the number of cards that should be given to each set.

        This is based on the number of set and number of cards given.
        see :py:meth:`CardsSet.distribute`
        """
        cards_per_set = len(self) // n_sets
        if n_cards:
            # If the number of cards is given
            if n_cards > cards_per_set:
                raise ValueError(
                    f"Cannot distribute {n_cards} cards to {n_sets} sets"
                    f" when the only {len(self)} cards are available."
                )
            cards_per_set = n_cards
        return cards_per_set

    def distribute_to(
        self,
        other_sets: list[CardsSet],
        n_cards: int | None = None,
        *,
        equally: bool = True,
        shuffle: bool = False,
        n_cards_at_a_time: int = 1,
    ) -> None:
        """Distribute n_cards from this set to the other sets.

        Similar to :py:meth:`CardsSet.distribute`, but with additional
        feature that this can act as a cards packet where cards are
        distributed from the top, s.t. the order is preserved.

        Assume the first element of the list is the card at the top
        of the packet, so the first to be distributed.

        :arg other_sets: The number of set that should be done
        :arg n_cards: see :py:meth:`CardsSet.distribute`
        :arg equally: see :py:meth:`CardsSet.distribute`
        :arg shuffle: Whether to shuffle the cards before distributing.
            Note that the default in this function is False instead
            of True, as for :py:meth:`CardsSet.distribute`
        :arg n_cards_at_a_time: The number of cards that should be
            distributed at one time.
        """
        if shuffle:
            self.shuffle()

        n_sets = len(other_sets)
        cards_per_set = self._find_ncards_per_set(n_sets, n_cards)

        # Cycler over the different card sets
        cycler = itertools.cycle(other_sets)

        # Find how many distriubtions will be required
        n_distributions = cards_per_set * n_sets // n_cards_at_a_time

        # Loop acts like a real distribution
        for i in range(0, n_distributions):
            # Get the current player
            set_to_distribute = next(cycler)
            set_to_distribute.extend(
                # Remove n_cards_at_a_time cards from the top of the packet
                [self.pop(0) for _ in range(n_cards_at_a_time)]
            )

        if not equally and not n_cards:
            for _ in range(len(self)):
                set_to_distribute = next(cycler)
                set_to_distribute.append(self.pop(0))

        return None

    # io methods
    def to_json(self, file: Path) -> None:
        """Save the cards set as a json file."""

        file = Path(file)

        with file.open("w+") as f:
            json.dump(to_json(self), f)

    # Graphic methods
    @property
    def graphics(self) -> CardsetGraphic:
        if self._graphics is None:
            raise NotImplementedError(f"No graphics set for {self}")

        return self._graphics

    @graphics.setter
    def graphics(self, value: CardsetGraphic) -> None:
        self._graphics = value
