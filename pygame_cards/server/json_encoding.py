from datetime import datetime
from json import JSONEncoder, JSONDecoder
import json
import logging
from typing import Any
import pygame

from pygame_cards.defaults import DefaultCardsSet, get_default_card_set


CARD_PLAYED = pygame.event.custom_type()

# subclass JSONEncoder
class PygameEventsEncoder(JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("pygame_cards.PygameEventsEncoder")

    def encode(self, o: pygame.event.Event | Any) -> str:
        self.logger.debug(f"PygameEventsEncoder.default({o=})")
        match o:
            case pygame.event.EventType():
                o = {
                    "pgc": "event",
                    "type": o.type,
                    "__dict__": self.encode(o.__dict__),
                }
            case datetime():
                o = str(o)
            case DefaultCardsSet():
                o = {
                    "pgc": "DefaultCardsSet",
                    "name": o.name,
                }

            case _:
                pass
        return JSONEncoder.encode(self, o)


class PygameEventsDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("pygame_cards.PygameEventsDecoder")

    def decode(self, json_str: str) -> pygame.event.Event | Any:
        self.logger.debug(f"PygameEventsDecoder.default({json_str=})")

        decoded = JSONDecoder.decode(self, json_str)
        if not (isinstance(decoded, dict) and "pgc" in decoded):
            return decoded

        match decoded["pgc"]:
            case "event":
                return pygame.event.Event(
                    decoded["type"], self.decode(decoded["__dict__"])
                )
            case "DefaultCardsSet":
                return get_default_card_set(decoded["name"])
            case _:
                pass


if __name__ == "__main__":
    from pygame_cards.classics import CardSets

    # logging.basicConfig(level=logging.DEBUG)

    e = pygame.event.Event(CARD_PLAYED, {"card": "Ace of Spades"})

    e_encoded = json.dumps(e, cls=PygameEventsEncoder)
    print(e_encoded)
    print(json.loads(e_encoded, cls=PygameEventsDecoder))

    cs_encoded = json.dumps(CardSets.n52, cls=PygameEventsEncoder)
    print(cs_encoded)
    print(json.loads(cs_encoded, cls=PygameEventsDecoder))
