import io
import re
from statistics import mean, stdev

import chess.pgn
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from chesslens.dependencies import get_db
from chesslens.models.db import Player, Game
from chesslens.services.playstyle_classifier import PlaystyleClassifier

router = APIRouter()

CLOCK_RE = re.compile(r"\[%clk (\d+):(\d+):(\d+(?:\.\d+)?)\]")


def _extract_basic_features(games: list) -> dict[str, float]:
    """Extract normalized features from raw game data without Stockfish."""
    all_capture_rates = []
    all_check_rates = []
    all_game_lengths = []
    all_think_times = []
    decisive_count = 0
    endgame_count = 0

    for g in games:
        try:
            pgn_game = chess.pgn.read_game(io.StringIO(g.pgn))
            if not pgn_game:
                continue
        except Exception:
            continue

        is_player_white = g.player_color == "white"
        player_moves = 0
        captures = 0
        checks = 0
        clocks = []

        for ply, node in enumerate(pgn_game.mainline()):
            is_white_move = ply % 2 == 0
            if is_white_move != is_player_white:
                continue

            player_moves += 1
            san = node.san()
            if "x" in san:
                captures += 1
            if "+" in san or "#" in san:
                checks += 1

            comment = node.comment or ""
            m = CLOCK_RE.search(comment)
            if m:
                secs = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
                clocks.append(secs)

        if player_moves > 0:
            all_capture_rates.append(captures / player_moves)
            all_check_rates.append(checks / player_moves)

        all_game_lengths.append(g.total_moves)

        if clocks and len(clocks) > 1:
            diffs = [clocks[i - 1] - clocks[i] for i in range(1, len(clocks)) if clocks[i - 1] > clocks[i]]
            if diffs:
                all_think_times.extend(diffs)

        if g.player_result in ("win", "loss"):
            decisive_count += 1
        if g.total_moves >= 80:
            endgame_count += 1

    total = max(1, len(games))

    def _norm(val: float, low: float, high: float) -> float:
        return max(0.0, min(1.0, (val - low) / max(0.001, high - low)))

    avg_capture = mean(all_capture_rates) if all_capture_rates else 0.15
    avg_check = mean(all_check_rates) if all_check_rates else 0.02
    avg_length = mean(all_game_lengths) if all_game_lengths else 40
    avg_think = mean(all_think_times) if all_think_times else 15
    think_var = stdev(all_think_times) if len(all_think_times) > 1 else 10

    return {
        "capture_rate": _norm(avg_capture, 0.05, 0.35),
        "check_frequency": _norm(avg_check, 0.0, 0.08),
        "sacrifice_rate": _norm(avg_capture * 0.3, 0.0, 0.1),  # Approximate
        "avg_think_time": _norm(avg_think, 2, 30),
        "think_time_variance": _norm(think_var, 2, 20),
        "decisive_game_rate": _norm(decisive_count / total, 0.5, 1.0),
        "game_length": _norm(avg_length, 20, 120),
        "endgame_frequency": _norm(endgame_count / total, 0.0, 0.5),
        "avg_centipawn_loss": 0.5,  # Unknown without Stockfish
        "blunder_rate": 0.5,
        "center_control": 0.5,
        "piece_activity": 0.5,
        "time_pressure_blunder_rate": 0.5,
        "acpl_endgame": 0.5,
    }


@router.get("/player/{username}/playstyle")
async def get_playstyle_analysis(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    """Get playstyle analysis for a player."""
    result = await db.execute(select(Player).where(Player.username == username.lower()))
    player = result.scalar_one_or_none()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    games_result = await db.execute(select(Game).where(Game.player_id == player.id))
    games = games_result.scalars().all()

    if not games:
        raise HTTPException(status_code=404, detail="No games found. Sync games first.")

    features = _extract_basic_features(games)
    classifier = PlaystyleClassifier()
    result = classifier.classify(features)

    return {
        "primary_archetype": result.primary_archetype,
        "secondary_archetype": result.secondary_archetype,
        "archetype_scores": {k: round(v, 1) for k, v in result.archetype_scores.items()},
        "radar_chart": [{"label": a.label, "value": round(a.value, 1)} for a in result.radar_chart],
        "description": result.description,
    }
