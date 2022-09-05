from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
import sys
from time import sleep
import pygame
from examples.tutorial.minion_card import MinionCard

from pygame_emojis import load_emoji

# Again, we start from the abstract graphics
from pygame_cards.abstract import AbstractCardGraphics

# Import the cards we just created
from minion_set import MY_COMMUNITY_OF_THE_RING
from pygame_cards.utils import position_for_centering


@dataclass
class MinionCardGraphics(AbstractCardGraphics):
    """A Grphics card for our lotr characters."""

    # Specify the type of card that this graphics accept
    card: MinionCard

    # This will be the file where the character is
    filepath: Path = None

    @cached_property
    def surface(self) -> pygame.Surface:

        # Size is a property from AbstractCardGraphics
        x, y = self.size

        # Create the surface on which we will plot the card
        surf = pygame.Surface(self.size)

        if self.filepath is not None:
            # Load the image of our character
            picture = pygame.image.load(self.filepath)
            # Rescale it to fit the surface
            surf.blit(pygame.transform.scale(picture, self.size), (0, 0))

        # Create the name on top using pygame fonts
        font = pygame.font.SysFont("urwgothic", 48)
        name = font.render(self.card.name, True, pygame.Color(163, 146, 139))

        # Make sure the name is centered in the x direction.
        surf.blit(name, (position_for_centering(name, surf)[0], 10))

        # Add some emojis for health and attack
        emoji_size = (100, 100)
        attack_emoji = load_emoji("⚔️", emoji_size)
        life_emoji = load_emoji("♥️", emoji_size)

        emoji_border_offset = 5
        surf.blit(
            attack_emoji,
            # Do a bit of maths to guess the position
            (
                emoji_border_offset,
                self.size[1] - emoji_border_offset - emoji_size[1],
            ),
        )
        surf.blit(
            life_emoji,
            (
                self.size[0] - emoji_border_offset - emoji_size[0],
                self.size[1] - emoji_border_offset - emoji_size[1],
            ),
        )

        return surf


for card in MY_COMMUNITY_OF_THE_RING:
    # Select the good file for each Card.
    match card.name:
        case "Bilbo":
            file = "DALL·E 2022-08-30 20.58.30 - frodo from lotr being obsessed with the ring, digital art.png"
        case "Gandalf":
            file = "DALL·E 2022-08-30 20.59.25 - gandalf from lotr looking very wise on his horse, digital art.png"
        case "Sam":
            file = "DALL·E 2022-08-30 21.01.56 - sam the hobbit from lotr sharing some elven bread, digital art.png"
        case _:
            raise ValueError(f"Unkonwn character {card.name}")

    card.graphics = MinionCardGraphics(
        card,
        filepath=Path("images", file),
    )

if __name__ == "__main__":

    # A very simple game loop to show the cards
    pygame.init()

    size = width, height = 1000, 500

    screen = pygame.display.set_mode(size)
    screen.fill("black")

    for i, card in enumerate(MY_COMMUNITY_OF_THE_RING):

        position = (50 + i * (100 + card.graphics.size[0]), 100)

        # Simply blit the card on the main surface
        screen.blit(card.graphics.surface, position)

    # Save images for the documentation
    pygame.image.save(
        screen,
        Path("images", f"card_from_tuto.png"),
    )

    while 1:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.flip()

        # Make sure you don't burn your cpu
        sleep(1)
