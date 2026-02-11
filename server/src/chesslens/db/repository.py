"""
Repository layer for database access.

Provides data access methods for players, games, and move evaluations.
Follows repository pattern to encapsulate database queries.
"""

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from chesslens.models.db import (
    AnalysisSummary,
    Game,
    MoveEvaluation,
    Player,
    PlayerAnalysis,
)


class PlayerRepository:
    """Repository for Player database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize player repository.

        Args:
            session: Active async SQLAlchemy session
        """
        self._session = session

    async def get_by_username(self, username: str) -> Player | None:
        """
        Retrieve player by username (case-insensitive).

        Args:
            username: Chess.com username

        Returns:
            Player instance or None if not found
        """
        result = await self._session.execute(
            select(Player).where(Player.username == username.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, player: Player) -> Player:
        """
        Create a new player record.

        Args:
            player: Player instance to persist

        Returns:
            Created player with assigned ID
        """
        self._session.add(player)
        await self._session.flush()
        return player


class GameRepository:
    """Repository for Game database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize game repository.

        Args:
            session: Active async SQLAlchemy session
        """
        self._session = session

    async def get_by_id(self, game_id: int) -> Game | None:
        """
        Retrieve game by ID.

        Args:
            game_id: Primary key of game

        Returns:
            Game instance or None if not found
        """
        result = await self._session.execute(select(Game).where(Game.id == game_id))
        return result.scalar_one_or_none()

    async def list_for_player(
        self,
        player_id: int,
        page: int = 1,
        per_page: int = 20,
        time_class: str | None = None,
        player_result: str | None = None,
    ) -> tuple[list[Game], int]:
        """
        List games for a player with pagination and filters.

        Args:
            player_id: Player's primary key
            page: Page number (1-indexed)
            per_page: Number of games per page
            time_class: Optional filter by time class (rapid, blitz, bullet)
            player_result: Optional filter by result (win, loss, draw)

        Returns:
            Tuple of (games list, total count)
        """
        query = select(Game).where(Game.player_id == player_id)
        count_query = select(func.count()).select_from(Game).where(Game.player_id == player_id)

        if time_class:
            query = query.where(Game.time_class == time_class)
            count_query = count_query.where(Game.time_class == time_class)
        if player_result:
            query = query.where(Game.player_result == player_result)
            count_query = count_query.where(Game.player_result == player_result)

        total = (await self._session.execute(count_query)).scalar() or 0
        query = query.order_by(desc(Game.played_at)).offset((page - 1) * per_page).limit(per_page)
        result = await self._session.execute(query)
        return list(result.scalars().all()), total

    async def get_existing_urls(self, player_id: int) -> set[str]:
        """
        Get all game URLs for a player (for deduplication).

        Args:
            player_id: Player's primary key

        Returns:
            Set of chess.com game URLs
        """
        result = await self._session.execute(
            select(Game.chess_com_game_url).where(Game.player_id == player_id)
        )
        return {row[0] for row in result.all()}

    async def get_unanalyzed(self, player_id: int, limit: int = 50) -> list[Game]:
        """
        Get unanalyzed games for a player.

        Args:
            player_id: Player's primary key
            limit: Maximum number of games to return

        Returns:
            List of games without analysis
        """
        result = await self._session.execute(
            select(Game)
            .where(Game.player_id == player_id, Game.is_analyzed == False)  # noqa: E712
            .order_by(desc(Game.played_at))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_analyzed(self, player_id: int) -> list[Game]:
        """
        Get all analyzed games for a player.

        Args:
            player_id: Player's primary key

        Returns:
            List of games with completed analysis
        """
        result = await self._session.execute(
            select(Game)
            .where(Game.player_id == player_id, Game.is_analyzed == True)  # noqa: E712
            .order_by(desc(Game.played_at))
        )
        return list(result.scalars().all())


class MoveEvaluationRepository:
    """Repository for MoveEvaluation database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize move evaluation repository.

        Args:
            session: Active async SQLAlchemy session
        """
        self._session = session

    async def get_for_game(self, game_id: int) -> list[MoveEvaluation]:
        """
        Get all move evaluations for a game, ordered by move index.

        Args:
            game_id: Game's primary key

        Returns:
            List of move evaluations in chronological order
        """
        result = await self._session.execute(
            select(MoveEvaluation)
            .where(MoveEvaluation.game_id == game_id)
            .order_by(MoveEvaluation.move_index)
        )
        return list(result.scalars().all())

    async def bulk_create(self, evaluations: list[MoveEvaluation]) -> None:
        """
        Create multiple move evaluations in a batch.

        Args:
            evaluations: List of MoveEvaluation instances to persist
        """
        self._session.add_all(evaluations)
        await self._session.flush()
