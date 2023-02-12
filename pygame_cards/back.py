import sys
from functools import cached_property

import pygame

from pygame_cards.abstract import AbstractCard, AbstractCardGraphics
from pygame_cards.utils import DEFAULT_CARDBACK


class CardBackGraphics(AbstractCardGraphics):
    """A simple graphics for a card back.

    You can assign that graphics to any card you want.
    """

    @cached_property
    def surface(self) -> pygame.Surface:
        return pygame.transform.scale(pygame.image.load(DEFAULT_CARDBACK), self.size)


if __name__ == "__main__":
    from time import sleep

    card_back = AbstractCard("")
    card_back.graphics_type = CardBackGraphics
    card_back.graphics.size = (300, 500)
    pygame.init()

    size = width, height = 1500, 700

    screen = pygame.display.set_mode(size)
    screen.fill("black")

    position = (100 + card_back.graphics.size[0], 100)

    # Simply blit the card on the main surface
    screen.blit(card_back.graphics.surface, position)

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.flip()

        # Make sure you don't burn your cpu
        sleep(1)
