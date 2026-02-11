"""
Feature extractor for ChessLens.

Extracts numeric features from analyzed games for playstyle classification
and machine learning applications.
"""

import chess
from dataclasses import dataclass, field
from statistics import mean, stdev


@dataclass
class GameFeatures:
    """Numeric features extracted from a single analyzed game."""

    # Accuracy
    avg_centipawn_loss: float = 0.0
    acpl_opening: float = 0.0
    acpl_middlegame: float = 0.0
    acpl_endgame: float = 0.0
    blunder_rate: float = 0.0

    # Aggression
    capture_rate: float = 0.0
    check_frequency: float = 0.0
    sacrifice_rate: float = 0.0

    # Positional
    center_control: float = 0.0
    piece_activity: float = 0.0

    # Time management
    avg_think_time: float = 0.0
    think_time_variance: float = 0.0
    time_pressure_blunder_rate: float = 0.0

    # Opening
    opening_repertoire_breadth: int = 0
    book_deviation_move: int = 0

    # Endgame
    endgame_frequency: float = 0.0
    game_length: int = 0

    # Results
    decisive_game_rate: float = 0.0


CENTER_SQUARES = [chess.E4, chess.D4, chess.E5, chess.D5]


class FeatureExtractor:
    """Extract per-game numeric features for playstyle classification."""

    def extract(
        self,
        move_evaluations: list[dict],
        player_color: str,
        total_moves: int,
    ) -> GameFeatures:
        """
        Extract features from move evaluation data for a single game.

        Args:
            move_evaluations: list of dicts with keys matching MoveEvaluation fields
            player_color: "white" or "black"
            total_moves: Total number of moves in the game

        Returns:
            GameFeatures object with extracted features
        """
        is_player_white = player_color == "white"
        features = GameFeatures()
        features.game_length = total_moves

        player_losses: list[int] = []
        phase_losses: dict[str, list[int]] = {
            "opening": [],
            "middlegame": [],
            "endgame": [],
        }
        think_times: list[float] = []
        captures = 0
        checks = 0
        blunders = 0
        player_moves = 0
        time_pressure_moves = 0
        time_pressure_blunders = 0

        for ev in move_evaluations:
            is_player_move = ev["is_white"] == is_player_white
            if not is_player_move:
                continue

            player_moves += 1
            cp_loss = ev.get("centipawn_loss", 0)
            player_losses.append(cp_loss)

            phase = ev.get("game_phase", "middlegame")
            if phase in phase_losses:
                phase_losses[phase].append(cp_loss)

            classification = ev.get("classification", "good")
            if classification in ("blunder", "mistake"):
                blunders += 1

            # Check for captures and checks using SAN
            san = ev.get("san", "")
            if "x" in san:
                captures += 1
            if "+" in san or "#" in san:
                checks += 1

            # Time management
            clock = ev.get("clock_seconds")
            if clock is not None:
                think_times.append(clock)
                if clock < 60:
                    time_pressure_moves += 1
                    if classification in ("blunder", "mistake"):
                        time_pressure_blunders += 1

        if player_moves == 0:
            return features

        features.avg_centipawn_loss = mean(player_losses) if player_losses else 0
        features.acpl_opening = (
            mean(phase_losses["opening"]) if phase_losses["opening"] else 0
        )
        features.acpl_middlegame = (
            mean(phase_losses["middlegame"]) if phase_losses["middlegame"] else 0
        )
        features.acpl_endgame = (
            mean(phase_losses["endgame"]) if phase_losses["endgame"] else 0
        )
        features.blunder_rate = blunders / player_moves
        features.capture_rate = captures / player_moves
        features.check_frequency = checks / player_moves
        features.endgame_frequency = 1.0 if phase_losses["endgame"] else 0.0

        if think_times and len(think_times) > 1:
            # Calculate time per move (deltas between consecutive clocks)
            deltas = []
            for i in range(1, len(think_times)):
                delta = think_times[i - 1] - think_times[i]
                if delta > 0:
                    deltas.append(delta)
            if deltas:
                features.avg_think_time = mean(deltas)
                features.think_time_variance = stdev(deltas) if len(deltas) > 1 else 0

        features.time_pressure_blunder_rate = time_pressure_blunders / max(
            1, time_pressure_moves
        )

        return features


class AggregatedFeatures:
    """Aggregate per-game features into player-level statistics."""

    def __init__(self):
        """Initialize empty aggregated features."""
        self.means: dict[str, float] = {}

    @classmethod
    def from_games(cls, game_features_list: list[GameFeatures]) -> "AggregatedFeatures":
        """
        Aggregate features from multiple games.

        Args:
            game_features_list: List of GameFeatures objects

        Returns:
            AggregatedFeatures with mean values across all games
        """
        agg = cls()
        if not game_features_list:
            return agg

        feature_names = [
            "avg_centipawn_loss",
            "acpl_opening",
            "acpl_middlegame",
            "acpl_endgame",
            "blunder_rate",
            "capture_rate",
            "check_frequency",
            "sacrifice_rate",
            "center_control",
            "piece_activity",
            "avg_think_time",
            "think_time_variance",
            "time_pressure_blunder_rate",
            "endgame_frequency",
            "game_length",
            "decisive_game_rate",
        ]

        for name in feature_names:
            values = [getattr(gf, name) for gf in game_features_list]
            agg.means[name] = mean(values) if values else 0.0

        return agg

    def to_normalized_dict(self) -> dict[str, float]:
        """
        Normalize features to 0-1 range using known reasonable ranges.

        Returns:
            Dictionary of feature names to normalized values (0-1)
        """
        ranges = {
            "avg_centipawn_loss": (0, 200),
            "acpl_opening": (0, 200),
            "acpl_middlegame": (0, 200),
            "acpl_endgame": (0, 200),
            "blunder_rate": (0, 0.3),
            "capture_rate": (0, 0.5),
            "check_frequency": (0, 0.15),
            "sacrifice_rate": (0, 0.1),
            "center_control": (0, 4),
            "piece_activity": (0, 50),
            "avg_think_time": (0, 60),
            "think_time_variance": (0, 30),
            "time_pressure_blunder_rate": (0, 0.5),
            "endgame_frequency": (0, 1),
            "game_length": (0, 120),
            "decisive_game_rate": (0, 1),
        }

        result = {}
        for name, value in self.means.items():
            min_val, max_val = ranges.get(name, (0, 1))
            if max_val > min_val:
                normalized = (value - min_val) / (max_val - min_val)
                result[name] = max(0.0, min(1.0, normalized))
            else:
                result[name] = 0.0
        return result
