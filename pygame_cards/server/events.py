from datetime import datetime
from json import JSONEncoder
from typing import Any
import pygame

from pygame_cards.defaults import DefaultCardsSet


CARD_PLAYED = pygame.event.custom_type()


# subclass JSONEncoder
class PygameEventsEncoder(JSONEncoder):
    def default(self, o: pygame.event.Event | Any):
        match o:
            case pygame.event.EventType():
                return {"_type_PygameEventsEncoder": o.type} | o.__dict__
            case datetime():
                return str(o)
            case DefaultCardsSet():
                return o.name

            case _:
                return JSONEncoder.default(self, o)
