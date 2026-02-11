"""
Analysis pipeline coordinator.

Ties together parsing, evaluation, and storage for complete game analysis.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from chesslens.models.db import Game, MoveEvaluation, AnalysisSummary
from chesslens.models.enums import MoveClassification
from chesslens.services.stockfish_analyzer import StockfishAnalyzer
from chesslens.services.pgn_parser import PgnParser

logger = logging.getLogger(__name__)


class AnalysisEngine:
    """Coordinates full game analysis pipeline: parse -> evaluate -> store."""

    def __init__(self, session: AsyncSession, http_client: httpx.AsyncClient):
        """
        Initialize analysis engine.

        Args:
            session: Database session for storing results
            http_client: HTTP client for Stockfish API requests
        """
        self._session = session
        self._analyzer = StockfishAnalyzer(http_client)
        self._parser = PgnParser()

    async def analyze_game(self, game: Game) -> AnalysisSummary:
        """
        Run full Stockfish analysis on a game and store results.

        Args:
            game: Game model instance with PGN data

        Returns:
            AnalysisSummary record with aggregate statistics

        Raises:
            ValueError: If PGN parsing fails
        """
        parsed = self._parser.parse(game.pgn)
        if parsed is None:
            raise ValueError(f"Failed to parse PGN for game {game.id}")

        result = await self._analyzer.analyze_game(parsed, game.player_color)

        # Store move evaluations
        for move_analysis in result.moves:
            eval_record = MoveEvaluation(
                game_id=game.id,
                move_index=move_analysis.ply,
                is_white=move_analysis.is_white,
                san=move_analysis.san,
                uci=move_analysis.uci,
                fen_before=move_analysis.fen_before,
                fen_after=move_analysis.fen_after,
                best_move_uci=move_analysis.best_move_uci,
                best_move_san=move_analysis.best_move_san,
                score_before_cp=move_analysis.score_before_cp,
                score_after_cp=move_analysis.score_after_cp,
                centipawn_loss=move_analysis.centipawn_loss,
                classification=move_analysis.classification,
                clock_seconds=move_analysis.clock_seconds,
                game_phase=move_analysis.game_phase,
                engine_line=move_analysis.engine_line,
            )
            self._session.add(eval_record)

        # Store analysis summary
        summary = AnalysisSummary(
            game_id=game.id,
            player_acpl=result.player_acpl,
            opponent_acpl=result.opponent_acpl,
            blunder_count=result.blunder_count,
            mistake_count=result.mistake_count,
            inaccuracy_count=result.inaccuracy_count,
            opening_acpl=result.opening_acpl,
            middlegame_acpl=result.middlegame_acpl,
            endgame_acpl=result.endgame_acpl,
        )
        self._session.add(summary)

        # Mark game as analyzed
        game.is_analyzed = True
        game.analyzed_at = datetime.now(timezone.utc)

        await self._session.flush()
        logger.info(
            f"Analysis complete for game {game.id}: "
            f"ACPL={result.player_acpl:.1f}, blunders={result.blunder_count}"
        )
        return summary
