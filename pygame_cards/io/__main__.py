import logging


if __name__ == "__main__":
    from pygame_cards.abstract import AbstractCard
    from pygame_cards.set import CardsSet

    from pygame_cards.io.utils import _logger, to_json

    _logger.setLevel(logging.DEBUG)
    _logger.handlers.append(logging.StreamHandler())
    obj = AbstractCard("a")
    obj = CardsSet([AbstractCard("a"), AbstractCard("b"), AbstractCard("b")])
    print(obj)
    print(obj.__dict__)
    print(to_json(obj))
