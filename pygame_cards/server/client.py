#!/usr/bin/env python

import asyncio
from datetime import datetime
import random
import threading
import websockets
import json
import pygame
from pygame_cards.server.events import CARD_PLAYED, PygameEventsEncoder
from pygame_cards.defaults import get_default_card_set
from pygame_cards.server.player import Player


import logging

logger = logging.getLogger("websockets")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


test_event = pygame.event.Event(
    CARD_PLAYED, {"card": "lotr", "datetime": datetime.now()}
)


class ClientPlayer(Player):
    async def join_game(self):
        async with websockets.connect("ws://localhost:8765") as websocket:
            self.websocket = websocket
            await websocket.send(
                json.dumps(
                    {
                        "event": "join_game_request",
                        "player_name": random.choice(["lol", "xd", "mdr"]),
                    }
                )
            )
            join_game_response = await websocket.recv()
            game_start_dict = json.loads(join_game_response)
            print(game_start_dict)
            if "default_cards_set" in game_start_dict:
                card_set = get_default_card_set(game_start_dict["default_cards_set"])
                print(card_set)
            await websocket.send(
                json.dumps(
                    {
                        "event": "player_ready",
                    }
                )
            )

            async for message in websocket:
                print(message)
        del self.websocket

    def send(self, message: str):
        asyncio.run(self.websocket.send(message))

    async def player_action(self): ...

    def start_game_loop(self):
        def join_game():
            asyncio.run(self.join_game())

        communication_thread = threading.Thread(target=join_game)
        communication_thread.start()

        while True:
            a = input("What to sent ?")
            self.send(a)


player = ClientPlayer()

player.start_game_loop()
