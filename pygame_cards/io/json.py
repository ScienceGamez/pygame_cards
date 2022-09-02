import logging
from types import NoneType
from typing import Any
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


def to_json(pywondersobject: Any):
    """Convert an object to a dictionary."""

    return item_to_json(pywondersobject)


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
