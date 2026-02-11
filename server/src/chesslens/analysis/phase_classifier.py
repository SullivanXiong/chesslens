"""
Game phase classification module.

Classifies chess positions into opening, middlegame, or endgame based on
material count and move number.
"""

import chess
from chesslens.models.enums import GamePhase


class PhaseClassifier:
    """Classify game phase based on material and move number."""

    PIECE_VALUES = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }

    def classify(self, board: chess.Board, move_number: int) -> GamePhase:
        """
        Classify the current game phase.

        Args:
            board: Current board position
            move_number: Current move number (full moves, not ply)

        Returns:
            GamePhase enum value (OPENING, MIDDLEGAME, or ENDGAME)
        """
        material = self._total_material(board)

        if move_number <= 12 and material >= 60:
            return GamePhase.OPENING
        elif material <= 26:
            return GamePhase.ENDGAME
        else:
            return GamePhase.MIDDLEGAME

    def _total_material(self, board: chess.Board) -> int:
        """Calculate total material value on the board."""
        total = 0
        for piece_type, value in self.PIECE_VALUES.items():
            total += len(board.pieces(piece_type, chess.WHITE)) * value
            total += len(board.pieces(piece_type, chess.BLACK)) * value
        return total
