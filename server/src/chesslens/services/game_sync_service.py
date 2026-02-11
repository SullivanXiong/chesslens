"""
Game synchronization service for fetching and parsing Chess.com games.

Orchestrates the full pipeline of fetching games from Chess.com,
parsing PGN data, and preparing it for database storage.
"""

import logging

from chesslens.services.chess_com_client import ChessComClient, ChessComGame
from chesslens.services.pgn_parser import PgnParser, ParsedGame

logger = logging.getLogger(__name__)


def determine_player_result(game: ChessComGame, username: str) -> str:
    """
    Determine game result from the specified player's perspective.

    Args:
        game: Raw Chess.com game data
        username: Player to determine result for

    Returns:
        "win", "loss", or "draw"
    """
    username_lower = username.lower()
    if game.white_username.lower() == username_lower:
        result = game.white_result
    else:
        result = game.black_result

    if result in ("win",):
        return "win"
    elif result in ("checkmated", "timeout", "resigned", "abandoned"):
        return "loss"
    else:
        return "draw"


def determine_player_color(game: ChessComGame, username: str) -> str:
    """
    Determine which color the specified player had.

    Args:
        game: Raw Chess.com game data
        username: Player to check color for

    Returns:
        "white" or "black"
    """
    if game.white_username.lower() == username.lower():
        return "white"
    return "black"


def determine_opponent_username(game: ChessComGame, username: str) -> str:
    """
    Determine the opponent's username.

    Args:
        game: Raw Chess.com game data
        username: Player whose opponent to find

    Returns:
        Opponent's username
    """
    if game.white_username.lower() == username.lower():
        return game.black_username
    return game.white_username


class GameSyncService:
    """
    Service for synchronizing games from Chess.com.

    Coordinates fetching games from the Chess.com API, parsing their PGN data,
    and preparing the structured data for database storage.
    """

    def __init__(self, chess_com_client: ChessComClient, pgn_parser: PgnParser | None = None):
        """
        Initialize game sync service.

        Args:
            chess_com_client: Client for Chess.com API requests
            pgn_parser: Optional PGN parser (creates default if not provided)
        """
        self._client = chess_com_client
        self._parser = pgn_parser or PgnParser()

    async def fetch_and_parse_all_games(
        self, username: str
    ) -> list[tuple[ChessComGame, ParsedGame]]:
        """
        Fetch all games for a player and parse their PGN data.

        Args:
            username: Chess.com username to fetch games for

        Returns:
            List of tuples containing (raw_game, parsed_game) for each successfully
            parsed game. Games that fail to parse are skipped with a warning.
        """
        raw_games = await self._client.fetch_all_games(username)
        logger.info(f"Fetched {len(raw_games)} games for {username}")

        results: list[tuple[ChessComGame, ParsedGame]] = []
        for raw_game in raw_games:
            parsed = self._parser.parse(raw_game.pgn)
            if parsed is None:
                logger.warning(f"Failed to parse PGN for game: {raw_game.url}")
                continue
            results.append((raw_game, parsed))

        logger.info(f"Successfully parsed {len(results)} games for {username}")
        return results

    async def sync_player(self, username: str):
        """
        Perform full player synchronization.

        Fetches player profile, rating statistics, and all game data.

        Args:
            username: Chess.com username to sync

        Returns:
            Tuple of (player, stats, games) where:
                - player: ChessComPlayer profile data
                - stats: ChessComStats rating data
                - games: List of (ChessComGame, ParsedGame) tuples
        """
        player = await self._client.get_player(username)
        stats = await self._client.get_stats(username)
        games = await self.fetch_and_parse_all_games(username)
        return player, stats, games
