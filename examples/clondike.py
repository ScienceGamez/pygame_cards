"""This is the first game we implement."""
from ast import Num
from dataclasses import dataclass, field
from functools import cached_property
import sys
import pygame

from pygame_cards.back import CARD_BACK
from pygame_cards.hands import AlignedHand
from pygame_cards.manager import CardSetRights, CardsManager
from pygame_cards.hands import CardsetGraphic
from pygame_cards.deck import CardBackOwner, Deck

from pygame_cards.set import CardsSet
from pygame_cards.classics import CardSets, NumberCard, Level, Colors
from pygame_cards.abstract import AbstractCard
import pygame_cards.events


pygame.init()


screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
# screen = pygame.display.set_mode((400, 300))
size = width, height = screen.get_size()


manager = CardsManager()


@dataclass
class ClondikePileGaphics(CardBackOwner):
    """Show a column in clondike.

    All cards are hidden but the last one is shown.

    :attr v_offset: The offset between cards in vertical.
    """

    v_offset: int = 30

    _n_cards_hidden: pygame.Surface = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self._n_cards_hidden = len(self.cardset) - 1

    def clear_cache(self) -> None:
        # Remove the surface cache_property if exists
        self.__dict__.pop("y_positions", None)
        super().clear_cache()

    @cached_property
    def surface(self) -> pygame.Surface:

        # Create the surface
        surf = pygame.Surface(self.size)

        # Calculate how we position the cards
        n_cards = len(self.cardset)
        if n_cards == 0:
            return surf

        x_position = (self.size[0] - self.card_size[0]) / 2

        # Add the cards on the surface
        for i in range(self._n_cards_hidden):
            surf.blit(self.card_back, (x_position, self.y_positions[i]))
        for j in range(self._n_cards_hidden, n_cards):
            surf.blit(
                self.cardset[j].graphics.surface,
                (x_position, self.y_positions[j]),
            )

        return surf

    @cached_property
    def y_positions(self) -> list[int]:
        n_cards = len(self.cardset)
        expected_h = n_cards * self.v_offset + self.card_size[1]
        h_space = (
            (self.size[1] - self.card_size[1]) / n_cards
            if expected_h > self.size[1]
            else self.v_offset
        )
        return [i * h_space for i in range(n_cards)]

    def get_card_at(self, pos: tuple[int, int]) -> AbstractCard:
        """Return the card at the given pixel position

        :arg pos: The position inside the CardsetGraphic surface.
        """
        if self.cardset:
            return self.cardset[-1]
        else:
            return None

    def remove_card(self, card: AbstractCard) -> None:

        return super().remove_card(card)

    def can_put(self, card: NumberCard) -> bool:
        if not isinstance(card, NumberCard):
            raise TypeError("Clondike pile only accepts number cards")
        if not self.cardset:
            # If empty can put any card we want
            return True
        last_card: NumberCard = self.cardset[-1]
        black_colors = [Colors.CLUB, Colors.SPADE]
        if (
            card.color in black_colors and last_card.color in black_colors
        ) or (
            card.color not in black_colors
            and last_card.color not in black_colors
        ):
            # Color should be different
            return False

        # Check if the number is one smaller
        return card.is_one_level_less_than(last_card, as_equals_1=True)

    def turn_top_card(self):
        # Turn the top card only if all the cards were hiddent
        if self._n_cards_hidden == len(self.cardset):
            self._n_cards_hidden -= 1
        self.clear_cache()


@dataclass
class ClondikeDepotPileGaphics(Deck):
    """Show a pile where you put the cards.

    All cards are hidden but the last one is shown.

    :attr color: The Color of this pile.
    """

    color: Colors = None

    @cached_property
    def surface(self):
        if len(self.cardset) == 0:
            return super().surface
        else:
            return self.cardset[-1].graphics.surface

    def can_put(self, card: NumberCard) -> bool:
        if card.color != self.color:
            return False
        if len(self.cardset) == 0:
            return card.number == Level.AS
        last_card: NumberCard = self.cardset[-1]
        return last_card.is_one_level_less_than(card, as_equals_1=True)


card_set = CardSets.n52
card_set.shuffle()

N_PILES = 7

pile_size = (width / (N_PILES + 2), height * 0.8)
card_size = (pile_size[0] * 0.8, pile_size[1] / 3)

# Get the card set of each pile
piles_card_sets = []
piles_graphics = []
card_idx = 0
for pile in range(N_PILES):
    # Piles increase in size all the time
    next_card_idx = card_idx + pile + 1
    piles_card_sets.append(card_set[card_idx:next_card_idx])
    card_idx = next_card_idx
    this_pile_graphics = ClondikePileGaphics(
        piles_card_sets[-1], pile_size, card_size
    )
    piles_graphics.append(this_pile_graphics)

    # Finally add the set to the manager
    manager.add_set(
        this_pile_graphics,
        # Position on the screen
        (pile_size[0] * (pile + 1), height * 0.2),
        CardSetRights(
            draggable_in=this_pile_graphics.can_put,
            draggable_out=True,
            highlight_hovered_card=True,
            clickable=True,
        ),
    )

depots: dict[Colors, ClondikeDepotPileGaphics] = {}
for i, color in enumerate(Colors):
    depot = ClondikeDepotPileGaphics(
        CardsSet(), color=color, card_size=card_size, size=card_size
    )
    manager.add_set(
        depot,
        (i * card_size[0] * 1.5, 0),
        CardSetRights(draggable_in=depot.can_put, draggable_out=False),
    )
    depots[color] = depot


pygame.display.flip()

clock = pygame.time.Clock()


while 1:
    screen.fill("black")
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                sys.exit()
            case pygame.KEYDOWN | pygame.K_ESCAPE:
                sys.exit()
            case pygame_cards.events.CARD_MOVED:
                from_set = event.from_set
                if isinstance(from_set, ClondikePileGaphics):
                    from_set.turn_top_card()
            case pygame_cards.events.CARDSSET_CLICKED:
                card = event.card
                set = event.set
                if isinstance(card, NumberCard) and isinstance(
                    set, ClondikePileGaphics
                ):
                    # Check if it can be stored in the packs
                    depot = depots[card.color]
                    if depot.can_put(card):

                        depot.append_card(card)
                        set.remove_card(card)
                        set.turn_top_card()

        manager.process_events(event)

    manager.update(time_delta)
    manager.draw(screen)
    pygame.display.flip()
