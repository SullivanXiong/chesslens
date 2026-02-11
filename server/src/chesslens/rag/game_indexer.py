from dataclasses import dataclass


@dataclass
class GameChunk:
    game_id: int
    chunk_type: str
    text: str
    metadata: dict


class GameIndexer:
    """Create searchable text chunks from analyzed games."""

    def index_game(
        self,
        game_id: int,
        opening_name: str,
        eco: str,
        player_result: str,
        player_color: str,
        opponent_name: str,
        opponent_rating: int,
        date: str,
        total_moves: int,
        acpl: float,
        blunder_count: int,
        mistake_count: int,
        move_evaluations: list[dict],
    ) -> list[GameChunk]:
        """Create chunks from a single analyzed game."""
        chunks = []

        # Game overview chunk
        chunks.append(
            GameChunk(
                game_id=game_id,
                chunk_type="game_overview",
                text=(
                    f"Game played on {date} as {player_color} against "
                    f"{opponent_name} ({opponent_rating}). "
                    f"Opening: {opening_name} ({eco}). "
                    f"Result: {player_result}. "
                    f"Average centipawn loss: {acpl:.0f}. "
                    f"Blunders: {blunder_count}, Mistakes: {mistake_count}. "
                    f"Game lasted {total_moves} half-moves."
                ),
                metadata={"game_id": game_id, "opening": eco, "result": player_result},
            )
        )

        # Individual blunder/mistake chunks
        for ev in move_evaluations:
            if ev.get("classification") not in ("blunder", "mistake"):
                continue

            chunks.append(
                GameChunk(
                    game_id=game_id,
                    chunk_type="blunder_analysis",
                    text=(
                        f"Move {ev.get('move_index', '?')} ({ev.get('san', '?')}) was a "
                        f"{ev.get('classification', '?')} "
                        f"(lost {ev.get('centipawn_loss', 0)} centipawns). "
                        f"The best move was {ev.get('best_move_san', 'unknown')}. "
                        f"Phase: {ev.get('game_phase', 'unknown')}. "
                        f"Position FEN: {ev.get('fen_before', '')}"
                    ),
                    metadata={
                        "game_id": game_id,
                        "move_index": ev.get("move_index"),
                        "classification": ev.get("classification"),
                        "phase": ev.get("game_phase"),
                    },
                )
            )

        return chunks
