"""
Position evaluation module using chess-api.com.

Provides Stockfish 17 NNUE evaluation via free cloud API.
"""

import httpx
from dataclasses import dataclass


@dataclass
class EngineEval:
    """Result of a single position evaluation."""

    score_cp: int  # Centipawns from white's perspective
    best_move_uci: str
    best_move_san: str
    mate_in: int | None
    principal_variation: list[str]
    depth: int


class PositionEvaluator:
    """Evaluate chess positions using chess-api.com (free Stockfish 17 NNUE)."""

    API_URL = "https://chess-api.com/v1"

    def __init__(self, http_client: httpx.AsyncClient):
        """
        Initialize position evaluator.

        Args:
            http_client: Async HTTP client for making API requests
        """
        self._client = http_client

    async def evaluate(self, fen: str, depth: int = 16) -> EngineEval:
        """
        Evaluate a chess position.

        Args:
            fen: Position in FEN notation
            depth: Search depth (max 18 for chess-api.com)

        Returns:
            EngineEval with score, best move, and principal variation

        Raises:
            httpx.HTTPError: If API request fails
        """
        resp = await self._client.post(
            self.API_URL,
            json={
                "fen": fen,
                "depth": min(depth, 18),
                "maxThinkingTime": 100,
                "variants": 1,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        # chess-api.com returns eval in pawns, convert to centipawns
        eval_pawns = data.get("eval", 0)
        score_cp = int(eval_pawns * 100) if data.get("mate") is None else 0

        if data.get("mate") is not None:
            mate_val = data["mate"]
            score_cp = 10000 if mate_val > 0 else -10000

        return EngineEval(
            score_cp=score_cp,
            best_move_uci=data.get("move", ""),
            best_move_san=data.get("san", ""),
            mate_in=data.get("mate"),
            principal_variation=data.get("continuationArr", []),
            depth=data.get("depth", depth),
        )
