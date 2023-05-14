"""Small sevrer for rock paper scisors game.

The server is based on websockets.

The available events are:
- join a new game: {"type": "init",}
- join an existing game: {"type": "init", "join": "<join_key>"}
- play a move: {"type": "play", "event": "<move>"}

"""

#!/usr/bin/env python

import asyncio
import json
from typing import Any
import websockets
import secrets
from websockets.server import serve, WebSocketServerProtocol

from content import RockPaperScissors, Player

JOIN: dict[str, tuple[RockPaperScissors, set[Any]]] = {}
WATCH = {}


async def error(websocket: WebSocketServerProtocol, message: str):
    """Send an error message."""

    event = {
        "type": "error",
        "message": message,
    }

    await websocket.send(json.dumps(event))


async def replay(websocket: WebSocketServerProtocol, game: RockPaperScissors):
    """Send previous moves."""

    for move in game.get_past_events():
        event = {
            "type": "play",
            "event": move,
        }

        await websocket.send(json.dumps(event))


async def play(
    websocket: WebSocketServerProtocol,
    game: RockPaperScissors,
    player: Player,
    connected,
):
    """Receive and process a play from a player."""

    async for message in websocket:
        # Parse instructions from the client.
        instructions = json.loads(message)

        print("received", instructions)

        if "type" not in instructions:
            await error(websocket, "expected 'type' field")
            continue

        if instructions["type"] != "play":
            await error(websocket, "expected 'play' event")
            continue

        if "event" not in instructions:
            await error(websocket, "expected 'event' field")
            continue
        try:
            event = instructions["event"]
            # Play the move.
            event_to_broadcast = game.play(player, event)

        except Exception as exc:
            # Send an "error" if the game could not resolve the event.
            await error(websocket, f"Game error: {exc}")
            continue

        if event_to_broadcast is not None:
            websockets.broadcast(connected, json.dumps(event_to_broadcast))


async def start(websocket):
    """Start a new game and add the first player to the game."""
    game = RockPaperScissors()

    connected = {websocket}

    join_key = secrets.token_urlsafe(nbytes=12)
    JOIN[join_key] = game, connected

    watch_key = secrets.token_urlsafe(12)

    WATCH[watch_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        await play(websocket, game, game.add_player(), connected)

    finally:
        del JOIN[join_key]


async def join(websocket: WebSocketServerProtocol, join_key):
    """Handle a connection from the second player: join an existing game."""

    # Find the game.
    try:
        game, connected = JOIN[join_key]

    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)

    try:
        # Send the first move, in case the first player already played it.
        await replay(websocket, game)

        # Receive and process moves from the second player.
        await play(websocket, game, game.add_player(), connected)

    finally:
        connected.remove(websocket)


async def watch(websocket, watch_key):
    """Handle a connection from a spectator: watch an existing game."""

    # Find the game.
    try:
        game, connected = WATCH[watch_key]

    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)

    try:
        # Send previous moves, in case the game already started.
        await replay(websocket, game)

        # Keep the connection open, but don't receive any messages.
        await websocket.wait_closed()

    finally:
        connected.remove(websocket)


async def handler(websocket):
    """Handle a connection and dispatch it according to who is connecting."""

    # Receive and parse the "init" event from the UI.

    message = await websocket.recv()

    try:
        event = json.loads(message)
    except json.JSONDecodeError:
        await error(websocket, "expected a JSON object")
        return

    if not isinstance(event, dict):
        await error(websocket, "expected a JSON object as dictionarry")
        return

    if "type" not in event:
        await error(websocket, "expected 'type' field")
        return

    if event["type"] != "init":
        await error(websocket, "expected 'init' event type")
        return

    if "join" in event:
        # Second player joins an existing game.
        await join(websocket, event["join"])

    elif "watch" in event:
        # Spectator watches an existing game.
        await watch(websocket, event["watch"])

    else:
        # First player starts a new game.
        await start(websocket)


async def main():
    async with serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
