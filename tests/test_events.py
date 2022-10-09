import logging
import unittest
import pygame
import pygame_cards

from pygame_cards.events import cardsset_clicked, CARDSSET_CLICKED
from pygame_cards.hands import AlignedHand, BaseHand, CardsetGraphic
from pygame_cards.manager import CardSetRights, CardsManager
from pygame_cards.classics import CardSets

pygame.init()

# Cards for testing
test_card_set = CardSets.n36[:3]


class TestEventsForTests(unittest.TestCase):
    def test_can_get_event(self):
        """Just test that pygame events can be get in tests."""

        test_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN)
        pygame.event.post(test_event)
        events = pygame.event.get()

        self.assertIn(test_event, events)


class TestCardsManager(unittest.TestCase):
    """Test that the card manager produces correct pygame.Events."""

    def setUp(self) -> None:
        super().setUp()
        self.manager = CardsManager()

        self.cardset_graphic = AlignedHand(
            test_card_set,
            size=(30, 10),
            card_size=(10, 8),
            card_border_radius=1,
        )

    def test_can_add_graphics(self):

        self.manager.add_set(self.cardset_graphic, (10, 10))

        self.assertIn(self.cardset_graphic, self.manager.card_sets)

    def test_can_listen_events(self):
        test_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"pos": (0, 0)}
        )
        self.manager.process_events(test_event)

        self.manager.update(0.2)

    def test_click(self):
        """Click event should occur when pressing on a card and release fast enough"""
        self.manager.add_set(
            self.cardset_graphic,
            (10, 10),
            card_set_rights=CardSetRights(clickable=True),
        )
        click_pos = (15, 15)
        down_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"pos": click_pos}
        )
        up_event = pygame.event.Event(pygame.MOUSEBUTTONUP, {"pos": click_pos})

        self.manager.process_events(down_event)
        # self.assertTrue(self.manager._is_aquiring_card)
        self.manager.process_events(up_event)
        # self.assertTrue(self.manager._clicked)

        self.manager.update(0.2)
        # self.assertEqual(self.manager.last_mouse_pos, click_pos)
        # self.assertEqual(self.manager._card_under_mouse, test_card_set[0])

        clicked_events = pygame.event.get([CARDSSET_CLICKED])
        self.assertEqual(len(clicked_events), 1)

    def test_dragging(self):
        # TODO implement
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    unittest.main()
