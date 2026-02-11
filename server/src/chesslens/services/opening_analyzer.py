"""
Opening analyzer for ChessLens.

Analyzes player opening repertoire using the Lichess Explorer database
to identify book deviations and opening performance statistics.
"""

import logging
from dataclasses import dataclass, field
import chess
import httpx

logger = logging.getLogger(__name__)


@dataclass
class BookMove:
    """A move from the opening book with statistics."""

    san: str
    uci: str
    games: int
    win_rate: float


@dataclass
class BookDeviation:
    """A deviation from book moves in the opening."""

    move_number: int
    player_played: str
    player_played_uci: str
    book_moves: list[BookMove]
    fen: str


@dataclass
class OpeningStats:
    """Statistics for a specific opening."""

    eco: str
    name: str
    games_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    deviations: list[BookDeviation] = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        """Calculate win rate for this opening."""
        return self.wins / max(1, self.games_played)

    @property
    def avg_deviation_move(self) -> float | None:
        """Calculate average move number where deviations occur."""
        if not self.deviations:
            return None
        return sum(d.move_number for d in self.deviations) / len(self.deviations)


@dataclass
class OpeningReport:
    """Comprehensive opening repertoire analysis."""

    openings: list[OpeningStats]
    most_played: str
    best_performing: str
    worst_performing: str
    repertoire_breadth: int
    book_adherence_rate: float


class OpeningAnalyzer:
    """Analyze opening repertoire and book adherence."""

    LICHESS_EXPLORER_URL = "https://explorer.lichess.ovh"

    def __init__(self, http_client: httpx.AsyncClient):
        """
        Initialize opening analyzer.

        Args:
            http_client: Async HTTP client for Lichess Explorer API calls
        """
        self._client = http_client

    async def analyze_repertoire(
        self, games: list[dict], username: str
    ) -> OpeningReport:
        """
        Analyze opening repertoire from a list of game dicts.

        Each game dict should have: eco, opening_name, player_color, player_result, pgn

        Args:
            games: List of game dictionaries with opening and result data
            username: Player's username (for future use)

        Returns:
            OpeningReport with repertoire statistics
        """
        opening_stats: dict[str, OpeningStats] = {}
        total_deviations = 0
        total_games = 0

        for game in games:
            eco = game.get("eco", "")
            name = game.get("opening_name", "Unknown")
            key = f"{eco}:{name}" if eco else name

            if key not in opening_stats:
                opening_stats[key] = OpeningStats(eco=eco, name=name)

            stats = opening_stats[key]
            stats.games_played += 1
            total_games += 1

            result = game.get("player_result", "")
            if result == "win":
                stats.wins += 1
            elif result == "loss":
                stats.losses += 1
            else:
                stats.draws += 1

        openings_list = sorted(
            opening_stats.values(), key=lambda o: o.games_played, reverse=True
        )

        most_played = openings_list[0].name if openings_list else "None"
        best_performing = (
            max(openings_list, key=lambda o: o.win_rate).name if openings_list else "None"
        )
        worst_performing = min(
            [o for o in openings_list if o.games_played >= 3],
            key=lambda o: o.win_rate,
            default=openings_list[-1] if openings_list else None,
        )
        worst_name = worst_performing.name if worst_performing else "None"

        return OpeningReport(
            openings=openings_list,
            most_played=most_played,
            best_performing=best_performing,
            worst_performing=worst_name,
            repertoire_breadth=len(opening_stats),
            book_adherence_rate=1.0 - (total_deviations / max(1, total_games)),
        )

    async def find_book_deviation(
        self, pgn_text: str, player_color: str
    ) -> BookDeviation | None:
        """
        Find where a player first deviates from book in a single game.

        Args:
            pgn_text: Complete PGN string for the game
            player_color: "white" or "black"

        Returns:
            BookDeviation object if deviation found, None otherwise
        """
        import chess.pgn
        import io

        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            return None

        board = game.board()
        is_player_white = player_color == "white"

        for ply, node in enumerate(game.mainline()):
            move = node.move
            is_white_move = ply % 2 == 0
            is_player_move = is_white_move == is_player_white

            if ply >= 40:  # Only check first 20 full moves
                break

            if is_player_move:
                book_data = await self._query_explorer(board.fen())
                book_moves_data = book_data.get("moves", [])

                if book_moves_data:
                    book_ucis = {m["uci"] for m in book_moves_data}
                    if move.uci() not in book_ucis:
                        return BookDeviation(
                            move_number=(ply // 2) + 1,
                            player_played=board.san(move),
                            player_played_uci=move.uci(),
                            book_moves=[
                                BookMove(
                                    san=m.get("san", ""),
                                    uci=m["uci"],
                                    games=m.get("white", 0)
                                    + m.get("draws", 0)
                                    + m.get("black", 0),
                                    win_rate=m.get("white", 0)
                                    / max(
                                        1,
                                        m.get("white", 0)
                                        + m.get("draws", 0)
                                        + m.get("black", 0),
                                    ),
                                )
                                for m in book_moves_data[:5]
                            ],
                            fen=board.fen(),
                        )

            board.push(move)

        return None

    async def _query_explorer(self, fen: str) -> dict:
        """
        Query Lichess Explorer API for opening book data.

        Args:
            fen: FEN position string

        Returns:
            JSON response from Explorer API with moves data
        """
        try:
            resp = await self._client.get(
                f"{self.LICHESS_EXPLORER_URL}/lichess",
                params={
                    "variant": "standard",
                    "fen": fen,
                    "ratings": "800,1000,1200,1400",
                    "speeds": "rapid,classical",
                },
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.warning(f"Lichess explorer query failed for FEN: {fen[:30]}...")
            return {"moves": []}
