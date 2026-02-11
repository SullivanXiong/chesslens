import logging
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class ChatService:
    """RAG-based chess coaching chatbot using Claude."""

    def __init__(self, anthropic_client):
        self._client = anthropic_client

    async def stream_response(
        self,
        username: str,
        message: str,
        player_summary: dict | None = None,
        game_context: dict | None = None,
        chat_history: list[dict] | None = None,
    ) -> AsyncIterator[str]:
        """Stream a coaching response to a user message.

        Args:
            username: Player's Chess.com username
            message: User's chat message
            player_summary: Dict with keys: rating, archetype, acpl, coaching_summary
            game_context: Optional dict with keys: game_id, pgn, moves (list of eval dicts),
                         current_move_index, current_fen
            chat_history: List of {"role": "user"/"assistant", "content": "..."} messages
        """
        system_prompt = self._build_system_prompt(username, player_summary, game_context)

        messages = []
        if chat_history:
            messages.extend(chat_history[-20:])  # Last 20 messages
        messages.append({"role": "user", "content": message})

        try:
            async with self._client.messages.stream(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Chat streaming error: {e}")
            yield f"I'm having trouble processing your question. Error: {str(e)}"

    def _build_system_prompt(
        self,
        username: str,
        player_summary: dict | None,
        game_context: dict | None,
    ) -> str:
        parts = [
            f"You are ChessLens Coach, a personal chess improvement assistant for {username}.",
            "You have deep knowledge of chess strategy and access to the player's analyzed game history.",
            "",
        ]

        if player_summary:
            parts.extend(
                [
                    "## Player Profile",
                    f"- Rating: ~{player_summary.get('rating', 'Unknown')} (rapid)",
                    f"- Playstyle: {player_summary.get('archetype', 'Unknown')}",
                    f"- Average centipawn loss: {player_summary.get('acpl', 'N/A')}",
                    "",
                ]
            )
            coaching = player_summary.get("coaching_summary")
            if coaching:
                parts.extend(["## Coaching Summary", coaching, ""])

        if game_context:
            parts.extend(
                [
                    "## Current Game Context",
                    f"Game ID: {game_context.get('game_id', 'N/A')}",
                ]
            )
            if game_context.get("current_fen"):
                parts.append(f"Current position (FEN): {game_context['current_fen']}")
            if game_context.get("current_move_index") is not None:
                parts.append(f"Viewing move: {game_context['current_move_index']}")

            # Add relevant move evaluations around the current position
            moves = game_context.get("moves", [])
            current_idx = game_context.get("current_move_index", 0)
            nearby = [m for m in moves if abs(m.get("move_index", 0) - current_idx) <= 3]
            if nearby:
                parts.append("\nNearby moves:")
                for m in nearby:
                    marker = (
                        " <-- current" if m.get("move_index") == current_idx else ""
                    )
                    parts.append(
                        f"  Move {m.get('move_index', '?')}: {m.get('san', '?')} "
                        f"(eval: {m.get('score_after_cp', '?')}cp, "
                        f"loss: {m.get('centipawn_loss', '?')}cp, "
                        f"{m.get('classification', '?')}){marker}"
                    )
                    if m.get("best_move_san"):
                        parts.append(f"    Best was: {m['best_move_san']}")
            parts.append("")

        parts.extend(
            [
                "## Instructions",
                "- When the user describes their thinking for a move, explain what they missed and how to adjust their thought process.",
                "- Reference specific positions, evaluations, and best moves when available.",
                "- Use algebraic notation (Nf3, e4) and name tactical motifs (pin, fork, skewer).",
                "- Explain WHY a move is good or bad in plain terms, not just that it is.",
                "- Be encouraging but honest. Acknowledge good intuitions while pointing out blind spots.",
                "- Keep responses concise and actionable. Aim for 2-4 paragraphs.",
            ]
        )

        return "\n".join(parts)
