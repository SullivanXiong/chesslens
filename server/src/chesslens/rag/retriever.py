import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    chunk_text: str
    score: float
    metadata: dict


class ChunkRetriever:
    """Retrieve relevant game chunks for RAG context.

    MVP: Simple keyword matching on chunk text.
    Phase 2: pgvector similarity search with embeddings.
    """

    def __init__(self, chunks: list[dict] | None = None):
        self._chunks = chunks or []

    def set_chunks(self, chunks: list[dict]):
        self._chunks = chunks

    def search(self, query: str, top_k: int = 8) -> list[RetrievalResult]:
        """Simple keyword-based search over chunks."""
        query_terms = set(query.lower().split())
        scored = []

        for chunk in self._chunks:
            text = chunk.get("text", "").lower()
            # Simple term frequency scoring
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                scored.append(
                    RetrievalResult(
                        chunk_text=chunk.get("text", ""),
                        score=score,
                        metadata=chunk.get("metadata", {}),
                    )
                )

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

    def get_game_chunks(self, game_id: int) -> list[RetrievalResult]:
        """Get all chunks for a specific game."""
        return [
            RetrievalResult(
                chunk_text=c.get("text", ""),
                score=1.0,
                metadata=c.get("metadata", {}),
            )
            for c in self._chunks
            if c.get("metadata", {}).get("game_id") == game_id
        ]
