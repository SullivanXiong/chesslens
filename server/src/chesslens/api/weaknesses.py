from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from chesslens.dependencies import get_db
from chesslens.models.db import Player, Game, MoveEvaluation
from chesslens.services.weakness_detector import WeaknessDetector

router = APIRouter()


@router.get("/player/{username}/weaknesses")
async def get_weaknesses_analysis(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    """Get weakness patterns analysis for a player."""
    result = await db.execute(select(Player).where(Player.username == username.lower()))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Check for analyzed games with move evaluations
    evals_result = await db.execute(
        select(MoveEvaluation)
        .join(Game, MoveEvaluation.game_id == Game.id)
        .where(Game.player_id == player.id)
    )
    evaluations = evals_result.scalars().all()

    if evaluations:
        # Build color map
        game_ids = {ev.game_id for ev in evaluations}
        games_result = await db.execute(select(Game).where(Game.id.in_(game_ids)))
        games = games_result.scalars().all()
        color_map = {g.id: g.player_color for g in games}

        ev_dicts = [
            {
                "game_id": ev.game_id,
                "move_index": ev.move_index,
                "is_white": ev.is_white,
                "san": ev.san,
                "centipawn_loss": ev.centipawn_loss,
                "classification": ev.classification.value if ev.classification else "good",
                "game_phase": ev.game_phase.value if ev.game_phase else "middlegame",
                "clock_seconds": ev.clock_seconds,
                "fen_before": ev.fen_before,
            }
            for ev in evaluations
        ]

        detector = WeaknessDetector()
        report = detector.analyze(ev_dicts, color_map)

        return {
            "overall_blunder_rate": round(report.overall_blunder_rate, 4),
            "phase_breakdown": {k: round(v, 4) for k, v in report.phase_breakdown.items()},
            "move_number_heatmap": report.move_number_heatmap,
            "rushing_analysis": {
                "blunder_rate_under_60s": round(report.rushing_analysis.blunder_rate_under_60s, 4),
                "blunder_rate_over_60s": round(report.rushing_analysis.blunder_rate_over_60s, 4),
                "time_trouble_multiplier": round(report.rushing_analysis.time_trouble_multiplier, 2),
                "verdict": report.rushing_analysis.verdict,
            },
            "top_blunders": report.top_blunders,
            "recurring_patterns": report.recurring_patterns,
        }

    # Fallback: basic stats from raw game data
    games_result = await db.execute(select(Game).where(Game.player_id == player.id))
    games = games_result.scalars().all()

    if not games:
        raise HTTPException(status_code=404, detail="No games found. Sync games first.")

    wins = sum(1 for g in games if g.player_result == "win")
    losses = sum(1 for g in games if g.player_result == "loss")
    draws = sum(1 for g in games if g.player_result not in ("win", "loss"))
    total = len(games)
    avg_moves = sum(g.total_moves for g in games) / max(1, total)
    short_games = sum(1 for g in games if g.total_moves <= 20)

    return {
        "overall_blunder_rate": 0,
        "phase_breakdown": {"opening": 0, "middlegame": 0, "endgame": 0},
        "move_number_heatmap": {},
        "rushing_analysis": {
            "blunder_rate_under_60s": 0,
            "blunder_rate_over_60s": 0,
            "time_trouble_multiplier": 0,
            "verdict": "Analyze games with Stockfish to get rushing analysis.",
        },
        "top_blunders": [],
        "recurring_patterns": [
            f"Win rate: {wins/max(1,total):.0%} ({wins}W / {draws}D / {losses}L across {total} games)",
            f"Average game length: {avg_moves:.0f} half-moves ({avg_moves/2:.0f} full moves)",
            f"Short games (under 20 moves): {short_games} ({short_games/max(1,total):.0%})",
            "Run Stockfish analysis on your games for detailed blunder detection.",
        ],
    }
