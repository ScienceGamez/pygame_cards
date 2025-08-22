"""Game Manager for cards in pygame."""

from dataclasses import dataclass
import logging
import random
from typing import Callable

import pygame
from pygame_cards.abstract import AbstractCard as Card
from pygame_cards.abstract import Manager
from pygame_cards.deck import Deck
from pygame_cards.events import cardsset_clicked, card_moved
from pygame_cards.hands import (
    AlignedHand,
    BaseHand,
    CardsetGraphic,
    RoundedHand,
    VerticalPileGraphic,
)

from pygame_cards.set import CardsSet
from pygame_cards.effects import Decay, outer_halo


@dataclass
class CardSetRights:
    """Rigths for what the manager can do with a card set.


    :param clickable: Whether clicking on the set will
        generate CARDSSET_CLICKED events.
    :param draggable_out: Whether we can drag the card out
        of the card set to another one.
    :param draggable_in: Whether we can drag a card from
        another card set into this one.
    :param highlight_hovered_card: Whether to highlight the
        hoverd_card from the cardset when the card set is hovered
    """

    clickable: bool = False
    draggable_out: bool | Callable[[Card], bool] = True
    draggable_in: bool | Callable[[Card], bool] = True
    highlight_hovered_card: bool = True
    drag_multiple_cards: bool = False

    def __post_init__(self):
        # Convert to a function
        if isinstance(self.draggable_in, bool):
            drag_in = self.draggable_in
            self.draggable_in = lambda card: drag_in
        if isinstance(self.draggable_out, bool):
            drag_out = self.draggable_out
            self.draggable_out = lambda card: drag_out


class CardsManager(Manager):
    """A card manager handling cardset graphics.

    This is meant to be used similarily as the ui_manager from
    :py:mod:`pygame_gui` .


    Capabilities :

    * Tracking which cardset and card are under the player mouse.
    * Moving cards from on cardset to another
    * Add related events in the game loop

    The cards manager can be inherited from if you need to add special
    graphic mechanics.

    """

    card_sets: list[CardsetGraphic]
    _card_sets_positions: list[tuple[int, int]]
    _card_sets_rigths: list[CardSetRights]

    # Attributes for recoreding past moves
    last_mouse_pos: tuple[int, int] = (0, 0)
    mouse_speed: tuple[int, int] = (0, 0)
    last_card_under_mouse: Card | None = None

    # For handling internal events
    _clicked: bool = False
    _is_aquiring_card: bool = False
    _stop_aquiring_card: bool = False
    _cardset_under_mouse: CardsetGraphic | None = None
    _card_under_mouse: Card | None = None
    _card_under_acquisition: Card | None = None
    _cardset_under_acquisition: CardsSet | None = None
    _cardset_of_acquisition: CardsSet | None = None
    _graphics_cardset_under_acquisition: VerticalPileGraphic | None = None
    mouse_pos = None
    _current_time: int = 0
    _time_last_down: int = 0

    def __init__(self, click_time: int = 150) -> None:
        """Create a manager.

        :arg click_time: The time you need from the mousebutton down
            to the mouse button up [ms]

        """
        super().__init__()
        self.card_sets = []
        self._card_sets_positions = []
        self._card_sets_rigths = []
        self.click_time = click_time

    def add_set(
        self,
        card_set: CardsetGraphic,
        position: tuple[int, int],
        # Attributes to handled how the user can handled the cards
        card_set_rights: CardSetRights = CardSetRights(),
    ):
        """Add a card set graphics to be managed.

        :arg card_set: The cardset graphics to add.
        :arg position: The position where to show it on screen.

        """
        self.card_sets.append(card_set)
        self._card_sets_positions.append(position)
        self._card_sets_rigths.append(card_set_rights)

    def process_events(self, event: pygame.event.Event):
        """Process a pygame event."""
        match event:
            case pygame.event.EventType(type=pygame.MOUSEBUTTONDOWN):
                # Check if we started to acquire a card
                self._is_aquiring_card = True
                self.mouse_pos = event.pos
                self._time_last_down = self._current_time
            case pygame.event.EventType(type=pygame.MOUSEBUTTONUP):
                if (
                    self._card_under_acquisition is not None
                    or self._cardset_under_acquisition is not None
                ):
                    self._stop_aquiring_card = True
                else:
                    self._is_aquiring_card = False
                    self._clicked = True
                self.mouse_pos = event.pos

    def update(self, time: int) -> bool:
        """Update the manager with the new time.

        Has to be called after process events.

        :arg time: The time since the last update.
            in ms.
        :return: whether the surface was updated or not.
        """

        if self.mouse_pos is None:
            # update the mouse pos if not in an event
            self.mouse_pos = pygame.mouse.get_pos()

        if self.last_mouse_pos != self.mouse_pos:
            # Find the card set under the mouse
            cardsets_under_mouse = [
                card_set
                for card_set, position in zip(self.card_sets, self._card_sets_positions)
                if card_set.surface.get_rect()
                .move(*position)
                .collidepoint(self.mouse_pos)
            ]
            self.logger.debug(f"{cardsets_under_mouse = }")

            # Try to find the card under the mouse
            self._cardset_under_mouse = None
            self._card_under_mouse = None
            for card_set in reversed(cardsets_under_mouse):
                self._cardset_under_mouse = card_set
                position = self._card_sets_positions[self.card_sets.index(card_set)]
                mousepos_in_set = (
                    self.mouse_pos[0] - position[0],
                    self.mouse_pos[1] - position[1],
                )
                self.logger.debug(
                    f"{mousepos_in_set = }, {self.mouse_pos = } - {position = }"
                )

                if self.get_cardset_rights(card_set).drag_multiple_cards:
                    sub_card_set = card_set.get_cards_at(mousepos_in_set)
                    if sub_card_set is not None:
                        self._subcardset_under_mouse = sub_card_set

                card = card_set.get_card_at(mousepos_in_set)
                if card is not None:
                    # Card was found
                    self._card_under_mouse = card
                    break
            self.logger.debug(f"{cardsets_under_mouse = }")
            self.logger.debug(f"{self._cardset_under_mouse = }")
            self.logger.debug(f"{self._card_under_mouse = }")

        if self._is_aquiring_card and self._stop_aquiring_card:
            # Was a single click
            _card_set_rights = self._card_sets_rigths[
                self.card_sets.index(self._cardset_under_mouse)
            ]
            if _card_set_rights.clickable and (
                (self._current_time - self._time_last_down) <= self.click_time
            ):
                # Post an event in the loop
                clicked_event = cardsset_clicked(
                    self._cardset_under_mouse, self._card_under_mouse
                )
                pygame.event.post(clicked_event)
            # Single click done
            self._is_aquiring_card, self._stop_aquiring_card = False, False

        if (
            self._is_aquiring_card
            and self._card_under_mouse is not None
            and self._card_under_acquisition is None
            and self._cardset_under_acquisition is None
        ):
            _card_set_rights = self._card_sets_rigths[
                self.card_sets.index(self._cardset_under_mouse)
            ]
            if _card_set_rights.draggable_out(self._card_under_mouse):
                # User starts to aquire a card
                self._cardset_of_acquisition = self._cardset_under_mouse
                if _card_set_rights.drag_multiple_cards:
                    self._cardset_under_acquisition = self._subcardset_under_mouse
                    self.logger.debug(
                        f"Under acquisition {self._cardset_under_acquisition}"
                    )
                    for card in self._cardset_under_acquisition:
                        self._cardset_of_acquisition.remove_card(card)
                        card.graphics.clear_cache()
                else:
                    self._card_under_acquisition = self._card_under_mouse

                    self.logger.debug(
                        f"Under acquisition {self._card_under_acquisition}"
                    )
                    self._cardset_of_acquisition.remove_card(
                        self._card_under_acquisition
                    )

                    self._card_under_acquisition.graphics.clear_cache()

            # self._cardset_under_mouse = None
            self._card_under_mouse = None
            self._subcardset_under_mouse = None
            self._is_aquiring_card = False

        if self._stop_aquiring_card:
            # Card released
            if (
                self._cardset_under_mouse == self._cardset_of_acquisition
                and self.get_cardset_rights(self._cardset_under_mouse).clickable
                and ((self._current_time - self._time_last_down) <= self.click_time)
            ):
                if self._card_under_acquisition:
                    # Check for click event
                    pygame.event.post(
                        cardsset_clicked(
                            self._cardset_under_mouse,
                            self._card_under_acquisition,
                        )
                    )
                if (
                    self._cardset_under_acquisition
                    and len(self._cardset_under_acquisition) == 1
                ):
                    pygame.event.post(
                        cardsset_clicked(
                            self._cardset_under_mouse,
                            self._cardset_under_acquisition[0],
                        )
                    )

            if (
                self._cardset_under_mouse is not None
                and self._card_under_acquisition is not None
                and self.get_cardset_rights(self._cardset_under_mouse).draggable_in(
                    self._card_under_acquisition
                )
            ):
                self._cardset_under_mouse.append_card(self._card_under_acquisition)

                pygame.event.post(
                    card_moved(
                        self._card_under_acquisition,
                        self._cardset_of_acquisition,
                        self._cardset_under_mouse,
                    )
                )
            elif (
                self._cardset_under_mouse is not None
                and self._cardset_under_acquisition
                and self.get_cardset_rights(self._cardset_under_mouse).draggable_in(
                    self._cardset_under_acquisition[0]
                )
            ):
                for card in self._cardset_under_acquisition:
                    self._cardset_under_mouse.append_card(card)

                    pygame.event.post(
                        card_moved(
                            card,
                            self._cardset_of_acquisition,
                            self._cardset_under_mouse,
                        )
                    )
            elif self._card_under_acquisition is not None:
                self._cardset_of_acquisition.append_card(self._card_under_acquisition)
            elif self._cardset_under_acquisition:
                self._cardset_of_acquisition.extend_cards(
                    self._cardset_under_acquisition
                )
            else:
                logging.warning(f"Unexpected behaviour in {self}")

            self._cardset_of_acquisition = None
            self._card_under_acquisition = None
            self._graphics_cardset_under_acquisition = None
            self._cardset_under_acquisition = None
            self._stop_aquiring_card = False

        if (
            self._clicked
            and self._cardset_under_mouse is not None
            and self.get_cardset_rights(self._cardset_under_mouse).clickable
        ):
            pygame.event.post(
                cardsset_clicked(
                    self._cardset_under_mouse,
                    self._card_under_mouse,
                )
            )
        # Update the mouse position and speed
        self.mouse_speed = (
            self.mouse_pos[0] - self.last_mouse_pos[0],
            self.mouse_pos[1] - self.last_mouse_pos[1],
        )
        self.last_mouse_pos = self.mouse_pos
        self.mouse_pos = None
        self._clicked = False
        self._current_time += time

    def get_cardset_rights(self, cards_set: CardsetGraphic) -> CardSetRights:
        return self._card_sets_rigths[self.card_sets.index(cards_set)]

    def draw(self, window: pygame.Surface, rotate_moving_card: bool = True):
        """Draw the cards on the screen."""
        for card_set, position in zip(self.card_sets, self._card_sets_positions):
            if (
                card_set == self._cardset_under_mouse
                and self._card_under_acquisition is not None
                and self.get_cardset_rights(card_set).draggable_in(
                    self._card_under_acquisition
                )
            ):
                # Add halo to the set under which the card is
                radius = (card_set.size[0] + card_set.size[1]) // 50
                window.blit(
                    outer_halo(
                        card_set.surface,
                        radius=radius,
                        decay=Decay.NONE,
                        inner_color=pygame.Color(255, 255, 255, 60),
                    ),
                    (position[0] - radius, position[1] - radius),
                )

            # Show the cardset
            window.blit(card_set.surface, position)

            if (
                card_set == self._cardset_under_mouse
                and self._card_under_mouse is not None
                and self._card_under_acquisition is None
                and self.get_cardset_rights(card_set).highlight_hovered_card
            ):
                # Show the hovered card
                hover = card_set.with_hovered(self._card_under_mouse)
                window.blit(
                    hover,
                    position,
                )
        if self._card_under_acquisition is not None:
            # Plot the card under acquisition
            card_surf = self._card_under_acquisition.graphics.surface
            if rotate_moving_card:
                # Angle is proportional to speed
                angle = self.mouse_speed[0] * 0.5
                card_surf = pygame.transform.rotate(card_surf, -angle)
            window.blit(
                card_surf,
                (
                    self.last_mouse_pos[0] - card_surf.get_size()[0] / 2,
                    self.last_mouse_pos[1] - card_surf.get_size()[1] * 0.1,
                ),
            )

        if self._cardset_under_acquisition:
            # Plot the cardset under acquisition
            card_size = self._cardset_under_acquisition[0].graphics.size
            if self._graphics_cardset_under_acquisition is None:
                self._graphics_cardset_under_acquisition = VerticalPileGraphic(
                    self._cardset_under_acquisition,
                    size=(card_size[0], card_size[1] * 3),
                    card_size=card_size,
                )
            graphic = self._graphics_cardset_under_acquisition
            surf = graphic.surface
            if rotate_moving_card:
                # Angle is proportional to speed
                angle = self.mouse_speed[0] * 0.5
                surf = pygame.transform.rotate(surf, -angle)
            window.blit(
                surf,
                (
                    self.last_mouse_pos[0]
                    + (
                        card_size[0] / 2 - surf.get_width()
                        if angle > 0
                        else -card_size[0] / 2
                    ),
                    self.last_mouse_pos[1] - card_size[1] * 0.1,
                ),
            )

    def start_crazy(self, screen: pygame.Surface):
        """Start the crazy mode.

        Good way to end a game.
        """
        # Get all cards available in the cardsets
        cards = []
        x_positions = []
        y_positions = []
        for cardset, pos in zip(self.card_sets, self._card_sets_positions):
            positions = cardset.get_card_positions()
            set_x, set_y = pos
            for card in cardset.cardset:
                x, y = positions[card]
                x_positions.append(x + set_x)
                y_positions.append(y + set_y)
                cards.append(card)

        cards = sum([cardset.cardset], [])

        x_velocities = [random.randint(-10, 10) for _ in range(len(cards))]
        y_velocities = [random.randint(-10, 10) for _ in range(len(cards))]
        y_acceleration = 1

        fps = 30
        clock = pygame.time.Clock()

        while True:
            # Update the position of all the cards based on the velocity and gravity
            for i in range(len(cards)):
                x, y = x_positions[i], y_positions[i]
                x_positions[i] += x_velocities[i]
                y_positions[i] += y_velocities[i]
                y_velocities[i] += y_acceleration
                if y_positions[i] > screen.get_height() - cards[i].graphics.size[1]:
                    y_velocities[i] = -y_velocities[i]
                if (
                    x_positions[i] < 0
                    or x_positions[i] > screen.get_width() - cards[i].graphics.size[0]
                ):
                    x_velocities[i] = -x_velocities[i]

            screen.blits(
                [
                    (card.graphics.surface, (x, y))
                    for card, x, y in zip(cards, x_positions, y_positions)
                ]
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()

            pygame.display.update()

            clock.tick(fps)


if __name__ == "__main__":
    # This will visualize the cards

    import sys
    import pygame
    from pygame_cards.classics import CardSets as ClassicCardSet

    logging.basicConfig()
    # logging.basicConfig(level=logging.DEBUG)

    pygame.init()

    size = width, height = 1500, 700

    screen = pygame.display.set_mode(size)

    # put a small button to start crazy stuff on the top right of the screen
    font = pygame.font.Font(None, 20)
    button = font.render("Start Crazy", True, (255, 255, 255))
    start_crazy_button_pos = (size[0] - button.get_width() - 10, 10)

    card_set = CardsSet(ClassicCardSet.n52[:3])
    card_set2 = ClassicCardSet.n52[7:18]
    graphics_aligned = AlignedHand(card_set, card_size=(110, 210))
    graphics_rounded = RoundedHand(card_set2)

    deck = Deck(ClassicCardSet.n52[18:])

    # graphics_aligned.logger.setLevel(logging.DEBUG)
    # graphics_rounded.logger.setLevel(logging.DEBUG)

    manager = CardsManager()

    manager.add_set(graphics_aligned, (200, 0))
    manager.add_set(graphics_rounded, (200, 400))
    manager.add_set(deck, (1200, 200))

    pygame.display.flip()

    clock = pygame.time.Clock()

    while 1:
        screen.fill("black")
        screen.blit(button, start_crazy_button_pos)
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # get the position of the mouse click
                mouse_pos = pygame.mouse.get_pos()
                # Check if touches the crazy stuff
                if (
                    start_crazy_button_pos[0]
                    <= mouse_pos[0]
                    <= start_crazy_button_pos[0] + button.get_width()
                ):
                    manager.start_crazy(screen)
                    break

            manager.process_events(event)

        manager.update(time_delta)
        manager.draw(screen)
        pygame.display.flip()
