import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CoachingSummary:
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    action_items: list[str]


class CoachingNarrator:
    """Generate natural language coaching insights using Claude."""

    def __init__(self, anthropic_client):
        self._client = anthropic_client

    async def generate_summary(
        self,
        username: str,
        rating: int | None,
        primary_archetype: str,
        secondary_archetype: str,
        overall_acpl: float,
        blunder_rate: float,
        rushing_multiplier: float,
        weakest_phase: str,
        best_opening: str,
        worst_opening: str,
        total_games_analyzed: int,
    ) -> CoachingSummary:
        """Generate a comprehensive coaching summary from analysis data."""
        prompt = f"""You are a chess coach analyzing a player's game data. Generate a personalized coaching report.

Player: {username}
Rating: ~{rating or 'Unknown'} (rapid)
Playstyle: {primary_archetype} / {secondary_archetype}
Games analyzed: {total_games_analyzed}

Key metrics:
- Average centipawn loss: {overall_acpl:.1f}
- Blunder rate: {blunder_rate:.1%}
- Time trouble multiplier: {rushing_multiplier:.1f}x (blunder rate increases this much under 60 seconds)
- Weakest game phase: {weakest_phase}
- Best opening: {best_opening}
- Worst opening: {worst_opening}

Generate a coaching report with:
1. A 2-3 sentence summary of their overall play
2. 2-3 specific strengths
3. 2-3 specific weaknesses with concrete improvement suggestions
4. 3-5 prioritized action items they can work on

Be encouraging but honest. Give practical, specific advice for a player at this level.
Respond in JSON format:
{{"summary": "...", "strengths": ["..."], "weaknesses": ["..."], "action_items": ["..."]}}"""

        try:
            message = await self._client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            import json

            text = message.content[0].text
            # Try to parse JSON from the response
            # Handle potential markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            data = json.loads(text.strip())
            return CoachingSummary(
                summary=data.get("summary", ""),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                action_items=data.get("action_items", []),
            )
        except Exception as e:
            logger.error(f"Failed to generate coaching summary: {e}")
            return CoachingSummary(
                summary=f"Analysis of {total_games_analyzed} games shows an average centipawn loss of {overall_acpl:.1f}.",
                strengths=["Data collected for analysis"],
                weaknesses=[f"Blunder rate of {blunder_rate:.1%} needs improvement"],
                action_items=[
                    "Review your blunders after each game",
                    "Practice tactical puzzles daily",
                ],
            )
