"""
Chess.com API client for fetching player data and games.

This module provides an async client for interacting with the Chess.com public API.
It handles fetching player profiles, statistics, and game archives.
"""

import httpx
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChessComPlayer:
    """Player profile data from Chess.com."""

    username: str
    url: str
    avatar_url: str | None
    country: str | None
    joined: datetime | None


@dataclass
class ChessComStats:
    """Player rating statistics across time controls."""

    rapid_rating: int | None
    blitz_rating: int | None
    bullet_rating: int | None


@dataclass
class ChessComGame:
    """Raw game data from Chess.com API."""

    url: str
    pgn: str
    time_control: str
    time_class: str
    rated: bool
    end_time: int
    white_username: str
    white_rating: int
    white_result: str
    black_username: str
    black_rating: int
    black_result: str


class ChessComClient:
    """
    Async client for Chess.com Public API.

    Provides methods to fetch player profiles, statistics, and game archives.
    Uses httpx for async HTTP requests.
    """

    BASE_URL = "https://api.chess.com/pub"

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        """
        Initialize Chess.com API client.

        Args:
            http_client: Optional httpx client. If None, creates a new client
                        with appropriate headers and timeout.
        """
        self._client = http_client or httpx.AsyncClient(
            headers={"User-Agent": "ChessLens/1.0 (github.com/SullivanXiong/chesslens)"},
            timeout=30.0,
        )
        self._owns_client = http_client is None

    async def get_player(self, username: str) -> ChessComPlayer:
        """
        Fetch player profile data.

        Args:
            username: Chess.com username

        Returns:
            ChessComPlayer with profile information

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        resp = await self._client.get(f"{self.BASE_URL}/player/{username}")
        resp.raise_for_status()
        data = resp.json()
        return ChessComPlayer(
            username=data["username"],
            url=data.get("url", ""),
            avatar_url=data.get("avatar"),
            country=data.get("country", "").split("/")[-1] if data.get("country") else None,
            joined=datetime.fromtimestamp(data["joined"]) if data.get("joined") else None,
        )

    async def get_stats(self, username: str) -> ChessComStats:
        """
        Fetch player rating statistics.

        Args:
            username: Chess.com username

        Returns:
            ChessComStats with ratings for different time controls

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        resp = await self._client.get(f"{self.BASE_URL}/player/{username}/stats")
        resp.raise_for_status()
        data = resp.json()

        def _get_rating(key: str) -> int | None:
            section = data.get(key)
            if section and "last" in section:
                return section["last"]["rating"]
            return None

        return ChessComStats(
            rapid_rating=_get_rating("chess_rapid"),
            blitz_rating=_get_rating("chess_blitz"),
            bullet_rating=_get_rating("chess_bullet"),
        )

    async def get_archive_urls(self, username: str) -> list[str]:
        """
        Fetch list of monthly game archive URLs for a player.

        Args:
            username: Chess.com username

        Returns:
            List of archive URLs (e.g., https://api.chess.com/pub/player/{username}/games/2024/01)

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        resp = await self._client.get(f"{self.BASE_URL}/player/{username}/games/archives")
        resp.raise_for_status()
        return resp.json().get("archives", [])

    async def get_monthly_games(self, archive_url: str) -> list[ChessComGame]:
        """
        Fetch games from a specific monthly archive URL.

        Args:
            archive_url: Full URL to a monthly archive

        Returns:
            List of ChessComGame objects from that month

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        resp = await self._client.get(archive_url)
        resp.raise_for_status()
        games = []
        for g in resp.json().get("games", []):
            if not g.get("pgn"):
                continue
            games.append(
                ChessComGame(
                    url=g.get("url", ""),
                    pgn=g["pgn"],
                    time_control=g.get("time_control", ""),
                    time_class=g.get("time_class", ""),
                    rated=g.get("rated", False),
                    end_time=g.get("end_time", 0),
                    white_username=g.get("white", {}).get("username", ""),
                    white_rating=g.get("white", {}).get("rating", 0),
                    white_result=g.get("white", {}).get("result", ""),
                    black_username=g.get("black", {}).get("username", ""),
                    black_rating=g.get("black", {}).get("rating", 0),
                    black_result=g.get("black", {}).get("result", ""),
                )
            )
        return games

    async def fetch_all_games(self, username: str) -> list[ChessComGame]:
        """
        Fetch all games for a player across all monthly archives.

        Args:
            username: Chess.com username

        Returns:
            List of all ChessComGame objects for the player

        Raises:
            httpx.HTTPStatusError: If any API request fails
        """
        archive_urls = await self.get_archive_urls(username)
        all_games: list[ChessComGame] = []
        for url in archive_urls:
            monthly_games = await self.get_monthly_games(url)
            all_games.extend(monthly_games)
        return all_games

    async def close(self):
        """Close the HTTP client if owned by this instance."""
        if self._owns_client:
            await self._client.aclose()
