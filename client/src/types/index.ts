export interface Player {
  id: number;
  username: string;
  avatar_url: string | null;
  rapid_rating: number | null;
  blitz_rating: number | null;
  bullet_rating: number | null;
  last_synced_at: string | null;
}

export interface GameSummary {
  id: number;
  chess_com_game_url: string;
  white_username: string;
  black_username: string;
  white_rating: number;
  black_rating: number;
  player_color: string;
  result: string;
  player_result: string;
  eco: string;
  opening_name: string;
  time_control: string;
  time_class: string;
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

export interface MoveEvaluation {
  id: number;
  move_index: number;
  is_white: boolean;
  san: string;
  uci: string;
  fen_before: string;
  fen_after: string;
  best_move_uci: string;
  best_move_san: string;
  score_before_cp: number;
  score_after_cp: number;
  centipawn_loss: number;
  classification: 'brilliant' | 'good' | 'book' | 'inaccuracy' | 'mistake' | 'blunder';
  clock_seconds: number | null;
  game_phase: 'opening' | 'middlegame' | 'endgame';
  engine_line: string[];
}

export interface GameDetail extends GameSummary {
  pgn: string;
  moves: MoveEvaluation[];
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
  game_id: number;
  status: 'pending' | 'analyzing' | 'complete' | 'failed';
  progress: number;
}

export interface OpeningStats {
  eco: string;
  name: string;
  games_played: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: number;
  avg_deviation_move: number;
}

export interface OpeningReport {
  openings: OpeningStats[];
  repertoire_breadth: number;
  most_played: string;
  best_performing: string;
}

export interface RushingAnalysis {
  normal_blunder_rate: number;
  time_pressure_blunder_rate: number;
  rushing_multiplier: number;
  time_pressure_threshold: number;
}

export interface WeaknessReport {
  phase_breakdown: { opening: number; middlegame: number; endgame: number };
  blunder_heatmap: { move_number: number; count: number }[];
  patterns: string[];
  rushing_analysis: RushingAnalysis;
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
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface SyncStatus {
  status: 'idle' | 'syncing' | 'complete' | 'error';
  games_fetched: number;
  total_archives: number;
  message: string;
}
