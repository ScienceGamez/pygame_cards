"""Currently not used."""

from pathlib import Path
from pygame_cards.set import CardsSet


class Game:
    """Represent a game and its content."""

    name: str
    contents_directory: Path

    card_set: CardsSet

    content_download_link: None | str

    def __init__(
        self, name: str, card_set: CardsSet, content_download_link: None | str
    ) -> None:
        pass
