import json
import logging
from pathlib import Path
from types import NoneType
from typing import Any, Type
from pygame_cards.abstract import AbstractCard


_logger = logging.getLogger("pygame_cards.io.json")


def key_to_json(key: Any) -> Any:
    _logger.debug(f"key_to_json: Converting {key}")
    try:
        key = str(key)
        return key
    except Exception as e:
        raise TypeError(
            "Could not convert {key} to a str for being a json valid key."
        )


def item_to_json(item: Any) -> Any:
    """Convert an item to a json."""
    _logger.debug(f"item_to_json: Converting type {type(item)} ")
    _logger.debug(f"item_to_json: Converting {item} ")
    if isinstance(item, (int, str, float, bool, NoneType)):
        json_item = item
    elif isinstance(item, dict):
        json_item = dic_to_json(item)
    elif isinstance(item, list):
        json_item = list_to_json(item)
    elif isinstance(item, AbstractCard):
        json_item = dic_to_json(item.__dict__)
        json_item.pop("u_id")  # Remove the id as will not be used in json
    elif isinstance(item, logging.Logger):
        json_item = None
    elif hasattr(item, "__dict__"):
        _logger.debug(
            f"item_to_json: Found __dict__, now try converting {item} "
        )
        json_item = dic_to_json(item.__dict__)
    else:
        _logger.exception(f"No conversion defined for object {item}")
        json_item = None
    _logger.debug(f"item_to_json: converted {item} to {json_item}")

    return json_item


def dic_to_json(dic: dict) -> dict:
    """Convert a dictionary to another python dictionary.

    Recursively calls this function if the object is not jsonable.
    """
    return {
        key_to_json(key): item_to_json(item)
        for key, item in dic.items()
        if not str(key).startswith("_")
        and not str(item).startswith("_")
        and item_to_json(item) is not None
        and key is not None
    }


def list_to_json(l) -> list:
    """Same as :py:func:`dic_to_json` but for lists."""
    return [item_to_json(item) for item in l if item is not None]


def to_json(object: Any):
    """Convert an object to a dictionary."""

    return item_to_json(object)


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


if __name__ == "__main__":
    from pygame_cards.abstract import AbstractCard
    from pygame_cards.set import CardsSet

    _logger.setLevel(logging.DEBUG)
    _logger.handlers.append(logging.StreamHandler())
    obj = AbstractCard("a")
    obj = CardsSet([AbstractCard("a"), AbstractCard("b"), AbstractCard("b")])
    print(obj)
    print(obj.__dict__)
    print(to_json(obj))
