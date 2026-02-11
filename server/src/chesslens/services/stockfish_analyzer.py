"""
Stockfish game analysis orchestration.

Coordinates full game analysis using cloud Stockfish API.
"""

import asyncio
import logging
from dataclasses import dataclass, field
import chess
import httpx

from chesslens.analysis.position_evaluator import PositionEvaluator, EngineEval
from chesslens.analysis.move_classifier import MoveClassifier
from chesslens.analysis.phase_classifier import PhaseClassifier
from chesslens.services.pgn_parser import ParsedGame, ParsedMove
from chesslens.models.enums import MoveClassification, GamePhase

logger = logging.getLogger(__name__)


@dataclass
class MoveAnalysis:
    """Analysis result for a single move."""

    ply: int
    is_white: bool
    san: str
    uci: str
    fen_before: str
    fen_after: str
    best_move_uci: str
    best_move_san: str
    score_before_cp: int
    score_after_cp: int
    centipawn_loss: int
    classification: MoveClassification
    game_phase: GamePhase
    clock_seconds: float | None
    engine_line: list[str]


@dataclass
class GameAnalysisResult:
    """Complete analysis result for a game."""

    player_acpl: float
    opponent_acpl: float
    blunder_count: int
    mistake_count: int
    inaccuracy_count: int
    opening_acpl: float | None
    middlegame_acpl: float | None
    endgame_acpl: float | None
    moves: list[MoveAnalysis] = field(default_factory=list)


class StockfishAnalyzer:
    """Orchestrate full game analysis using cloud Stockfish."""

    REQUEST_DELAY = 0.05  # 50ms between requests to chess-api.com

    def __init__(self, http_client: httpx.AsyncClient):
        """
        Initialize Stockfish analyzer.

        Args:
            http_client: Async HTTP client for API requests
        """
        self._evaluator = PositionEvaluator(http_client)
        self._move_classifier = MoveClassifier()
        self._phase_classifier = PhaseClassifier()

    async def analyze_game(
        self, parsed_game: ParsedGame, player_color: str
    ) -> GameAnalysisResult:
        """
        Analyze all positions in a game.

        Args:
            parsed_game: Parsed game with moves and positions
            player_color: "white" or "black" - which side to analyze

        Returns:
            GameAnalysisResult with move-by-move analysis and summary statistics
        """
        is_player_white = player_color == "white"
        move_analyses: list[MoveAnalysis] = []

        player_losses: list[int] = []
        opponent_losses: list[int] = []
        phase_losses: dict[GamePhase, list[int]] = {
            GamePhase.OPENING: [],
            GamePhase.MIDDLEGAME: [],
            GamePhase.ENDGAME: [],
        }

        blunders = mistakes = inaccuracies = 0

        for i, move in enumerate(parsed_game.moves):
            # Evaluate position before this move
            eval_before = await self._evaluator.evaluate(move.fen_before)
            await asyncio.sleep(self.REQUEST_DELAY)

            # Evaluate position after this move
            eval_after = await self._evaluator.evaluate(move.fen_after)
            await asyncio.sleep(self.REQUEST_DELAY)

            # Calculate centipawn loss from mover's perspective
            if move.is_white:
                cp_loss = max(0, eval_before.score_cp - eval_after.score_cp)
            else:
                cp_loss = max(0, (-eval_before.score_cp) - (-eval_after.score_cp))

            # Cap at 1000
            cp_loss = min(cp_loss, 1000)

            classification = self._move_classifier.classify(cp_loss)
            board = chess.Board(move.fen_before)
            phase = self._phase_classifier.classify(board, move.move_number)

            is_player_move = move.is_white == is_player_white
            if is_player_move:
                player_losses.append(cp_loss)
                phase_losses[phase].append(cp_loss)
                if classification == MoveClassification.BLUNDER:
                    blunders += 1
                elif classification == MoveClassification.MISTAKE:
                    mistakes += 1
                elif classification == MoveClassification.INACCURACY:
                    inaccuracies += 1
            else:
                opponent_losses.append(cp_loss)

            move_analyses.append(
                MoveAnalysis(
                    ply=move.ply,
                    is_white=move.is_white,
                    san=move.san,
                    uci=move.uci,
                    fen_before=move.fen_before,
                    fen_after=move.fen_after,
                    best_move_uci=eval_before.best_move_uci,
                    best_move_san=eval_before.best_move_san,
                    score_before_cp=eval_before.score_cp,
                    score_after_cp=eval_after.score_cp,
                    centipawn_loss=cp_loss,
                    classification=classification,
                    game_phase=phase,
                    clock_seconds=move.clock_seconds,
                    engine_line=eval_before.principal_variation[:5],
                )
            )

            if (i + 1) % 10 == 0:
                logger.info(f"Analyzed {i + 1}/{len(parsed_game.moves)} moves")

        def _avg(lst: list[int]) -> float:
            return sum(lst) / len(lst) if lst else 0.0

        return GameAnalysisResult(
            player_acpl=_avg(player_losses),
            opponent_acpl=_avg(opponent_losses),
            blunder_count=blunders,
            mistake_count=mistakes,
            inaccuracy_count=inaccuracies,
            opening_acpl=_avg(phase_losses[GamePhase.OPENING])
            if phase_losses[GamePhase.OPENING]
            else None,
            middlegame_acpl=_avg(phase_losses[GamePhase.MIDDLEGAME])
            if phase_losses[GamePhase.MIDDLEGAME]
            else None,
            endgame_acpl=_avg(phase_losses[GamePhase.ENDGAME])
            if phase_losses[GamePhase.ENDGAME]
            else None,
            moves=move_analyses,
        )
