"""Classic games cards based on emojis.

This is based on emojis and cards are created at runtime.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from logging import warning
import random
import sys
import pygame
from pygame_cards.abstract import AbstractCard
from pygame_cards.abstract import AbstractCardGraphics
from pygame_emojis import load_emoji, load_svg, find_code, _SVG_DIR

from pygame_cards.effects import outer_halo, Decay
from pygame_cards.set import CardsSet


class Colors(Enum):
    SPADE = "♠"
    HEART = "♥"
    DIAMOND = "♦"
    CLUB = "♣"


class Level(Enum):
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    AS = "A"


RGBColor: dict[Colors, str] = {
    Colors.SPADE: "black",
    Colors.HEART: "red",
    Colors.DIAMOND: "red",
    Colors.CLUB: "black",
}
# Colors to specify an emoji version
HEXEmojiColor: dict[Colors, str] = {
    Colors.SPADE: "1F3FB",
    Colors.HEART: "1F3FC",
    Colors.DIAMOND: "1F3FD",
    Colors.CLUB: "1F3FF",
}

LevelEmojis: dict[Level, str] = {
    Level.KING: "🤴",
    Level.QUEEN: "👸",
    Level.JACK: "💂",
}


class EmojisFrenchSuits(AbstractCardGraphics):
    """A graphics showing the cards with emojis."""

    card: NumberCard
    _icon_size: int = 60

    @property
    def icon_size(self):
        return self._icon_size

    def clear_cache(self) -> None:
        super().clear_cache()
        self.__dict__.pop("symbols_rows", None)
        self.__dict__.pop("symbols_cols", None)
        self.__dict__.pop("top_label", None)

    @cached_property
    def symbols_rows(self):
        return [
            self.size[1] / 8 * (i + 1) - self._icon_size / 2 for i in range(7)
        ]

    @cached_property
    def symbols_cols(self):
        return [
            self.size[0] / 4 * (i + 1) - self._icon_size / 2 for i in range(3)
        ]

    @cached_property
    def top_label(self) -> pygame.Surface:
        """The label at top of the cards."""
        scale = 0.15
        s = pygame.Surface(
            (int(self.size[0] * scale), int(self.size[1] * scale * 1.5)),
            pygame.SRCALPHA,
        )

        s.blit(
            load_emoji(
                self.card.color.value,
                (int(self.size[0] * scale), int(self.size[1] * scale / 1.5)),
            ),
            (0, int(self.size[1] * scale) / 2),
        )

        r = int(0.1 * min(*self.size))
        font = pygame.font.Font(None, int(self.size[1] * 0.12))
        x_pos_text = int(self.size[0] * scale / 4)
        if isinstance(self.card.number, int) and self.card.number >= 10:
            x_pos_text = x_pos_text / 4
        s.blit(
            font.render(
                str(
                    self.card.number
                    if isinstance(self.card.number, int)
                    else self.card.number.value
                ),
                True,
                RGBColor[self.card.color],
            ),
            (x_pos_text, 0),
        )
        return s

    @cached_property
    def surface(self) -> pygame.Surface:
        scale = 0.02
        scale_size = 0.15
        y_offset = self.size[1] * scale_size * 0.8
        s = super().surface
        s.blit(
            self.top_label,
            (int(self.size[0] * scale), int(self.size[1] * scale)),
        )
        # s.blit(
        #    pygame.transform.flip(self.top_label, flip_x=True, flip_y=True),
        #    (
        #        int(self.size[0] * scale),
        #        self.size[1] - int(self.size[1] * scale_size) - y_offset,
        #    ),
        # )
        # s.blit(
        #    self.top_label,
        #    (
        #        self.size[0] - int(self.size[0] * scale_size),
        #        int(self.size[1] * scale),
        #    ),
        # )
        s.blit(
            pygame.transform.flip(self.top_label, flip_x=True, flip_y=True),
            (
                self.size[0] - int(self.size[0] * scale_size),
                self.size[1] - int(self.size[1] * scale_size) - y_offset,
            ),
        )
        # Add a face to the card
        if self.card.number in LevelEmojis:

            code_list = find_code(LevelEmojis[self.card.number])
            code = "-".join(code_list)
            emojis_files = [f for f in _SVG_DIR.rglob(f"{code}*.svg")]
            good_color = [
                e
                for e in emojis_files
                if HEXEmojiColor[self.card.color] in e.stem
            ]
            # Dimension for the face
            w = self.size[0] * 0.8
            h = self.size[1] * 0.4
            face_surf = load_svg(good_color[0], size=(w, h))
            s.blit(
                pygame.transform.flip(face_surf, False, True),
                ((self.size[0] - w) / 2, (self.size[1] - h)),
            )
            s.blit(
                face_surf,
                ((self.size[0] - w) / 2, (self.size[1] / 2 - h)),
            )

        elif self.card.number == Level.AS:
            # Dimension for the face
            w = self.size[0] * 0.8
            s.blit(
                load_emoji(self.card.color.value, (w, w)),
                (((self.size[0] - w) / 2, (self.size[1] - w) / 2)),
            )

        elif isinstance(self.card.number, int):
            # place the icons
            icon_s = load_emoji(self.card.color.value, self.icon_size)
            flipped_icon = pygame.transform.flip(icon_s, False, True)
            r = self.symbols_rows
            c = self.symbols_cols
            self.logger.debug(
                f"{r=}, {c=}, {s.get_size()}, {icon_s.get_size()}"
            )
            if self.card.number in [2, 3]:
                s.blit(icon_s, (c[1], r[0]))
                s.blit(flipped_icon, (c[1], r[-1]))
            if self.card.number > 3:
                s.blit(icon_s, (c[0], r[0]))
                s.blit(icon_s, (c[2], r[0]))
                s.blit(flipped_icon, (c[0], r[-1]))
                s.blit(flipped_icon, (c[2], r[-1]))
            if self.card.number in [6, 7, 8]:
                s.blit(icon_s, (c[0], r[3]))
                s.blit(icon_s, (c[2], r[3]))
            if self.card.number in [3, 5, 9]:
                # Middle icon
                s.blit(icon_s, (c[1], r[3]))
            if self.card.number in [7, 8]:
                # Middle mid top
                s.blit(icon_s, (c[1], (r[1] + r[2]) // 2))
            if self.card.number == 8:
                # Middle mid down
                s.blit(
                    flipped_icon,
                    (c[1], (r[4] + r[5]) // 2),
                )
            if self.card.number in [9, 10]:
                # Middle mid top
                s.blit(icon_s, (c[0], r[2]))
                s.blit(icon_s, (c[2], r[2]))

                s.blit(flipped_icon, (c[0], r[4]))
                s.blit(flipped_icon, (c[2], r[4]))
            if self.card.number == 10:
                s.blit(icon_s, (c[1], r[1]))
                s.blit(flipped_icon, (c[1], r[5]))

        else:
            warning(f"Could not decorate {self.card}")

        return s


@dataclass(repr=False, eq=False)
class NumberCard(AbstractCard):

    number: int | Level
    color: Colors

    graphics_type = EmojisFrenchSuits


class CardSets:
    """Default card sets that can be used.

    :attr n52: A 52 game cards.
    :attr n36: A 36 game cards.
    """

    @classmethod
    @property
    def n52(self) -> CardsSet[NumberCard]:
        return CardsSet(
            [
                NumberCard(f"{n} of {c.value}", n, c)
                for c in Colors
                for n in [i for i in range(2, 11)] + [l for l in Level]
            ]
        )

    @classmethod
    @property
    def n36(self) -> CardsSet[NumberCard]:
        return CardsSet(
            [
                NumberCard(f"{n} of {c.value}", n, c)
                for c in Colors
                for n in [i for i in range(6, 11)] + [l for l in Level]
            ]
        )


if __name__ == "__main__":

    # This will visualize the cards

    pygame.init()

    size = width, height = 1500, 1000

    screen = pygame.display.set_mode(size)

    set = CardSets.n52
    counter = 0
    card = random.choice(set)
    print(set)

    # Add event to show the first card
    pygame.event.post(
        pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_LEFT})
    )
    while 1:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Arrows allow to navigate around the cards
                if event.key == pygame.K_LEFT:
                    counter -= 1
                elif event.key == pygame.K_RIGHT:
                    counter += 1
                elif event.key == pygame.K_UP:
                    counter += len(set) // 4
                elif event.key == pygame.K_DOWN:
                    counter -= len(set) // 4
                else:
                    counter = random.randint(0, len(set))
                card = set[counter % len(set)]
                graphics = EmojisFrenchSuits(card)
                screen.fill("black")
                screen.blit(
                    outer_halo(
                        graphics.surface,
                        decay=Decay.QUADRATIC,
                        inner_color=pygame.Color(255, 255, 30),
                    ),
                    (180, 180),
                )
                screen.blit(graphics.surface, (200, 200))

                rotated = pygame.transform.rotate(graphics.surface, 45)
                screen.blit(rotated, (600, 200))

                pygame.display.update()

        pygame.time.wait(100)
