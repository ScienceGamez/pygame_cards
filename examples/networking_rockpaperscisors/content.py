"""Shared content for the game."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from functools import cached_property

import pygame
from pygame_emojis import load_emoji
from pygame_cards.hands import AlignedHand
from pygame_cards.manager import CardSetRights, CardsManager

import pygame_cards.events

from pygame_cards.set import CardsSet
from pygame_cards.abstract import AbstractCard, AbstractCardGraphics


class CARDSIGN(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


EMOJI_TO_USE: dict[CARDSIGN, str] = {
    CARDSIGN.ROCK: "🪨",
    CARDSIGN.PAPER: "📄",
    CARDSIGN.SCISSORS: "✂️",
}


@dataclass
class RockPaperScisorsGraphics(AbstractCardGraphics):
    card: RockPaperScissorsCard

    @cached_property
    def surface(self) -> pygame.Surface:
        # Transparent background
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)

        # Load the emoji as a pygame.Surface
        emoji = EMOJI_TO_USE[self.card.sign]
        surface = load_emoji(emoji, self.size)
        # Draw the emoji
        surf.blit(surface, (0, 0))

        return surf


@dataclass
class RockPaperScissorsCard(AbstractCard):
    sign: CARDSIGN
    graphics_type = RockPaperScisorsGraphics


ROCK_PAPER_SCISSORS_CARDSET = CardsSet(
    # Iterate over enum to create the cards
    [RockPaperScissorsCard(sign=sign, name=sign.value) for sign in CARDSIGN]
)


if __name__ == "__main__":
    print(ROCK_PAPER_SCISSORS_CARDSET)

    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    # Create the cardset graphics
    cardset_graphics = AlignedHand(
        cardset=ROCK_PAPER_SCISSORS_CARDSET, card_halo_ratio=0.2
    )

    # Create a manager and add the carset to it
    manager = CardsManager()
    manager.add_set(
        cardset_graphics,
        position=(500, 500),
        card_set_rights=CardSetRights(
            clickable=True, draggable_out=False, draggable_in=False
        ),
    )

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame_cards.events.CARDSSET_CLICKED:
                print(event.set, event.card)

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        manager.process_events(event)
        time_delta = clock.tick(60)  # limits FPS to 60

        manager.update(time_delta)
        manager.draw(screen)
        # flip() the display to put your work on screen
        pygame.display.flip()

    pygame.quit()
