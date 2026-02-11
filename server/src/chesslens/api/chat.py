from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat():
    """Interactive chat endpoint for chess coaching."""
    return {"status": "not_implemented"}
