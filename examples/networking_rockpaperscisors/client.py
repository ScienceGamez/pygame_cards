#!/usr/bin/env python

import asyncio
import json
from websockets.sync.client import connect


""" def send_message(message: dict):
    with connect("ws://localhost:8765") as websocket:
        websocket.send(json.dumps(message))
        message = websocket.recv()
        print(f"Received: {message}")


# Wait for Ctrl+C
try:
    while True:
        val = input("Enter your message: ")
        send_message({"mesage": val})
except KeyboardInterrupt:
    print("Goodbye!")
 """

# Do the same but with a single connection at the beginning

with connect("ws://localhost:8765") as websocket:
    try:
        while True:
            val = input("Enter your message: ")
            websocket.send(json.dumps({"mesage": val}))
            message = websocket.recv()
            print(f"Received: {message}")
    except KeyboardInterrupt:
        print("Goodbye!")
