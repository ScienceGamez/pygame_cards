"""Small sevrer for rock paper scisors game.

The server is based on websockets.
"""

#!/usr/bin/env python

import asyncio
import json
from websockets.server import serve


async def echo(websocket):
    async for message in websocket:
        print(message)

        try:
            json.loads(message)
        except:
            print("not json")

        await websocket.send(message)


async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
