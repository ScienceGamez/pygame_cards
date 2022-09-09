import sys
import pygame

# Import the cardsets from the classic sets
from pygame_cards.classics import CardSets


# A set of 52 cards
card_set = CardSets.n52
n_cards = len(card_set)

pygame.init()

size = width, height = 1600, 700

n_rows = 4
spacing = 20

cards_per_row = n_cards // n_rows
# Calculate the card size for proper showing
card_size = (
    (width - (spacing) * (cards_per_row + 1)) / cards_per_row,
    (height - (spacing) * (n_rows + 1)) / n_rows,
)


screen = pygame.display.set_mode(size)

for i, card in enumerate(card_set):
    card.graphics.size = card_size
    # Show the surface of each cards on the screen
    row_position, col_position = i % cards_per_row, i // cards_per_row
    screen.blit(
        card.graphics.surface,
        (
            (spacing) * (1 + row_position) + row_position * card_size[0],
            (spacing) * (1 + col_position) + col_position * card_size[1],
        ),
    )

pygame.display.update()

while 1:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            sys.exit()

    pygame.time.wait(100)
