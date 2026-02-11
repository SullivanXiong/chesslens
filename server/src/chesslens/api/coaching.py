from fastapi import APIRouter

router = APIRouter()


@router.get("/player/{username}/coaching")
async def get_coaching_recommendations(username: str):
    """Get personalized coaching recommendations for a player."""
    return {"status": "not_implemented"}
