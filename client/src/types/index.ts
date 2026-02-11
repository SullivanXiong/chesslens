export interface Player {
  username: string;
  avatar_url: string | null;
  ratings: {
    rapid: number | null;
    blitz: number | null;
    bullet: number | null;
  };
  total_games: number;
  last_synced_at: string | null;
}

export interface GameSummary {
  id: number;
  chess_com_game_url: string;
  player_color: string;
  opponent_username: string;
  opponent_rating: number | null;
  player_result: string;
  eco: string | null;
  opening_name: string | null;
  time_class: string | null;
  played_at: string;
  total_moves: number;
  is_analyzed: boolean;
}

export interface GameList {
  games: GameSummary[];
  total: number;
  page: number;
  per_page: number;
}

export interface Move {
  move_index: number;
  is_white: boolean;
  san: string;
  fen_after: string;
  clock_seconds: number | null;
}

export interface MoveEvaluation extends Move {
  uci: string;
  fen_before: string;
  best_move_uci: string | null;
  best_move_san: string | null;
  score_before_cp: number | null;
  score_after_cp: number | null;
  centipawn_loss: number;
  classification: 'brilliant' | 'good' | 'book' | 'inaccuracy' | 'mistake' | 'blunder';
  game_phase: 'opening' | 'middlegame' | 'endgame' | null;
  engine_line: string[] | null;
}

export interface GameDetail extends GameSummary {
  pgn: string;
  moves: Move[];
}

export interface AnalysisSummary {
  player_acpl: number;
  opponent_acpl: number;
  blunder_count: number;
  mistake_count: number;
  inaccuracy_count: number;
  opening_acpl: number | null;
  middlegame_acpl: number | null;
  endgame_acpl: number | null;
}

export interface AnalysisStatus {
  status: string;
  moves_analyzed: number;
  total_moves: number;
}

export interface OpeningStats {
  eco: string;
  name: string;
  games_played: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: number;
  avg_deviation_move: number | null;
}

export interface OpeningReport {
  openings: OpeningStats[];
  most_played: string;
  best_performing: string;
  worst_performing: string;
  repertoire_breadth: number;
  book_adherence_rate: number;
}

export interface RushingAnalysis {
  blunder_rate_under_60s: number;
  blunder_rate_over_60s: number;
  time_trouble_multiplier: number;
  verdict: string;
}

export interface WeaknessReport {
  overall_blunder_rate: number;
  phase_breakdown: Record<string, number>;
  move_number_heatmap: Record<number, number>;
  rushing_analysis: RushingAnalysis;
  top_blunders: Record<string, unknown>[];
  recurring_patterns: string[];
}

export interface RadarAxis {
  label: string;
  value: number;
}

export interface PlaystyleReport {
  primary_archetype: string;
  secondary_archetype: string;
  archetype_scores: Record<string, number>;
  radar_chart: RadarAxis[];
  description: string;
}

export interface CoachingSummary {
  summary: string;
  strengths: string[];
  weaknesses: string[];
  action_items: string[];
  generated_at: string | null;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface SyncStatus {
  status: string;
  games_fetched: number;
  total_archives: number;
}
