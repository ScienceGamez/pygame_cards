import logging
from pathlib import Path
import unittest
from pygame_cards.abstract import AbstractCard
from pygame_cards.io.json import from_json
from pygame_cards.set import CardsSet


def get_set_of_size(n: int) -> CardsSet:
    """Return a set with the desired size."""
    return CardsSet([AbstractCard(f"{i}") for i in range(n)])


class TestCard(unittest.TestCase):
    def test_create(self):
        s = CardsSet([AbstractCard("A")])
        self.assertEqual(len(s), 1)

    def test_list_stuff(self):
        s = CardsSet([AbstractCard("A")])
        s.append(AbstractCard("A"))
        self.assertEqual(len(s), 2)

    def test_check_type(self):
        s = CardsSet([AbstractCard("A")])
        self.assertTrue(s.check_cards())
        s.append(AbstractCard("A"))
        self.assertTrue(s.check_cards())
        s.append(1)
        # now is false
        self.assertFalse(s.check_cards())

    def test_join(self):
        """Test the join methods, that merges sets togehter"""
        s1 = CardsSet([AbstractCard("A")])
        s2 = CardsSet([AbstractCard("A"), AbstractCard("B")])

        s = CardsSet.join(s1, s2)
        self.assertEqual(len(s), 3)

    def test_cards_per_set(self):
        s = get_set_of_size(10)
        self.assertEqual(s._find_ncards_per_set(1, None), 10)
        self.assertEqual(s._find_ncards_per_set(2, None), 5)
        self.assertEqual(s._find_ncards_per_set(3, None), 3)
        self.assertEqual(s._find_ncards_per_set(4, None), 2)
        self.assertEqual(s._find_ncards_per_set(5, None), 2)
        self.assertEqual(s._find_ncards_per_set(6, None), 1)

        self.assertEqual(s._find_ncards_per_set(3, 2), 2)
        self.assertEqual(s._find_ncards_per_set(3, 3), 3)
        self.assertEqual(s._find_ncards_per_set(2, 5), 5)

        self.assertRaises(ValueError, s._find_ncards_per_set, 3, 4)

    def test_distribute(self):
        """Test that the cards are correctly distributed"""
        n = 10
        s = CardsSet([AbstractCard(f"{i}") for i in range(n)])
        card_sets = s.distribute(2)

        self.assertEqual(len(card_sets), 2)
        for set in card_sets:
            self.assertEqual(len(set), 5)
        # Put all the cards together
        all_cards_after_shuffle = CardsSet.join(*card_sets)
        for card in s:
            self.assertIn(card, all_cards_after_shuffle)

    def test_draw(self):
        s = CardsSet(
            [
                a := AbstractCard("A"),
                b := AbstractCard("B"),
                c := AbstractCard("C"),
            ]
        )
        drawn = s.draw(2)
        self.assertListEqual(drawn, [a, b])
        self.assertListEqual(s, [c])

    def test_distribute_withleftovers(self):
        """Test that the cards are correctly distributed"""
        n = 13
        s = get_set_of_size(n)
        original_s = s.copy()
        card_sets = s.distribute(4)

        # Should be 4 sets of 3 cards
        self.assertEqual(len(card_sets), 4)
        for set in card_sets:
            self.assertEqual(len(set), 3)

        self.assertEqual(len(s), 1)  # One card leftover
        # Put all the cards together
        all_cards_after_shuffle = CardsSet.join(*card_sets)
        for card in original_s:
            self.assertIn(card, all_cards_after_shuffle + s)
        # Make sure the leftover were not distributed
        for card in s:
            self.assertNotIn(card, all_cards_after_shuffle)

    def test_distribute_to_withleftovers(self):
        """Test that the cards are correctly distributed"""
        n = 13
        s = get_set_of_size(n)
        original_s = s.copy()

        sets = [
            CardsSet(
                [
                    a := AbstractCard("A"),
                    b := AbstractCard("B"),
                    c := AbstractCard("C"),
                ]
            ),
            CardsSet(
                [
                    a2 := AbstractCard("A"),
                ],
            ),
            CardsSet(),
            CardsSet(),
        ]
        s.distribute_to(sets)

        # Should be 4 sets
        self.assertEqual(len(sets), 4)
        for set, expected_size in zip(sets, [6, 4, 3, 3]):
            self.assertEqual(len(set), expected_size)

        self.assertEqual(len(s), 1)  # One card leftover
        # Put all the cards together
        all_cards_after_shuffle = CardsSet.join(*sets)
        for card in original_s:
            self.assertIn(card, all_cards_after_shuffle + s)
        # Make sure the leftover were not distributed
        for card in s:
            self.assertNotIn(card, all_cards_after_shuffle)


class TestSaving(unittest.TestCase):
    test_file = Path("testcardsetsaving.json")

    set_card_type = AbstractCard
    set_type = CardsSet

    def setUp(self) -> None:
        # Make sure the file does not exist
        self.test_file.unlink(missing_ok=True)

    def tearDown(self):
        # Make sure the file is destroyed
        self.test_file.unlink(missing_ok=True)

    def test_jsonable(self):
        """Make sure the cards set can be saved."""
        cards_set = get_set_of_size(5)
        cards_set.to_json(self.test_file)
        self.assertTrue(self.test_file.is_file())

    def test_loads_from_json(self):
        cards_set = get_set_of_size(5)
        cards_set.to_json(self.test_file)
        loaded_set = from_json(self.test_file, self.set_card_type)

    def test_is_same(self):
        """Check that when we reload the cards set, it has the same cards."""
        cards_set = get_set_of_size(5)
        cards_set.to_json(self.test_file)
        loaded_set = from_json(self.test_file, self.set_card_type)
        for card1, card2 in zip(cards_set, loaded_set):
            self.assertEqual(card1.name, card2.name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
