"""
Enums for ChessLens chess analysis app.

Defines game phases, move classifications, time controls,
game results, and player archetypes.
"""

from enum import Enum


class GamePhase(str, Enum):
    """Phases of a chess game."""

    OPENING = "opening"
    MIDDLEGAME = "middlegame"
    ENDGAME = "endgame"


class MoveClassification(str, Enum):
    """Classification of chess moves based on evaluation."""

    BRILLIANT = "brilliant"
    GOOD = "good"
    BOOK = "book"
    INACCURACY = "inaccuracy"
    MISTAKE = "mistake"
    BLUNDER = "blunder"


class TimeClass(str, Enum):
    """Time control classes for chess games."""

    BULLET = "bullet"
    BLITZ = "blitz"
    RAPID = "rapid"
    CLASSICAL = "classical"
    DAILY = "daily"


class GameResult(str, Enum):
    """Game result from player's perspective."""

    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"


class Archetype(str, Enum):
    """Player playstyle archetypes."""

    THE_ATTACKER = "the_attacker"
    THE_DEFENDER = "the_defender"
    THE_POSITIONAL_PLAYER = "the_positional_player"
    THE_SPEEDSTER = "the_speedster"
    THE_IMPROVISER = "the_improviser"
    THE_GRINDER = "the_grinder"
