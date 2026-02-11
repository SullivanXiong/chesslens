"""
PGN parser for converting Chess.com PGN strings into structured data.

Uses python-chess to parse PGN notation and extract move-by-move game data
including positions, clocks, and metadata.
"""

import chess.pgn
import io
import re
from dataclasses import dataclass, field


@dataclass
class ParsedMove:
    """Structured data for a single move in a chess game."""

    move_number: int  # Full move number (1-based)
    ply: int  # Half-move index (0-based)
    is_white: bool
    san: str  # Standard Algebraic Notation (e.g., "Nf3")
    uci: str  # Universal Chess Interface format (e.g., "g1f3")
    fen_before: str  # Board position before the move
    fen_after: str  # Board position after the move
    clock_seconds: float | None = None  # Remaining time in seconds


@dataclass
class ParsedGame:
    """Complete parsed game data including metadata and all moves."""

    chess_com_url: str
    white_username: str
    black_username: str
    white_rating: int
    black_rating: int
    result: str  # "1-0", "0-1", "1/2-1/2", or "*"
    eco: str  # ECO opening code (e.g., "C00")
    opening_name: str
    time_control: str
    date: str
    total_moves: int  # Number of half-moves (plies)
    moves: list[ParsedMove] = field(default_factory=list)


class PgnParser:
    """Parser for Chess.com PGN data."""

    CLOCK_REGEX = re.compile(r"\[%clk\s+(\d+):(\d+):(\d+(?:\.\d+)?)\]")

    def parse(self, pgn_text: str) -> ParsedGame | None:
        """
        Parse a PGN string into structured game data.

        Args:
            pgn_text: Complete PGN string including headers and moves

        Returns:
            ParsedGame object with all game data, or None if parsing fails
        """
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            return None

        headers = game.headers
        moves: list[ParsedMove] = []
        board = game.board()

        for ply, node in enumerate(game.mainline()):
            move = node.move
            san = board.san(move)
            fen_before = board.fen()
            board.push(move)
            fen_after = board.fen()

            clock_seconds = self._parse_clock(node.comment) if node.comment else None

            moves.append(
                ParsedMove(
                    move_number=(ply // 2) + 1,
                    ply=ply,
                    is_white=(ply % 2 == 0),
                    san=san,
                    uci=move.uci(),
                    fen_before=fen_before,
                    fen_after=fen_after,
                    clock_seconds=clock_seconds,
                )
            )

        return ParsedGame(
            chess_com_url=headers.get("Link", ""),
            white_username=headers.get("White", ""),
            black_username=headers.get("Black", ""),
            white_rating=int(headers.get("WhiteElo", "0") or "0"),
            black_rating=int(headers.get("BlackElo", "0") or "0"),
            result=headers.get("Result", "*"),
            eco=headers.get("ECO", ""),
            opening_name=headers.get(
                "Opening",
                headers.get("ECOUrl", "").split("/")[-1].replace("-", " ")
                if headers.get("ECOUrl")
                else "",
            ),
            time_control=headers.get("TimeControl", ""),
            date=headers.get("UTCDate", headers.get("Date", "")),
            total_moves=len(moves),
            moves=moves,
        )

    def _parse_clock(self, comment: str) -> float | None:
        """
        Parse Chess.com clock annotation into seconds.

        Chess.com embeds remaining time in PGN comments as [%clk H:MM:SS.S]

        Args:
            comment: Move comment string from PGN

        Returns:
            Remaining time in seconds, or None if no clock found
        """
        match = self.CLOCK_REGEX.search(comment)
        if not match:
            return None
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        return hours * 3600 + minutes * 60 + seconds
