"""
Move classification module.

Classifies chess moves by centipawn loss into categories:
good, inaccuracy, mistake, or blunder.
"""

from chesslens.models.enums import MoveClassification


class MoveClassifier:
    """Classify moves based on centipawn loss."""

    def classify(self, centipawn_loss: int) -> MoveClassification:
        """
        Classify a move based on centipawn loss.

        Args:
            centipawn_loss: Centipawns lost by making this move (0 = best move)

        Returns:
            MoveClassification enum value
        """
        if centipawn_loss <= 0:
            return MoveClassification.GOOD
        elif centipawn_loss <= 10:
            return MoveClassification.GOOD
        elif centipawn_loss <= 50:
            return MoveClassification.INACCURACY
        elif centipawn_loss <= 100:
            return MoveClassification.MISTAKE
        else:
            return MoveClassification.BLUNDER
