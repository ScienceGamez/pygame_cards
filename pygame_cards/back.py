from functools import cached_property
import sys
from time import sleep
import pygame
from pygame_cards.abstract import AbstractCard, AbstractCardGraphics
from pygame_emojis import load_svg

from pygame_cards.utils import DEFAULT_CARDBACK

CARD_BACK = AbstractCard("")


class CardBackGraphics(AbstractCardGraphics):
    """A simple graphics for a card back."""

    @cached_property
    def surface(self) -> pygame.Surface:
        return pygame.transform.scale(
            pygame.image.load(DEFAULT_CARDBACK), self.size
        )


CARD_BACK.graphics_type = CardBackGraphics

if __name__ == "__main__":
    pygame.init()

    size = width, height = 1500, 700

    screen = pygame.display.set_mode(size)
    screen.fill("black")

    position = (100 + CARD_BACK.graphics.size[0], 100)

    # Simply blit the card on the main surface
    screen.blit(CARD_BACK.graphics.surface, position)

    while 1:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.flip()

        # Make sure you don't burn your cpu
        sleep(1)
