import { useParams, Link } from 'react-router-dom';
import { useGame, useTriggerAnalysis } from '@/hooks/use-queries';
import { useBoardStore } from '@/store/board-store';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, RotateCw, Zap } from 'lucide-react';

export default function GameDetailPage() {
  const { username, gameId } = useParams<{ username: string; gameId: string }>();
  const game = useGame(username!, Number(gameId));
  const analysis = useTriggerAnalysis();
  const { currentMoveIndex, setMoveIndex, nextMove, prevMove, firstMove, lastMove, flipBoard, orientation } = useBoardStore();

  if (game.isLoading) return <div className="text-center py-12 text-muted-foreground">Loading game...</div>;
  if (!game.data) return <div className="text-center py-12 text-destructive">Game not found</div>;

  const g = game.data;
  const moves = g.moves || [];
  const currentMove = moves[currentMoveIndex];
  const fen = currentMove ? currentMove.fen_after : 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link to={`/${username}/games`} className="hover:underline">Games</Link>
        <span>/</span>
        <span>{g.opening_name || g.eco}</span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Board + controls */}
        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-lg border bg-card p-4">
            <div className="flex justify-between items-center mb-2 text-sm">
              <span>{g.black_username} ({g.black_rating})</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${g.player_result === 'win' ? 'bg-green-100 text-green-800' : g.player_result === 'loss' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {g.result}
              </span>
            </div>
            <div className="aspect-square bg-muted rounded flex items-center justify-center text-muted-foreground">
              {/* Chess board will be rendered here with react-chessboard */}
              <p className="text-sm">Board: {fen.split(' ')[0].substring(0, 30)}...</p>
            </div>
            <div className="flex justify-between items-center mt-2 text-sm">
              <span>{g.white_username} ({g.white_rating})</span>
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

          {/* Eval info for current move */}
          {currentMove && (
            <div className="rounded-lg border bg-card p-4 text-sm space-y-1">
              <p><strong>Move {Math.ceil((currentMoveIndex + 1) / 2)}{currentMove.is_white ? '.' : '...'} {currentMove.san}</strong></p>
              <p>Eval: {currentMove.score_after_cp / 100} | Loss: {currentMove.centipawn_loss}cp | {currentMove.classification}</p>
              {currentMove.classification !== 'good' && currentMove.classification !== 'book' && (
                <p className="text-muted-foreground">Best was: {currentMove.best_move_san}</p>
              )}
            </div>
          )}
        </div>

        {/* Move list sidebar */}
        <div className="rounded-lg border bg-card p-4 max-h-[600px] overflow-y-auto">
          <h3 className="font-semibold mb-3">Moves</h3>
          <div className="space-y-0.5">
            {moves.map((m, i) => {
              const colors: Record<string, string> = {
                blunder: 'bg-eval-blunder/20 text-eval-blunder',
                mistake: 'bg-eval-mistake/20 text-eval-mistake',
                inaccuracy: 'bg-eval-inaccuracy/20 text-eval-inaccuracy',
                good: '',
                book: 'bg-blue-100 text-blue-800',
                brilliant: 'bg-eval-brilliant/20 text-eval-brilliant',
              };
              return (
                <button
                  key={i}
                  onClick={() => setMoveIndex(i)}
                  className={`inline-block px-1.5 py-0.5 rounded text-xs font-mono cursor-pointer ${i === currentMoveIndex ? 'ring-2 ring-ring' : ''} ${colors[m.classification] || ''}`}
                >
                  {m.is_white ? `${Math.ceil((i + 1) / 2)}. ` : ''}{m.san}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
