"""Class for representing a game and its content."""


from pathlib import Path
from pygame_cards.set import CardsSet


class Game:
    name: str
    contents_directory: Path

    card_set: CardsSet

    content_download_link: None | str

    def __init__(
        self, name: str, card_set: CardsSet, content_download_link: None | str
    ) -> None:
        pass
