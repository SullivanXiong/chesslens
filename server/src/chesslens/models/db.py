"""
SQLAlchemy ORM models for ChessLens.

Defines database tables for players, games, move evaluations,
analysis summaries, player analysis, chat messages, and embeddings.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from chesslens.models.enums import GamePhase, MoveClassification


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Player(Base):
    """Chess.com player profile and ratings."""

    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    chess_com_url: Mapped[Optional[str]] = mapped_column(String(200))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    country: Mapped[Optional[str]] = mapped_column(String(10))
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rapid_rating: Mapped[Optional[int]] = mapped_column(Integer)
    blitz_rating: Mapped[Optional[int]] = mapped_column(Integer)
    bullet_rating: Mapped[Optional[int]] = mapped_column(Integer)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    total_games_fetched: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    games: Mapped[List["Game"]] = relationship("Game", back_populates="player")
    player_analysis: Mapped[Optional["PlayerAnalysis"]] = relationship(
        "PlayerAnalysis", back_populates="player", uselist=False
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="player")


class Game(Base):
    """Individual chess game with metadata."""

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), index=True, nullable=False)
    chess_com_game_url: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    pgn: Mapped[str] = mapped_column(Text, nullable=False)
    white_username: Mapped[str] = mapped_column(String(50), nullable=False)
    black_username: Mapped[str] = mapped_column(String(50), nullable=False)
    player_color: Mapped[str] = mapped_column(String(10), nullable=False)
    white_rating: Mapped[Optional[int]] = mapped_column(Integer)
    black_rating: Mapped[Optional[int]] = mapped_column(Integer)
    result: Mapped[str] = mapped_column(String(10), nullable=False)
    player_result: Mapped[str] = mapped_column(String(10), nullable=False)
    eco: Mapped[Optional[str]] = mapped_column(String(10))
    opening_name: Mapped[Optional[str]] = mapped_column(String(200))
    time_control: Mapped[Optional[str]] = mapped_column(String(20))
    time_class: Mapped[Optional[str]] = mapped_column(String(20))
    played_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    total_moves: Mapped[int] = mapped_column(Integer, nullable=False)
    is_analyzed: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="games")
    move_evaluations: Mapped[List["MoveEvaluation"]] = relationship(
        "MoveEvaluation", back_populates="game", cascade="all, delete-orphan"
    )
    analysis_summary: Mapped[Optional["AnalysisSummary"]] = relationship(
        "AnalysisSummary", back_populates="game", uselist=False, cascade="all, delete-orphan"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="context_game")
    game_chunk_embeddings: Mapped[List["GameChunkEmbedding"]] = relationship(
        "GameChunkEmbedding", back_populates="game", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (Index("idx_player_played_at", "player_id", "played_at"),)


class MoveEvaluation(Base):
    """Evaluation of a single move in a game."""

    __tablename__ = "move_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), index=True, nullable=False)
    move_index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_white: Mapped[bool] = mapped_column(Boolean, nullable=False)
    san: Mapped[str] = mapped_column(String(10), nullable=False)
    uci: Mapped[str] = mapped_column(String(10), nullable=False)
    fen_before: Mapped[str] = mapped_column(String(100), nullable=False)
    fen_after: Mapped[str] = mapped_column(String(100), nullable=False)
    best_move_uci: Mapped[Optional[str]] = mapped_column(String(10))
    best_move_san: Mapped[Optional[str]] = mapped_column(String(10))
    score_before_cp: Mapped[Optional[int]] = mapped_column(Integer)
    score_after_cp: Mapped[Optional[int]] = mapped_column(Integer)
    centipawn_loss: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    classification: Mapped[MoveClassification] = mapped_column(nullable=False)
    clock_seconds: Mapped[Optional[float]] = mapped_column(Float)
    game_phase: Mapped[Optional[GamePhase]] = mapped_column()
    engine_line: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="move_evaluations")

    # Indexes
    __table_args__ = (Index("idx_game_move", "game_id", "move_index"),)


class AnalysisSummary(Base):
    """Summary statistics for a game analysis."""

    __tablename__ = "analysis_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), unique=True, nullable=False)
    player_acpl: Mapped[float] = mapped_column(Float, nullable=False)
    opponent_acpl: Mapped[float] = mapped_column(Float, nullable=False)
    player_accuracy: Mapped[Optional[float]] = mapped_column(Float)
    blunder_count: Mapped[int] = mapped_column(Integer, nullable=False)
    mistake_count: Mapped[int] = mapped_column(Integer, nullable=False)
    inaccuracy_count: Mapped[int] = mapped_column(Integer, nullable=False)
    opening_acpl: Mapped[Optional[float]] = mapped_column(Float)
    middlegame_acpl: Mapped[Optional[float]] = mapped_column(Float)
    endgame_acpl: Mapped[Optional[float]] = mapped_column(Float)
    book_deviation_move: Mapped[Optional[int]] = mapped_column(Integer)
    book_deviation_san: Mapped[Optional[str]] = mapped_column(String(10))
    features: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="analysis_summary")


class PlayerAnalysis(Base):
    """Aggregate analysis and playstyle profile for a player."""

    __tablename__ = "player_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), unique=True, nullable=False)
    analyzed_game_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    primary_archetype: Mapped[Optional[str]] = mapped_column(String(50))
    secondary_archetype: Mapped[Optional[str]] = mapped_column(String(50))
    archetype_scores: Mapped[Optional[dict]] = mapped_column(JSONB)
    radar_chart_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    aggregated_features: Mapped[Optional[dict]] = mapped_column(JSONB)
    opening_report: Mapped[Optional[dict]] = mapped_column(JSONB)
    weakness_report: Mapped[Optional[dict]] = mapped_column(JSONB)
    rushing_score: Mapped[Optional[float]] = mapped_column(Float)
    weakest_phase: Mapped[Optional[str]] = mapped_column(String(20))
    coaching_summary: Mapped[Optional[str]] = mapped_column(Text)
    coaching_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="player_analysis")


class ChatMessage(Base):
    """Chat message in a coaching session."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(10), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_game_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("games.id"))
    context_move_index: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="chat_messages")
    context_game: Mapped[Optional["Game"]] = relationship("Game", back_populates="chat_messages")

    # Indexes
    __table_args__ = (Index("idx_session_created", "session_id", "created_at"),)


class GameChunkEmbedding(Base):
    """Vector embeddings for game chunks for RAG."""

    __tablename__ = "game_chunk_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("games.id"), nullable=False)
    chunk_type: Mapped[str] = mapped_column(String(50), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB)
    # Requires pgvector: embedding = mapped_column(Vector(1536))

    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="game_chunk_embeddings")
