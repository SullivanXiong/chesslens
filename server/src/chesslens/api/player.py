from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from chesslens.dependencies import get_db, get_http_client
from chesslens.models.db import Player
from chesslens.models.schemas import PlayerResponse, SyncStatusResponse
from chesslens.services.chess_com_client import ChessComClient
from chesslens.services.pgn_parser import PgnParser
from chesslens.services.game_sync_service import GameSyncService, determine_player_color, determine_player_result
from datetime import datetime, timezone

router = APIRouter()


@router.get("/player/{username}", response_model=PlayerResponse)
async def get_player(
    username: str,
    db: AsyncSession = Depends(get_db),
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    """Fetch or refresh player profile from Chess.com."""
    client = ChessComClient(http_client)

    # Check if player exists in DB
    result = await db.execute(select(Player).where(Player.username == username.lower()))
    player = result.scalar_one_or_none()

    # Fetch fresh data from Chess.com
    try:
        profile = await client.get_player(username)
        stats = await client.get_stats(username)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Player '{username}' not found on Chess.com")
        raise HTTPException(status_code=502, detail="Chess.com API error")

    if player is None:
        player = Player(
            username=profile.username.lower(),
            chess_com_url=profile.url,
            avatar_url=profile.avatar_url,
            country=profile.country,
            joined_at=profile.joined,
            rapid_rating=stats.rapid_rating,
            blitz_rating=stats.blitz_rating,
            bullet_rating=stats.bullet_rating,
            last_synced_at=datetime.now(timezone.utc),
        )
        db.add(player)
    else:
        player.avatar_url = profile.avatar_url
        player.rapid_rating = stats.rapid_rating
        player.blitz_rating = stats.blitz_rating
        player.bullet_rating = stats.bullet_rating
        player.last_synced_at = datetime.now(timezone.utc)

    await db.flush()

    return PlayerResponse(
        username=player.username,
        avatar_url=player.avatar_url,
        ratings={
            "rapid": player.rapid_rating,
            "blitz": player.blitz_rating,
            "bullet": player.bullet_rating,
        },
        total_games=player.total_games_fetched,
        last_synced_at=player.last_synced_at.isoformat() if player.last_synced_at else None,
    )


@router.post("/player/{username}/sync", response_model=SyncStatusResponse)
async def sync_games(
    username: str,
    db: AsyncSession = Depends(get_db),
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    """Fetch all games from Chess.com and store them."""
    from chesslens.models.db import Game

    client = ChessComClient(http_client)
    sync_service = GameSyncService(client)

    # Get or create player
    result = await db.execute(select(Player).where(Player.username == username.lower()))
    player = result.scalar_one_or_none()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found. Call GET /api/player/{username} first.")

    # Fetch and parse all games
    player_data, stats, games = await sync_service.sync_player(username)

    # Get existing game URLs to avoid duplicates
    existing_result = await db.execute(
        select(Game.chess_com_game_url).where(Game.player_id == player.id)
    )
    existing_urls = {row[0] for row in existing_result.all()}

    new_count = 0
    for raw_game, parsed_game in games:
        if raw_game.url in existing_urls:
            continue

        game = Game(
            player_id=player.id,
            chess_com_game_url=raw_game.url,
            pgn=raw_game.pgn,
            white_username=raw_game.white_username,
            black_username=raw_game.black_username,
            player_color=determine_player_color(raw_game, username),
            white_rating=raw_game.white_rating,
            black_rating=raw_game.black_rating,
            result=parsed_game.result,
            player_result=determine_player_result(raw_game, username),
            eco=parsed_game.eco,
            opening_name=parsed_game.opening_name,
            time_control=raw_game.time_control,
            time_class=raw_game.time_class,
            played_at=datetime.fromtimestamp(raw_game.end_time, tz=timezone.utc),
            total_moves=parsed_game.total_moves,
        )
        db.add(game)
        new_count += 1

    player.total_games_fetched = (player.total_games_fetched or 0) + new_count
    player.last_synced_at = datetime.now(timezone.utc)

    return SyncStatusResponse(
        status="complete",
        games_fetched=new_count,
        total_archives=len(games),
    )
