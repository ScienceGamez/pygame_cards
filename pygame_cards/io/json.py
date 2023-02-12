from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Type
from pygame_cards.abstract import AbstractCard

from pygame_cards.set import CardsSet


# io methods


def from_json(file: Path, card_type: Type = AbstractCard) -> CardsSet:
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
            player_counts: list[int] = card_dict.pop("add_card_at_playercount", [1])
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
        [card_type(**card_dict, **global_kwargs) for card_dict in cards_list]
    )


def from_jsons(
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
                "Impossible to specifiy 'card_types' as list and 'files' as Path"
            )
        # Find all the json files in the given pattern
        files = [f for f in Path(files).rglob("*.json")]
    if not isinstance(card_types, list):
        card_types = [card_types for _ in files]

    return CardsSet.join(
        *[from_json(file, card_type) for file, card_type in zip(files, card_types)]
    )
