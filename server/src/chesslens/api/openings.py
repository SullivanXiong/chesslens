from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from chesslens.dependencies import get_db, get_http_client
from chesslens.models.db import Player, Game
from chesslens.services.opening_analyzer import OpeningAnalyzer

router = APIRouter()


@router.get("/player/{username}/openings")
async def get_openings_analysis(
    username: str,
    db: AsyncSession = Depends(get_db),
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    """Get opening repertoire analysis for a player."""
    result = await db.execute(select(Player).where(Player.username == username.lower()))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    games_result = await db.execute(select(Game).where(Game.player_id == player.id))
    games = games_result.scalars().all()

    if not games:
        raise HTTPException(status_code=404, detail="No games found. Sync games first.")

    game_dicts = [
        {
            "eco": g.eco or "",
            "opening_name": g.opening_name or "Unknown",
            "player_color": g.player_color,
            "player_result": g.player_result,
            "pgn": g.pgn,
        }
        for g in games
    ]

    analyzer = OpeningAnalyzer(http_client)
    report = await analyzer.analyze_repertoire(game_dicts, username)

    return {
        "openings": [
            {
                "eco": o.eco,
                "name": o.name,
                "games_played": o.games_played,
                "wins": o.wins,
                "draws": o.draws,
                "losses": o.losses,
                "win_rate": round(o.win_rate, 3),
                "avg_deviation_move": o.avg_deviation_move,
            }
            for o in report.openings
        ],
        "most_played": report.most_played,
        "best_performing": report.best_performing,
        "worst_performing": report.worst_performing,
        "repertoire_breadth": report.repertoire_breadth,
        "book_adherence_rate": round(report.book_adherence_rate, 3),
    }
