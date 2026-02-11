from fastapi import APIRouter

router = APIRouter()


@router.post("/analysis/game/{game_id}")
async def analyze_game(game_id: int):
    """Start analysis for a game."""
    return {"status": "not_implemented"}


@router.get("/analysis/game/{game_id}/status")
async def get_analysis_status(game_id: int):
    """Get analysis status for a game."""
    return {"status": "not_implemented"}


@router.get("/analysis/game/{game_id}/result")
async def get_analysis_result(game_id: int):
    """Get analysis result for a game."""
    return {"status": "not_implemented"}
