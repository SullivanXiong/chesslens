from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from chesslens.db.engine import async_session_factory
from chesslens.services.chess_com_client import ChessComClient
from chesslens.services.pgn_parser import PgnParser


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(
        headers={"User-Agent": "ChessLens/1.0 (github.com/SullivanXiong/chesslens)"},
        timeout=30.0,
    ) as client:
        yield client


def get_pgn_parser() -> PgnParser:
    return PgnParser()
