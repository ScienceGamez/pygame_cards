from pygame_cards.set import CardsSet


class DefaultCardsSet(CardsSet):
    name: str


def get_default_card_set(name: str) -> DefaultCardsSet:
    """This is a card set that the user already has installed in the package.

    This is useful for networking to specify the card set exists.
    """

    match name:
        case "n52":
            from pygame_cards.classics import CardSets

            return CardSets.n52
        case "n36":
            from pygame_cards.classics import CardSets

            return CardSets.n36
        case _:
            raise ValueError(f"Unkown card set with name {name}")
