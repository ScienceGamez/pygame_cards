#!/usr/bin/env python

import argparse
import asyncio
import itertools
import json
import logging
import threading
import websockets
from pygame_cards.server.player import Player
import logging

logger = logging.getLogger("websockets")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


CLIENT_ID_COUNTER = itertools.count()
CLIENT_ID_LOCK = threading.Lock()


class ClientManager:
    clients: list

    players: list[Player]

    def __init__(self) -> None:
        self.websockets = []

    async def manage_communication(self, websocket):
        print("managing2")
        async for message in websocket:
            print(message)
            try:
                message_dict = json.loads(message)
            except:
                logging.error(f"{message=}")
                message_dict = {}

            match message_dict:
                case {"event": "join_game_request", "player_name": _}:
                    response = {}

                    with CLIENT_ID_LOCK:
                        response["player_id"] = next(CLIENT_ID_COUNTER)

                    response["default_cards_set"] = "n52"
                    # send the response
                    await websocket.send(json.dumps(response))
                case {"event": "join_game_request"}:
                    response = {"error:event": "join_game_request"}
                    # send the response
                    await websocket.send(json.dumps(response))
                case {"event": "player_ready"}:
                    websockets.broadcast(self.websockets, f"Client joined {websocket}")
                    self.websockets.append(websocket)
                case _:
                    logging.error(f"{message_dict}")

    async def listen_commands(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("command")
        while True:
            text = input("Enter Command: ")
            args = parser.parse_args(text.split(" "))
            print("received", args)
            print("command", args.command)
            match args.command:
                case "hello":
                    await asyncio.gather(
                        *[websocket.send("hello") for websocket in self.websockets]
                    )
                case "exit":
                    return


clients_manager = ClientManager()


async def manage_communication():
    print("managing")
    async with websockets.serve(
        clients_manager.manage_communication, "localhost", 8765
    ):
        await asyncio.Future()  # run forever
    print("managed")


def start_server():
    asyncio.run(manage_communication())


communication_thread = threading.Thread(target=start_server)
communication_thread.start()


asyncio.run(clients_manager.listen_commands())
