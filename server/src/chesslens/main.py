from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chesslens.api.player import router as player_router
from chesslens.api.games import router as games_router
from chesslens.api.analysis import router as analysis_router
from chesslens.api.openings import router as openings_router
from chesslens.api.weaknesses import router as weaknesses_router
from chesslens.api.playstyle import router as playstyle_router
from chesslens.api.coaching import router as coaching_router
from chesslens.api.chat import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="ChessLens",
    description="Chess analysis engine powered by Stockfish and AI",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(player_router, prefix="/api", tags=["player"])
app.include_router(games_router, prefix="/api", tags=["games"])
app.include_router(analysis_router, prefix="/api", tags=["analysis"])
app.include_router(openings_router, prefix="/api", tags=["openings"])
app.include_router(weaknesses_router, prefix="/api", tags=["weaknesses"])
app.include_router(playstyle_router, prefix="/api", tags=["playstyle"])
app.include_router(coaching_router, prefix="/api", tags=["coaching"])
app.include_router(chat_router, prefix="/api", tags=["chat"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
