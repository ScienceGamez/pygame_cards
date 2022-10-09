import unittest
from pygame_cards.abstract import AbstractCard


class TestCard(unittest.TestCase):
    def test_create(self):
        AbstractCard("A")

    def test_name(self):
        card = AbstractCard("A")
        self.assertEqual(card.name, "A")

    def test_uid_different(self):
        card = AbstractCard("A")
        card2 = AbstractCard("A")
        self.assertNotEqual(card.u_id, card2.u_id)

    def test_cannot_create_uuid(self):
        self.assertRaises(TypeError, AbstractCard, "A", u_id="sdf")

    def test_uid_not_exposed_in_dict(self):
        card = AbstractCard("A")
        self.assertIn("name", card.__dict__)


if __name__ == "__main__":
    unittest.main()
