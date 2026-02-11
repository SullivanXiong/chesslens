import { LineChart, Line, XAxis, YAxis, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';
import type { MoveEvaluation } from '@/types';

interface EvalChartProps {
  moves: MoveEvaluation[];
  currentIndex?: number;
}

export function EvalChart({ moves, currentIndex }: EvalChartProps) {
  const data = moves.map((m, i) => ({
    move: Math.ceil((i + 1) / 2),
    eval: Math.max(-5, Math.min(5, m.score_after_cp / 100)),
    classification: m.classification,
    san: m.san,
  }));

  return (
    <div className="h-48 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <XAxis dataKey="move" tick={{ fontSize: 10 }} />
          <YAxis domain={[-5, 5]} tick={{ fontSize: 10 }} tickFormatter={(v) => `${v > 0 ? '+' : ''}${v}`} />
          <Tooltip
            content={({ payload }) => {
              if (!payload?.[0]) return null;
              const d = payload[0].payload;
              return (
                <div className="rounded border bg-card p-2 text-xs shadow">
                  <p>{d.san} ({d.classification})</p>
                  <p>Eval: {d.eval > 0 ? '+' : ''}{d.eval.toFixed(2)}</p>
                </div>
              );
            }}
          />
          <ReferenceLine y={0} stroke="hsl(var(--border))" />
          <Line type="monotone" dataKey="eval" stroke="hsl(var(--primary))" strokeWidth={1.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
