"""
Weakness detector for ChessLens.

Detects recurring blunder patterns, time trouble issues, and phase-specific
weaknesses from analyzed game data.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from statistics import mean

from chesslens.models.enums import GamePhase, MoveClassification

logger = logging.getLogger(__name__)


@dataclass
class RushingAnalysis:
    """Analysis of time trouble and rushing patterns."""

    blunder_rate_under_60s: float
    blunder_rate_over_60s: float
    time_trouble_multiplier: float
    verdict: str


@dataclass
class WeaknessReport:
    """Comprehensive weakness analysis report."""

    overall_blunder_rate: float
    phase_breakdown: dict[str, float]
    move_number_heatmap: dict[int, int]
    rushing_analysis: RushingAnalysis
    top_blunders: list[dict]
    recurring_patterns: list[str]


class WeaknessDetector:
    """Detect recurring weakness patterns from analyzed games."""

    def analyze(
        self,
        move_evaluations: list[dict],
        player_color_per_game: dict[int, str],
    ) -> WeaknessReport:
        """
        Analyze weaknesses from move evaluation data.

        Args:
            move_evaluations: list of dicts with keys: game_id, move_index, is_white,
                san, centipawn_loss, classification, game_phase, clock_seconds, fen_before
            player_color_per_game: {game_id: "white"/"black"}

        Returns:
            WeaknessReport with comprehensive weakness analysis
        """
        blunders_by_phase: dict[str, int] = defaultdict(int)
        moves_by_phase: dict[str, int] = defaultdict(int)
        blunders_by_move_number: dict[int, int] = defaultdict(int)
        time_blunders: list[tuple[float, int]] = []  # (clock_seconds, cp_loss)
        time_non_blunders: list[float] = []
        top_blunders: list[dict] = []
        total_player_moves = 0
        total_blunders = 0

        for ev in move_evaluations:
            game_id = ev["game_id"]
            player_color = player_color_per_game.get(game_id, "white")
            is_player_white = player_color == "white"
            is_player_move = ev["is_white"] == is_player_white

            if not is_player_move:
                continue

            total_player_moves += 1
            phase = ev.get("game_phase", "middlegame")
            moves_by_phase[phase] += 1
            classification = ev.get("classification", "good")

            is_blunder = classification in ("blunder", "mistake")
            if is_blunder:
                total_blunders += 1
                blunders_by_phase[phase] += 1
                move_num = (ev["move_index"] // 2) + 1
                blunders_by_move_number[move_num] += 1

                if ev.get("centipawn_loss", 0) > 100:
                    top_blunders.append(
                        {
                            "game_id": game_id,
                            "move_index": ev["move_index"],
                            "san": ev.get("san", ""),
                            "centipawn_loss": ev.get("centipawn_loss", 0),
                            "phase": phase,
                        }
                    )

            clock = ev.get("clock_seconds")
            if clock is not None:
                if is_blunder:
                    time_blunders.append((clock, ev.get("centipawn_loss", 0)))
                else:
                    time_non_blunders.append(clock)

        # Phase breakdown: blunder rate per phase
        phase_breakdown = {}
        for phase in ["opening", "middlegame", "endgame"]:
            total = moves_by_phase.get(phase, 0)
            blunders = blunders_by_phase.get(phase, 0)
            phase_breakdown[phase] = blunders / max(1, total)

        # Rushing analysis
        rushing = self._analyze_rushing(
            time_blunders, time_non_blunders, total_player_moves
        )

        # Sort top blunders
        top_blunders.sort(key=lambda x: x["centipawn_loss"], reverse=True)

        # Detect recurring patterns
        patterns = self._detect_patterns(
            phase_breakdown, rushing, blunders_by_move_number
        )

        return WeaknessReport(
            overall_blunder_rate=total_blunders / max(1, total_player_moves),
            phase_breakdown=phase_breakdown,
            move_number_heatmap=dict(blunders_by_move_number),
            rushing_analysis=rushing,
            top_blunders=top_blunders[:10],
            recurring_patterns=patterns,
        )

    def _analyze_rushing(
        self,
        time_blunders: list[tuple[float, int]],
        time_non_blunders: list[float],
        total_moves: int,
    ) -> RushingAnalysis:
        """
        Analyze relationship between time pressure and blunder rate.

        Args:
            time_blunders: List of (clock_seconds, cp_loss) for blunders
            time_non_blunders: List of clock_seconds for non-blunders
            total_moves: Total number of moves analyzed

        Returns:
            RushingAnalysis with time trouble statistics
        """
        threshold = 60.0  # seconds

        under_threshold_blunders = [t for t, _ in time_blunders if t < threshold]
        over_threshold_blunders = [t for t, _ in time_blunders if t >= threshold]
        under_threshold_nonblunders = [t for t in time_non_blunders if t < threshold]
        over_threshold_nonblunders = [t for t in time_non_blunders if t >= threshold]

        moves_under = len(under_threshold_blunders) + len(under_threshold_nonblunders)
        moves_over = len(over_threshold_blunders) + len(over_threshold_nonblunders)

        rate_under = len(under_threshold_blunders) / max(1, moves_under)
        rate_over = len(over_threshold_blunders) / max(1, moves_over)
        multiplier = rate_under / max(0.01, rate_over)

        if multiplier > 2.0:
            verdict = f"Your blunder rate is {multiplier:.1f}x higher when you have less than 60 seconds. Slow down!"
        elif multiplier > 1.5:
            verdict = "Time pressure slightly increases your blunder rate. Try to manage your clock better."
        else:
            verdict = "Your blunder rate is consistent regardless of time pressure."

        return RushingAnalysis(
            blunder_rate_under_60s=rate_under,
            blunder_rate_over_60s=rate_over,
            time_trouble_multiplier=multiplier,
            verdict=verdict,
        )

    def _detect_patterns(
        self,
        phase_breakdown: dict[str, float],
        rushing: RushingAnalysis,
        heatmap: dict[int, int],
    ) -> list[str]:
        """
        Detect recurring weakness patterns from aggregated data.

        Args:
            phase_breakdown: Blunder rate by game phase
            rushing: Time trouble analysis
            heatmap: Blunders by move number

        Returns:
            List of human-readable pattern descriptions
        """
        patterns = []

        # Worst phase
        worst_phase = max(phase_breakdown, key=phase_breakdown.get)
        if phase_breakdown[worst_phase] > 0.1:
            patterns.append(
                f"Most blunders occur in the {worst_phase} ({phase_breakdown[worst_phase]:.0%} blunder rate)"
            )

        # Rushing pattern
        if rushing.time_trouble_multiplier > 2.0:
            patterns.append(
                f"Blunder rate increases {rushing.time_trouble_multiplier:.1f}x in time trouble (under 60s)"
            )

        # Move number clusters
        if heatmap:
            peak_move = max(heatmap, key=heatmap.get)
            if heatmap[peak_move] >= 3:
                patterns.append(f"Blunders cluster around move {peak_move}")

        return patterns
