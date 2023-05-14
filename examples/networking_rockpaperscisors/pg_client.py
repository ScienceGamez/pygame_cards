"""Pygame example using websockets to communicate with a server."""
import json
import logging
import threading
from time import sleep
import pygame
import websocket
from content import RockPaperScissors, Player, ROCK_PAPER_SCISSORS_CARDSET
import pygame_cards.events
from pygame_cards.hands import AlignedHand
from pygame_cards.manager import CardSetRights, CardsManager


logging.basicConfig()
socket = "ws://localhost:8765/"
# websocket.enableTrace(True)

PLAYING = True

# Game to join
join_key = "cUVtaORqA0SfPjTT"
# If you are the first play
# join_key = None


# Call backs from the websocket
def on_open(ws):
    if join_key is None:
        ws.send(json.dumps({"type": "init"}))
    else:
        ws.send(json.dumps({"type": "init", "join": join_key}))
    print(">>>>>>OPENED")


def on_message(ws, message):
    print("Message received: ", message)


def on_close(ws, close_status_code, close_msg):
    global PLAYING
    PLAYING = False
    print(">>>>>>CLOSED")


def on_error(ws, error):
    print(error)


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()


ws = websocket.WebSocketApp(
    socket, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error
)

wst = threading.Thread(target=lambda: ws.run_forever())
wst.daemon = True
wst.start()


# Create the cardset graphics
cardset_graphics = AlignedHand(cardset=ROCK_PAPER_SCISSORS_CARDSET, card_halo_ratio=0.2)

# Create a manager and add the carset to it
manager = CardsManager()
manager.add_set(
    cardset_graphics,
    position=(500, 500),
    card_set_rights=CardSetRights(
        clickable=True, draggable_out=False, draggable_in=False
    ),
)
# manager.logger.setLevel(logging.DEBUG)

while PLAYING:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            PLAYING = False
            ws.close()
        if (
            event.type == pygame_cards.events.CARDSSET_CLICKED
            and event.card is not None
        ):
            ws.send(json.dumps({"type": "play", "event": event.card.name}))

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    manager.process_events(event)
    time_delta = clock.tick(60)  # limits FPS to 60

    manager.update(time_delta)
    manager.draw(screen)
    # flip() the display to put your work on screen
    pygame.display.flip()

pygame.quit()
wst.join()
