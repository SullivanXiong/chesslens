import { useParams } from 'react-router-dom';
import { useWeaknesses } from '@/hooks/use-queries';
import { AlertTriangle, Clock, Target } from 'lucide-react';

export default function WeaknessesPage() {
  const { username } = useParams<{ username: string }>();
  const weaknesses = useWeaknesses(username!);

  if (weaknesses.isLoading) return <div className="text-center py-12 text-muted-foreground">Loading analysis...</div>;
  if (weaknesses.error) return <div className="text-center py-12 text-destructive">Analyze some games first.</div>;

  const data = weaknesses.data;
  if (!data) return null;

  const heatmapEntries = Object.entries(data.move_number_heatmap ?? {})
    .map(([move, count]) => ({ move_number: Number(move), count: count as number }))
    .sort((a, b) => a.move_number - b.move_number);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Weaknesses</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2 mb-2"><Target className="h-5 w-5 text-muted-foreground" /><p className="text-sm text-muted-foreground">Opening</p></div>
          <p className="text-2xl font-bold">{(data.phase_breakdown.opening ?? 0).toFixed(1)} ACPL</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2 mb-2"><AlertTriangle className="h-5 w-5 text-muted-foreground" /><p className="text-sm text-muted-foreground">Middlegame</p></div>
          <p className="text-2xl font-bold">{(data.phase_breakdown.middlegame ?? 0).toFixed(1)} ACPL</p>
        </div>
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center gap-2 mb-2"><Clock className="h-5 w-5 text-muted-foreground" /><p className="text-sm text-muted-foreground">Endgame</p></div>
          <p className="text-2xl font-bold">{(data.phase_breakdown.endgame ?? 0).toFixed(1)} ACPL</p>
        </div>
      </div>

      {/* Rushing analysis */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="text-lg font-semibold mb-4">Time Pressure Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-3xl font-bold">{(data.rushing_analysis.blunder_rate_over_60s * 100).toFixed(1)}%</p>
            <p className="text-sm text-muted-foreground">Normal blunder rate</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-eval-blunder">{(data.rushing_analysis.blunder_rate_under_60s * 100).toFixed(1)}%</p>
            <p className="text-sm text-muted-foreground">Under 60s blunder rate</p>
          </div>
          <div>
            <p className="text-3xl font-bold">{data.rushing_analysis.time_trouble_multiplier.toFixed(1)}x</p>
            <p className="text-sm text-muted-foreground">Time pressure multiplier</p>
          </div>
        </div>
        {data.rushing_analysis.verdict && (
          <p className="text-sm text-muted-foreground text-center mt-4">{data.rushing_analysis.verdict}</p>
        )}
      </div>

      {/* Blunder heatmap */}
      {heatmapEntries.length > 0 && (
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">Blunder Heatmap (by move number)</h3>
          <div className="flex items-end gap-1 h-32">
            {heatmapEntries.map((b) => {
              const maxCount = Math.max(...heatmapEntries.map((x) => x.count), 1);
              const height = (b.count / maxCount) * 100;
              return (
                <div key={b.move_number} className="flex-1 flex flex-col items-center" title={`Move ${b.move_number}: ${b.count} blunders`}>
                  <div className="w-full bg-eval-blunder/80 rounded-t" style={{ height: `${height}%` }} />
                  <span className="text-[10px] text-muted-foreground mt-1">{b.move_number}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Patterns */}
      {data.recurring_patterns && data.recurring_patterns.length > 0 && (
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-3">Identified Patterns</h3>
          <ul className="space-y-2">
            {data.recurring_patterns.map((p: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <AlertTriangle className="h-4 w-4 text-eval-mistake mt-0.5 shrink-0" />
                {p}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
