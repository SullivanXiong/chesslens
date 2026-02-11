"""
Playstyle classifier for ChessLens.

Classifies players into archetypes based on their playing style and generates
radar charts for visualization.
"""

from dataclasses import dataclass


@dataclass
class RadarAxis:
    """A single axis on the radar chart."""

    label: str
    value: float


@dataclass
class PlaystyleResult:
    """Complete playstyle classification result."""

    primary_archetype: str
    secondary_archetype: str
    archetype_scores: dict[str, float]
    radar_chart: list[RadarAxis]
    description: str


ARCHETYPES = {
    "The Attacker": {
        "description": "Aggressive player who seeks initiative through captures, checks, and sacrifices",
        "weights": {
            "capture_rate": 0.3,
            "check_frequency": 0.2,
            "sacrifice_rate": 0.2,
            "avg_think_time": -0.15,  # Inverted: faster = more attacking
            "decisive_game_rate": 0.15,
        },
    },
    "The Defender": {
        "description": "Solid player who prioritizes safety and accuracy over aggression",
        "weights": {
            "avg_centipawn_loss": -0.35,  # Inverted: lower = better
            "blunder_rate": -0.3,  # Inverted
            "capture_rate": -0.15,
            "decisive_game_rate": -0.2,
        },
    },
    "The Positional Player": {
        "description": "Strategic player who builds advantages through center control and piece placement",
        "weights": {
            "center_control": 0.3,
            "piece_activity": 0.25,
            "endgame_frequency": 0.2,
            "avg_centipawn_loss": -0.25,  # Inverted
        },
    },
    "The Speedster": {
        "description": "Fast, intuitive player who relies on pattern recognition but may rush",
        "weights": {
            "avg_think_time": -0.35,  # Inverted: faster
            "think_time_variance": -0.2,  # Inverted: more consistent
            "time_pressure_blunder_rate": 0.25,
            "blunder_rate": 0.2,
        },
    },
    "The Improviser": {
        "description": "Creative player with wide opening repertoire but inconsistent results",
        "weights": {
            "think_time_variance": 0.3,
            "sacrifice_rate": 0.25,
            "capture_rate": 0.2,
            "avg_centipawn_loss": 0.15,  # Higher variance = more improvising
        },
    },
    "The Grinder": {
        "description": "Patient player who wins through endgame technique and attrition",
        "weights": {
            "game_length": 0.3,
            "endgame_frequency": 0.3,
            "acpl_endgame": -0.2,  # Inverted: better endgame play
            "decisive_game_rate": 0.2,
        },
    },
}


class PlaystyleClassifier:
    """Classify player playstyle into archetypes."""

    def classify(self, normalized_features: dict[str, float]) -> PlaystyleResult:
        """
        Classify playstyle based on normalized features.

        Args:
            normalized_features: Dictionary of feature names to normalized values (0-1)

        Returns:
            PlaystyleResult with primary/secondary archetypes and radar chart
        """
        scores = {}
        for archetype, config in ARCHETYPES.items():
            score = 0.0
            for feat, weight in config["weights"].items():
                feat_value = normalized_features.get(feat, 0.5)
                if weight < 0:
                    score += abs(weight) * (1.0 - feat_value)
                else:
                    score += weight * feat_value
            scores[archetype] = score

        total = sum(scores.values())
        if total > 0:
            percentages = {k: (v / total) * 100 for k, v in scores.items()}
        else:
            percentages = {k: 100 / len(scores) for k in scores}

        sorted_archetypes = sorted(scores, key=scores.get, reverse=True)
        primary = sorted_archetypes[0]
        secondary = sorted_archetypes[1]

        radar = self._build_radar(normalized_features)

        return PlaystyleResult(
            primary_archetype=primary,
            secondary_archetype=secondary,
            archetype_scores=percentages,
            radar_chart=radar,
            description=ARCHETYPES[primary]["description"],
        )

    def _build_radar(self, features: dict[str, float]) -> list[RadarAxis]:
        """
        Build radar chart data from normalized features.

        Args:
            features: Dictionary of normalized feature values (0-1)

        Returns:
            List of RadarAxis objects for chart visualization
        """

        def _avg(*keys: str) -> float:
            values = [features.get(k, 0.5) for k in keys]
            return (sum(values) / len(values)) * 100

        return [
            RadarAxis(
                label="Aggression",
                value=_avg("capture_rate", "check_frequency", "sacrifice_rate"),
            ),
            RadarAxis(
                label="Accuracy",
                value=(1.0 - features.get("avg_centipawn_loss", 0.5)) * 100,
            ),
            RadarAxis(
                label="Positional", value=_avg("center_control", "piece_activity")
            ),
            RadarAxis(
                label="Endgame", value=_avg("endgame_frequency", "acpl_endgame")
            ),
            RadarAxis(
                label="Speed", value=(1.0 - features.get("avg_think_time", 0.5)) * 100
            ),
            RadarAxis(
                label="Creativity",
                value=_avg("sacrifice_rate", "think_time_variance"),
            ),
        ]
