#!/usr/bin/env python

import argparse
import asyncio
import json
import threading
import time
import websockets
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

""" with connect("ws://localhost:8765") as websocket:
    try:
        while True:
            val = input("Enter your message: ")
            websocket.send(json.dumps({"mesage": val}))
            message = websocket.recv()
            print(f"Received: {message}")
    except KeyboardInterrupt:
        print("Goodbye!")
 """


class ServerListener:
    must_stop: bool = False

    messages_to_send: list[str] = []

    def set_websocket(self, websocket: websockets.WebSocketClientProtocol):
        self.websocket = websocket

    def send_messages(self):
        try:
            while not self.must_stop:
                while self.messages_to_send:
                    # Pop the message
                    msg = self.messages_to_send.pop(0)
                    self.websocket.send(json.dumps({"message": msg}))
                # Wait max one second for receive timeout

                # message = self.websocket.recv()

                # print(f"Received: {message}")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("Goodbye!")
        self.websocket.close()


if __name__ == "__main__":
    server_listener = ServerListener()

    def start_listening(server_listener):
        with connect("ws://localhost:8765") as websocket:
            server_listener.set_websocket(websocket)
            server_listener.send_messages()

    listening_thread = threading.Thread(target=start_listening, args=(server_listener,))
    listening_thread.start()

    # Add a message very second
    for i in range(10):
        server_listener.messages_to_send.append("Hello")
        time.sleep(1)

    server_listener.must_stop = True
