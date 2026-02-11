import { useParams, Link } from 'react-router-dom';
import { useGame, useTriggerAnalysis } from '@/hooks/use-queries';
import { useBoardStore } from '@/store/board-store';
import { ChessBoard } from '@/components/chess-board';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, RotateCw, Zap } from 'lucide-react';

const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

export default function GameDetailPage() {
  const { username, gameId } = useParams<{ username: string; gameId: string }>();
  const game = useGame(username!, Number(gameId));
  const analysis = useTriggerAnalysis();
  const { currentMoveIndex, setMoveIndex, nextMove, prevMove, firstMove, lastMove, flipBoard, orientation } = useBoardStore();

  if (game.isLoading) return <div className="text-center py-12 text-muted-foreground">Loading game...</div>;
  if (!game.data) return <div className="text-center py-12 text-destructive">Game not found</div>;

  const g = game.data;
  const moves = g.moves || [];
  const currentMove = currentMoveIndex >= 0 && currentMoveIndex < moves.length ? moves[currentMoveIndex] : null;
  const fen = currentMove ? currentMove.fen_after : START_FEN;

  const topPlayer = orientation === 'white'
    ? { name: g.opponent_username, rating: g.opponent_rating }
    : { name: username, rating: g.player_color === 'white' ? null : g.opponent_rating };
  const bottomPlayer = orientation === 'white'
    ? { name: username, rating: null }
    : { name: g.opponent_username, rating: g.opponent_rating };

  const resultBadge = g.player_result === 'win'
    ? 'bg-green-100 text-green-800'
    : g.player_result === 'loss'
      ? 'bg-red-100 text-red-800'
      : 'bg-yellow-100 text-yellow-800';

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link to={`/${username}/games`} className="hover:underline">Games</Link>
        <span>/</span>
        <span>{g.opening_name || g.eco || 'Unknown Opening'}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Board + controls */}
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-lg border bg-card p-4">
            <div className="flex justify-between items-center mb-2 text-sm">
              <span className="font-medium">{topPlayer.name} {topPlayer.rating != null ? `(${topPlayer.rating})` : ''}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${resultBadge}`}>
                {g.player_result}
              </span>
            </div>
            <ChessBoard fen={fen} orientation={orientation} />
            <div className="flex justify-between items-center mt-2 text-sm">
              <span className="font-medium">{bottomPlayer.name} {bottomPlayer.rating != null ? `(${bottomPlayer.rating})` : ''}</span>
            </div>
            <div className="flex items-center justify-center gap-2 mt-4">
              <button onClick={() => firstMove()} className="rounded border p-2 hover:bg-muted"><ChevronsLeft className="h-4 w-4" /></button>
              <button onClick={() => prevMove()} className="rounded border p-2 hover:bg-muted"><ChevronLeft className="h-4 w-4" /></button>
              <button onClick={() => nextMove(moves.length - 1)} className="rounded border p-2 hover:bg-muted"><ChevronRight className="h-4 w-4" /></button>
              <button onClick={() => lastMove(moves.length - 1)} className="rounded border p-2 hover:bg-muted"><ChevronsRight className="h-4 w-4" /></button>
              <button onClick={flipBoard} className="rounded border p-2 hover:bg-muted ml-2"><RotateCw className="h-4 w-4" /></button>
              {!g.is_analyzed && (
                <button
                  onClick={() => analysis.mutate(g.id)}
                  disabled={analysis.isPending}
                  className="flex items-center gap-1 rounded bg-primary px-3 py-2 text-sm text-primary-foreground hover:bg-primary/90 ml-2"
                >
                  <Zap className="h-4 w-4" />
                  Analyze
                </button>
              )}
            </div>
          </div>

          {/* Move info */}
          {currentMove && (
            <div className="rounded-lg border bg-card p-4 text-sm space-y-1">
              <p className="font-medium">
                Move {Math.ceil((currentMoveIndex + 1) / 2)}{currentMove.is_white ? '.' : '...'} {currentMove.san}
              </p>
              {currentMove.clock_seconds != null && (
                <p className="text-muted-foreground">
                  Clock: {Math.floor(currentMove.clock_seconds / 60)}:{String(Math.floor(currentMove.clock_seconds % 60)).padStart(2, '0')}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Move list sidebar */}
        <div className="rounded-lg border bg-card p-4 max-h-[600px] overflow-y-auto">
          <h3 className="font-semibold mb-3">Moves</h3>
          <div className="flex flex-wrap gap-0.5">
            {moves.map((m, i) => (
              <button
                key={i}
                onClick={() => setMoveIndex(i)}
                className={`inline-block px-1.5 py-0.5 rounded text-xs font-mono cursor-pointer hover:bg-muted ${i === currentMoveIndex ? 'ring-2 ring-ring bg-muted' : ''}`}
              >
                {m.is_white ? `${Math.ceil((i + 1) / 2)}. ` : ''}{m.san}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
