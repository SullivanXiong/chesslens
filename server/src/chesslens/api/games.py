from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from chesslens.dependencies import get_db
from chesslens.models.db import Player, Game
from chesslens.models.schemas import GameListResponse, GameSummaryResponse, GameDetailResponse, MoveResponse
from chesslens.services.pgn_parser import PgnParser

router = APIRouter()


@router.get("/player/{username}/games", response_model=GameListResponse)
async def list_games(
    username: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    time_class: str | None = Query(None),
    result: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List games for a player with optional filters."""
    player_result = await db.execute(select(Player).where(Player.username == username.lower()))
    player = player_result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    query = select(Game).where(Game.player_id == player.id)
    count_query = select(func.count()).select_from(Game).where(Game.player_id == player.id)

    if time_class:
        query = query.where(Game.time_class == time_class)
        count_query = count_query.where(Game.time_class == time_class)
    if result:
        query = query.where(Game.player_result == result)
        count_query = count_query.where(Game.player_result == result)

    total = (await db.execute(count_query)).scalar() or 0
    query = query.order_by(desc(Game.played_at)).offset((page - 1) * per_page).limit(per_page)
    games_result = await db.execute(query)
    games = games_result.scalars().all()

    def _opponent(g: Game) -> tuple[str, int]:
        if g.player_color == "white":
            return g.black_username, g.black_rating or 0
        return g.white_username, g.white_rating or 0

    return GameListResponse(
        games=[
            GameSummaryResponse(
                id=g.id,
                chess_com_game_url=g.chess_com_game_url,
                player_color=g.player_color,
                opponent_username=_opponent(g)[0],
                opponent_rating=_opponent(g)[1],
                player_result=g.player_result,
                eco=g.eco,
                opening_name=g.opening_name,
                time_class=g.time_class,
                played_at=g.played_at.isoformat() if g.played_at else None,
                total_moves=g.total_moves,
                is_analyzed=g.is_analyzed,
            )
            for g in games
        ],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/player/{username}/games/{game_id}", response_model=GameDetailResponse)
async def get_game(
    username: str,
    game_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a single game with parsed moves."""
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    parser = PgnParser()
    parsed = parser.parse(game.pgn)
    moves = []
    if parsed:
        moves = [
            MoveResponse(
                move_index=m.ply,
                is_white=m.is_white,
                san=m.san,
                fen_after=m.fen_after,
                clock_seconds=m.clock_seconds,
            )
            for m in parsed.moves
        ]

    opponent_username = game.black_username if game.player_color == "white" else game.white_username
    opponent_rating = game.black_rating if game.player_color == "white" else game.white_rating

    return GameDetailResponse(
        id=game.id,
        chess_com_game_url=game.chess_com_game_url,
        player_color=game.player_color,
        opponent_username=opponent_username,
        opponent_rating=opponent_rating or 0,
        player_result=game.player_result,
        eco=game.eco,
        opening_name=game.opening_name,
        time_class=game.time_class,
        played_at=game.played_at.isoformat() if game.played_at else None,
        total_moves=game.total_moves,
        is_analyzed=game.is_analyzed,
        pgn=game.pgn,
        moves=moves,
    )
