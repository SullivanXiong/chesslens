from fastapi import APIRouter

router = APIRouter()


@router.get("/player/{username}/playstyle")
async def get_playstyle_analysis(username: str):
    """Get playstyle analysis for a player."""
    return {"status": "not_implemented"}
