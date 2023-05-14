"""Shared content for the game."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Any

import pygame
from pygame_emojis import load_emoji
from pygame_cards.hands import AlignedHand
from pygame_cards.manager import CardSetRights, CardsManager

import pygame_cards.events

from pygame_cards.set import CardsSet
from pygame_cards.abstract import AbstractCard, AbstractCardGraphics


class Sign(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

    # Override the > method to allow comparison between the signs
    def __gt__(self, other: Sign) -> bool:
        if self == Sign.ROCK:
            return other == Sign.SCISSORS
        if self == Sign.PAPER:
            return other == Sign.ROCK
        if self == Sign.SCISSORS:
            return other == Sign.PAPER

        return False


class Player(Enum):
    PLAYER1 = "player1"
    PLAYER2 = "player2"


EMOJI_TO_USE: dict[Sign, str] = {
    Sign.ROCK: "🪨",
    Sign.PAPER: "📄",
    Sign.SCISSORS: "✂️",
}


@dataclass
class RockPaperScisorsGraphics(AbstractCardGraphics):
    card: RockPaperScissorsCard

    @cached_property
    def surface(self) -> pygame.Surface:
        # Transparent background
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)

        # Load the emoji as a pygame.Surface
        emoji = EMOJI_TO_USE[self.card.sign]
        surface = load_emoji(emoji, self.size)
        # Draw the emoji
        surf.blit(surface, (0, 0))

        return surf


@dataclass
class RockPaperScissorsCard(AbstractCard):
    sign: Sign
    graphics_type = RockPaperScisorsGraphics


ROCK_PAPER_SCISSORS_CARDSET = CardsSet(
    # Iterate over enum to create the cards
    [RockPaperScissorsCard(sign=sign, name=sign.value) for sign in Sign]
)


class RockPaperScissors:
    """
    A Rock paper scisors game.

    Play plays with :meth:`play`.

    Get past moves with :attr:`moves`.

    """

    def __init__(self):
        self.curent_moves: dict[Player, Sign] = {}
        self.points: dict[Player, int] = {Player.PLAYER1: 0, Player.PLAYER2: 0}
        self.points_to_win = 3

        self.past_moves: list[tuple(Player, Sign)] = []

        self.players = []

    def play(self, player: Player, event: Any) -> Any | None:
        """player plays sign

        Gets an event from a play message.

        Returns a message (json serializable object),
        to be broadcasted to all players or None,
        if nothing should be broadcasted.

        """
        if player in self.curent_moves:
            raise RuntimeError("Already played, waiting for other player.")

        try:
            sign = Sign(event)
        except ValueError:
            raise RuntimeError(f"Invalid sign {event}. Accepted values are in {Sign}")

        self.curent_moves[player] = sign
        self.past_moves.append((player, sign))
        if len(self.curent_moves) < 2:
            # Wait for other player
            return None

        # Both players played
        player1_sign = self.curent_moves[Player.PLAYER1]
        player2_sign = self.curent_moves[Player.PLAYER2]

        # Reset the current moves
        self.curent_moves = {}

        # Check who won
        if player1_sign == player2_sign:
            winner = None
        else:
            if player1_sign > player2_sign:
                winner = Player.PLAYER1
            else:
                winner = Player.PLAYER2

            self.points[winner] += 1

            if self.points[winner] >= self.points_to_win:
                # If move is winning, send a "win" message.
                return {
                    "type": "win",
                    "player": winner.value,
                }

        # Send a "results" message to update the UI.
        return {
            "type": "results",
            "winner": winner.value if winner else None,
        }

    def get_past_events(self) -> list[str]:
        """Returns a list of past moves as strings."""
        return [f"{player.value},{sign.value}" for player, sign in self.past_moves]

    def add_player(self) -> Player:
        """Add a player to the game."""

        if len(self.players) >= 2:
            raise RuntimeError("Already 2 players")

        player = Player(f"player{len(self.players)+1}")
        self.players.append(player)
        return player


if __name__ == "__main__":
    sing = Sign("rock")
    print(sing)
