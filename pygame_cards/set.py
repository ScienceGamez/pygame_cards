from __future__ import annotations
import itertools
import json
import logging
from pathlib import Path
import random
from typing import Type
from pygame_cards.abstract import AbstractCard
from pywonders.io.json import to_json


class CardsSet(list[AbstractCard]):
    """A list of cards.

    This class inherit diretly from the python list.
    This implies that any method from lists can be used.
    """

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
            [
                card
                for card in self
                if card.add_card_at_playercount <= n_players
            ]
        )

    def draw(self, n_cards: int) -> CardsSet:
        """Draw the n first cards from the set.

        To draw the first card of the set you can use the :py:meth:`pop(0)`.
        """
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

        if (
            not equally
            and not n_cards
            and (remaining_cards := (len(self) % n_sets))
        ):
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
    @classmethod
    def from_json(cls, file: Path, card_type: Type = AbstractCard) -> CardsSet:
        """Create a CardsSet from a given file and a type of card.

        You can set shared attribute to all the cards in the file, by
        having the first json being a card with no name.
        Otherwise, it is mandatory to give names to the cards.

        :arg file: The path to the json file.
        :arg card_type: The Class that should be used for the CardsSet
        """
        file = Path(file)

        with file.open("r") as f:
            cards_list: list[dict] = json.load(f)

        global_kwargs = (
            # First element used as global parameters
            {}
            if "name" in cards_list[0].keys()
            else cards_list.pop(0)
        )

        additional_cards_dicts = []
        for card_dict in cards_list:
            # Find at which number of player the card should be added
            if "add_card_at_playercount" in card_dict.keys():

                player_counts: list[int] = card_dict.pop(
                    "add_card_at_playercount", [1]
                )
                if isinstance(player_counts, list):
                    # Make a Mik mack to correctly add the cards
                    card_dict["add_card_at_playercount"] = player_counts[0]
                    for count in player_counts[1:]:
                        new_dict = card_dict.copy()
                        new_dict["add_card_at_playercount"] = count
                        additional_cards_dicts.append(new_dict)
        # Add the additional cards to the list
        cards_list += additional_cards_dicts
        return CardsSet(
            [
                card_type(**card_dict, **global_kwargs)
                for card_dict in cards_list
            ]
        )

    @classmethod
    def from_jsons(
        cls,
        files: list[Path] | Path,
        card_types: list[Type] | Type = AbstractCard,
    ):
        """Load cards from different files.

        Same as :py:method:`from_json` but with mutlitple files.
        :arg files: The list of path to load. If a single path is given,
            will try to read all the json files.
        """
        if not isinstance(files, list):
            logging.getLogger("pygame_cards.from_jsons").debug(
                f"Received a single file {files}"
            )
            if isinstance(card_types, list):
                raise TypeError(
                    "Impossible to specifiy "
                    "'card_types' as list and 'files' as Path"
                )
            # Find all the json files in the given pattern
            files = [f for f in Path(files).rglob("*.json")]
        if not isinstance(card_types, list):
            card_types = [card_types for _ in files]

        return CardsSet.join(
            *[
                CardsSet.from_json(file, card_type)
                for file, card_type in zip(files, card_types)
            ]
        )

    def to_json(self, file: Path) -> None:
        """Save the cards set as a json file."""

        file = Path(file)

        with file.open("w+") as f:
            json.dump(to_json(self), f)
