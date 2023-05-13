"""This is a client with a pygame GUI."""
# import and init pygame library
import threading
import asyncio
import pygame
import websockets
import asyncio
import pygame
from websockets.sync.client import connect

IPADDRESS = "localhost"
PORT = 8765

EVENTTYPE = pygame.event.custom_type()


def send_server(message: str):
    with connect(f"ws://{IPADDRESS}:{PORT}") as websocket:
        websocket.send(message)


async def processMsg(message):
    print(f"[Received]: {message}")
    pygame.fastevent.post(pygame.event.Event(EVENTTYPE, message=message))


def listen_server(future: asyncio.Future):
    with connect(f"ws://{IPADDRESS}:{PORT}") as websocket:
        # wait asynch for pygame events to send them
        # to the server
        print("Connected to server")
        while not future.done():
            message = websocket.recv()
            print(f"Received: {message}")


def start_server(loop: asyncio.AbstractEventLoop, future: asyncio.Future):
    loop.run_until_complete(listen_server(future))


def stop_server(loop: asyncio.AbstractEventLoop, future: asyncio.Future):
    loop.call_soon_threadsafe(future.set_result, None)
    send_server("stop")


loop = asyncio.get_event_loop()
future = loop.create_future()
thread = threading.Thread(target=start_server, args=(loop, future))
thread.start()

pygame.init()
pygame.fastevent.init()

# screen dimensions
HEIGHT = 320
WIDTH = 480

# set up the drawing window
screen = pygame.display.set_mode([WIDTH, HEIGHT])

color = pygame.Color("blue")
radius = 30
x = int(WIDTH / 2)

# run until the user asks to quit
while True:
    # did the user close the window
    for event in pygame.fastevent.get():
        if event.type == pygame.QUIT:
            print("Stoping event loop")
            stop_server(loop, future)
            print("Waiting for termination")
            thread.join()
            print("Shutdown pygame")
            pygame.quit()

        elif event.type == EVENTTYPE:
            print(event.message)
            color = pygame.Color("red")
            x = (x + radius / 3) % (WIDTH - radius * 2) + radius

    # fill the background with white
    screen.fill((255, 255, 255))

    # draw a solid blue circle in the center
    pygame.draw.circle(screen, color, (x, int(HEIGHT / 2)), radius)

    # flip the display
    pygame.display.flip()
