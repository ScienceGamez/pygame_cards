"""An example of game: solitaire-klondike."""
from dataclasses import dataclass, field
from functools import cached_property
import sys
import pygame

from pygame_cards.hands import (
    HorizontalPileGraphic,
    VerticalPileGraphic,
)
from pygame_cards.manager import CardSetRights, CardsManager
from pygame_cards.deck import CardBackOwner, Deck

from pygame_cards.set import CardsSet
from pygame_cards.classics import CardSets, NumberCard, Level, Colors
from pygame_cards.abstract import AbstractCard
import pygame_cards.events


pygame.init()


screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
size = width, height = screen.get_size()


manager = CardsManager()


@dataclass
class ClondikePileGaphics(VerticalPileGraphic, CardBackOwner):
    """Show a column in clondike.

    All cards are hidden but the last one is shown.
    """

    _n_cards_hidden: pygame.Surface = field(init=False)

    def __post_init__(self):
        super().__post_init__()

        self._n_cards_hidden = len(self.cardset) - 1

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

    def _get_card_index_at(self, pos: tuple[int, int]) -> int | None:
        idx = super()._get_card_index_at(pos)
        if (
            idx is None
            or self._n_cards_hidden >= len(self.cardset)
            or idx < self._n_cards_hidden
        ):
            return None
        else:
            return idx

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
piles_card_sets: list[CardSets] = []
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
        (pile_size[0] * (pile + 1), card_size[1] * 1.5),
        CardSetRights(
            draggable_in=this_pile_graphics.can_put,
            draggable_out=True,
            highlight_hovered_card=True,
            clickable=True,
            drag_multiple_cards=True,
        ),
    )

deck = Deck(
    CardsSet(card_set[next_card_idx:]),
    card_size=card_size,
    size=(card_size[0] + 40, card_size[1] + 40),
)

temp_3_cards = HorizontalPileGraphic(
    CardsSet(),
    card_size=card_size,
    size=(2 * card_size[0], card_size[1] + 40),
)
# Will store the 3 cards group
temp_3_cards_storage: list[CardsSet] = []

manager.add_set(
    deck,
    (screen.get_size()[0] - deck.size[1] - deck.card_border_radius, 50),
    CardSetRights(
        clickable=True,
        draggable_in=False,
        draggable_out=False,
    ),
)
manager.add_set(
    temp_3_cards,
    (screen.get_size()[0] - 2 * deck.size[1] - deck.card_border_radius, 50),
    CardSetRights(
        clickable=True,
        draggable_in=False,
        # Only the last card can be used
        draggable_out=lambda card: card == temp_3_cards.cardset[-1]
        if temp_3_cards.cardset
        else True,
    ),
)

depots: dict[Colors, ClondikeDepotPileGaphics] = {}
for i, color in enumerate(Colors):
    depot = ClondikeDepotPileGaphics(
        CardsSet(), color=color, card_size=card_size, size=card_size
    )
    manager.add_set(
        depot,
        (30 + i * card_size[0] * 1.3, 50),
        CardSetRights(draggable_in=depot.can_put, draggable_out=False),
    )
    depots[color] = depot


pygame.display.flip()

clock = pygame.time.Clock()

tick = 0
while 1:
    # pygame.image.save(screen, "solitaire.png")
    screen.fill("black")
    time_delta = clock.tick(60)

    tick += 1

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                sys.exit()
            case pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:

                    sys.exit()
            case pygame_cards.events.CARD_MOVED:
                from_set = event.from_set
                if isinstance(from_set, ClondikePileGaphics):
                    from_set.turn_top_card()
                if (
                    from_set == temp_3_cards
                    and len(temp_3_cards.cardset) == 0
                    and len(temp_3_cards_storage) > 0
                ):
                    # In case the 3 card storage is empty, take the old cards
                    temp_3_cards.extend_cards(temp_3_cards_storage.pop(-1))
            case pygame_cards.events.CARDSSET_CLICKED:
                card = event.card
                set = event.set
                if isinstance(card, NumberCard) and (
                    isinstance(set, ClondikePileGaphics) or set == temp_3_cards
                ):
                    # Check if it can be stored in the packs
                    depot = depots[card.color]
                    if depot.can_put(card):

                        depot.append_card(card)
                        set.remove_card(card)
                        if isinstance(set, ClondikePileGaphics):
                            set.turn_top_card()

                if set == deck:
                    if len(deck.cardset) == 0:
                        while temp_3_cards_storage:
                            deck.extend_cards(temp_3_cards_storage.pop(0))
                        deck.extend_cards(temp_3_cards.remove_all_cards())

                    else:
                        if temp_3_cards.cardset:
                            # Put away the cards
                            temp_3_cards_storage.append(
                                temp_3_cards.cardset.draw(-1)
                            )
                        cards = deck.draw_cards(min(3, len(deck.cardset)))
                        temp_3_cards.extend_cards(cards)

        manager.process_events(event)

    manager.update(time_delta)
    manager.draw(screen)
    pygame.display.flip()
