"""
Pydantic schemas for ChessLens API.

Defines request and response models for all API endpoints.
Uses Pydantic v2 with model_config for ORM compatibility.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class PlayerResponse(BaseModel):
    """Player profile with ratings and sync status."""

    model_config = ConfigDict(from_attributes=True)

    username: str
    avatar_url: Optional[str] = None
    ratings: Dict[str, Optional[int]]
    total_games: int
    last_synced_at: Optional[datetime] = None


class SyncStatusResponse(BaseModel):
    """Status of game synchronization process."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    games_fetched: int
    total_archives: int


class GameSummaryResponse(BaseModel):
    """Summary information for a single game."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    chess_com_game_url: str
    player_color: str
    opponent_username: str
    opponent_rating: Optional[int]
    player_result: str
    eco: Optional[str]
    opening_name: Optional[str]
    time_class: Optional[str]
    played_at: datetime
    total_moves: int
    is_analyzed: bool


class GameListResponse(BaseModel):
    """Paginated list of games."""

    model_config = ConfigDict(from_attributes=True)

    games: List[GameSummaryResponse]
    total: int
    page: int
    per_page: int


class MoveResponse(BaseModel):
    """Basic move information without evaluation."""

    model_config = ConfigDict(from_attributes=True)

    move_index: int
    is_white: bool
    san: str
    fen_after: str
    clock_seconds: Optional[float]


class GameDetailResponse(GameSummaryResponse):
    """Detailed game information with moves."""

    model_config = ConfigDict(from_attributes=True)

    pgn: str
    moves: List[MoveResponse]


class MoveEvaluationResponse(MoveResponse):
    """Move with full evaluation data."""

    model_config = ConfigDict(from_attributes=True)

    uci: str
    fen_before: str
    best_move_uci: Optional[str]
    best_move_san: Optional[str]
    score_before_cp: Optional[int]
    score_after_cp: Optional[int]
    centipawn_loss: int
    classification: str
    game_phase: Optional[str]
    engine_line: Optional[List[str]]


class AnalysisSummaryResponse(BaseModel):
    """Summary statistics for game analysis."""

    model_config = ConfigDict(from_attributes=True)

    player_acpl: float
    opponent_acpl: float
    blunder_count: int
    mistake_count: int
    inaccuracy_count: int
    opening_acpl: Optional[float]
    middlegame_acpl: Optional[float]
    endgame_acpl: Optional[float]


class AnalysisResultResponse(BaseModel):
    """Complete analysis result for a game."""

    model_config = ConfigDict(from_attributes=True)

    game_id: int
    acpl: float
    accuracy: Optional[float]
    evaluations: List[MoveEvaluationResponse]
    summary: AnalysisSummaryResponse


class AnalysisStatusResponse(BaseModel):
    """Status of ongoing game analysis."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    moves_analyzed: int
    total_moves: int


class OpeningStatsResponse(BaseModel):
    """Statistics for a specific opening."""

    model_config = ConfigDict(from_attributes=True)

    eco: str
    name: str
    games_played: int
    wins: int
    draws: int
    losses: int
    win_rate: float
    avg_deviation_move: Optional[float]


class OpeningReportResponse(BaseModel):
    """Comprehensive opening repertoire report."""

    model_config = ConfigDict(from_attributes=True)

    openings: List[OpeningStatsResponse]
    most_played: str
    best_performing: str
    worst_performing: str
    repertoire_breadth: int
    book_adherence_rate: float


class RushingAnalysisResponse(BaseModel):
    """Analysis of time pressure impact on move quality."""

    model_config = ConfigDict(from_attributes=True)

    blunder_rate_under_60s: float
    blunder_rate_over_60s: float
    time_trouble_multiplier: float
    verdict: str


class WeaknessReportResponse(BaseModel):
    """Detailed weakness and pattern analysis."""

    model_config = ConfigDict(from_attributes=True)

    overall_blunder_rate: float
    phase_breakdown: Dict[str, float]
    move_number_heatmap: Dict[int, int]
    rushing_analysis: RushingAnalysisResponse
    top_blunders: List[dict]
    recurring_patterns: List[str]


class RadarAxisResponse(BaseModel):
    """Single axis for radar chart."""

    model_config = ConfigDict(from_attributes=True)

    label: str
    value: float


class PlaystyleResponse(BaseModel):
    """Player playstyle profile with archetypes."""

    model_config = ConfigDict(from_attributes=True)

    primary_archetype: str
    secondary_archetype: str
    archetype_scores: Dict[str, float]
    radar_chart: List[RadarAxisResponse]
    description: str


class CoachingSummaryResponse(BaseModel):
    """AI-generated coaching summary."""

    model_config = ConfigDict(from_attributes=True)

    summary: str
    strengths: List[str]
    weaknesses: List[str]
    action_items: List[str]
    generated_at: Optional[str]


class ChatContext(BaseModel):
    """Context for a chat message."""

    model_config = ConfigDict(from_attributes=True)

    game_id: Optional[int] = None
    move_index: Optional[int] = None
    fen: Optional[str] = None


class ChatRequest(BaseModel):
    """Request to send a chat message."""

    model_config = ConfigDict(from_attributes=True)

    session_id: str
    username: str
    message: str
    context: Optional[ChatContext] = None
