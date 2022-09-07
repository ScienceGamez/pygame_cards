"""Game Manager for cards in pygame."""
from dataclasses import dataclass
import logging

import pygame
from pygame_cards.abstract import AbstractCard as Card
from pygame_cards.abstract import Manager
from pygame_cards.deck import Deck
from pygame_cards.events import cardsset_clicked
from pygame_cards.hands import (
    AlignedHand,
    BaseHand,
    CardsetGraphic,
    RoundedHand,
)

from pygame_cards.set import CardsSet
from pygame_cards.effects import Decay, outer_halo


@dataclass
class CardSetRights:
    """Rigths for what the manager can do with a card set.


    :attr clickable: Whether clicking on the set will
        generate CARDSSET_CLICKED events.
    :attr draggable_out: Whether we can drag the card out
        of the card set to another one.
    :attr draggable_in: Whether we can drag a card from
        another card set into this one.
    :attr highlight_hovered_card: Whether to highlight the
        hoverd_card from the cardset when the card set is hovered
    """

    clickable: bool = False
    draggable_out: bool = True
    draggable_in: bool = True
    highlight_hovered_card: bool = True


class CardsManager(Manager):
    """A card manager class.

    This is meant to be used similarily as the ui_manager from
    :py:module:`pygame_gui`.


    Capabilities:

    * Looking which cardset and card are under the player mouse.
    * Moving cards from on cardset to another

    """

    card_sets: list[CardsetGraphic]
    _card_sets_positions: list[tuple[int, int]]
    _card_sets_rigths: list[CardSetRights]

    # Attribues for recoreding past moves
    last_mouse_pos: tuple[int, int] = (0, 0)
    mouse_speed: tuple[int, int] = (0, 0)
    last_card_under_mouse: Card | None = None

    # For handling internal events
    _is_aquiring_card: bool = False
    _stop_aquiring_card: bool = False
    _cardset_under_mouse: CardsetGraphic | None = None
    _card_under_mouse: Card | None = None
    _card_under_acquisition: Card | None = None
    _cardset_of_acquisition: CardsSet | None = None

    def __init__(self) -> None:
        super().__init__()
        self.card_sets = []
        self._card_sets_positions = []
        self._card_sets_rigths = []

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
            case pygame.event.EventType(type=pygame.MOUSEBUTTONUP):
                if self._card_under_acquisition is not None:
                    self._stop_aquiring_card = True
                else:
                    self._is_aquiring_card = False

    def update(self, time: int) -> bool:
        """Update the manager with the new time.

        Has to be called after process events.

        :return whether the surface was updated.
        """
        mouse_pos = pygame.mouse.get_pos()

        if self.last_mouse_pos != mouse_pos:

            # Find the card set under the mouse
            cardsets_under_mouse = [
                card_set
                for card_set, position in zip(
                    self.card_sets, self._card_sets_positions
                )
                if card_set.surface.get_rect()
                .move(*position)
                .collidepoint(mouse_pos)
            ]

            # Try to find the card under the mouse
            self._cardset_under_mouse = None
            self._card_under_mouse = None
            for card_set in reversed(cardsets_under_mouse):
                self._cardset_under_mouse = card_set
                position = self._card_sets_positions[
                    self.card_sets.index(card_set)
                ]
                mousepos_in_set = (
                    self.last_mouse_pos[0] - position[0],
                    self.last_mouse_pos[1] - position[1],
                )
                card = card_set.get_card_at(mousepos_in_set)
                if card is not None:
                    # Card was found
                    self._card_under_mouse = card
                    break

        if self._is_aquiring_card and self._stop_aquiring_card:
            # Was a single click
            _card_set_rights = self._card_sets_rigths[
                self.card_sets.index(self._cardset_under_mouse)
            ]
            if _card_set_rights.clickable:
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
        ):
            _card_set_rights = self._card_sets_rigths[
                self.card_sets.index(self._cardset_under_mouse)
            ]
            if _card_set_rights.draggable_out:
                # User starts to aquire a card
                self._card_under_acquisition = self._card_under_mouse
                self._cardset_of_acquisition = self._cardset_under_mouse

                self.logger.debug(
                    f"Under acquisition {self._card_under_acquisition}"
                )
                self._cardset_of_acquisition.remove_card(
                    self._card_under_acquisition
                )

                self._card_under_acquisition.graphics.clear_cache()

            self._cardset_under_mouse = None
            self._card_under_mouse = None
            self._is_aquiring_card = False

        if self._stop_aquiring_card:
            # Card released
            if (
                self._cardset_under_mouse is not None
                and self.get_cardset_rights(
                    self._cardset_under_mouse
                ).draggable_in
            ):
                self._cardset_under_mouse.append_card(
                    self._card_under_acquisition
                )
            else:
                self._cardset_of_acquisition.append_card(
                    self._card_under_acquisition
                )

            self._cardset_of_acquisition = None
            self._card_under_acquisition = None
            self._stop_aquiring_card = False

        # Update the mouse position and speed
        self.mouse_speed = (
            mouse_pos[0] - self.last_mouse_pos[0],
            mouse_pos[1] - self.last_mouse_pos[1],
        )
        self.last_mouse_pos = mouse_pos

    def get_cardset_rights(self, cards_set: CardsetGraphic) -> CardSetRights:
        return self._card_sets_rigths[self.card_sets.index(cards_set)]

    def draw(self, window: pygame.Surface, rotate_moving_card: bool = True):
        """Draw the cards on the screen."""
        for card_set, position in zip(
            self.card_sets, self._card_sets_positions
        ):

            if (
                card_set == self._cardset_under_mouse
                and self._card_under_acquisition is not None
                and self.get_cardset_rights(card_set).draggable_in
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

            # Plo the card under acquisition
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
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                sys.exit()

            manager.process_events(event)

        manager.update(time_delta)
        manager.draw(screen)
        pygame.display.flip()
