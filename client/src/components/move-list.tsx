import type { MoveEvaluation } from '@/types';

interface MoveListProps {
  moves: MoveEvaluation[];
  currentIndex: number;
  onMoveClick: (index: number) => void;
}

const classColors: Record<string, string> = {
  brilliant: 'bg-eval-brilliant/20 text-eval-brilliant',
  good: '',
  book: 'bg-blue-50 text-blue-700',
  inaccuracy: 'bg-eval-inaccuracy/20 text-eval-inaccuracy',
  mistake: 'bg-eval-mistake/20 text-eval-mistake',
  blunder: 'bg-eval-blunder/20 text-eval-blunder',
};

export function MoveList({ moves, currentIndex, onMoveClick }: MoveListProps) {
  const rows: { number: number; white?: { move: MoveEvaluation; index: number }; black?: { move: MoveEvaluation; index: number } }[] = [];

  for (let i = 0; i < moves.length; i++) {
    const m = moves[i];
    const moveNum = Math.ceil((i + 1) / 2);
    if (m.is_white) {
      rows.push({ number: moveNum, white: { move: m, index: i } });
    } else {
      if (rows.length > 0 && !rows[rows.length - 1].black) {
        rows[rows.length - 1].black = { move: m, index: i };
      } else {
        rows.push({ number: moveNum, black: { move: m, index: i } });
      }
    }
  }

  return (
    <div className="text-sm font-mono space-y-0.5">
      {rows.map((row) => (
        <div key={row.number} className="flex items-center">
          <span className="w-8 text-right text-muted-foreground mr-1">{row.number}.</span>
          {row.white && (
            <button
              onClick={() => onMoveClick(row.white!.index)}
              className={`px-1.5 py-0.5 rounded cursor-pointer min-w-[60px] text-left ${
                row.white.index === currentIndex ? 'ring-2 ring-ring' : ''
              } ${classColors[row.white.move.classification] || ''}`}
            >
              {row.white.move.san}
            </button>
          )}
          {row.black && (
            <button
              onClick={() => onMoveClick(row.black!.index)}
              className={`px-1.5 py-0.5 rounded cursor-pointer min-w-[60px] text-left ${
                row.black.index === currentIndex ? 'ring-2 ring-ring' : ''
              } ${classColors[row.black.move.classification] || ''}`}
            >
              {row.black.move.san}
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
