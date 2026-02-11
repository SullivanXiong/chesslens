import { useParams } from 'react-router-dom';
import { usePlaystyle } from '@/hooks/use-queries';

export default function PlaystylePage() {
  const { username } = useParams<{ username: string }>();
  const playstyle = usePlaystyle(username!);

  if (playstyle.isLoading) return <div className="text-center py-12 text-muted-foreground">Loading playstyle...</div>;
  if (playstyle.error) return <div className="text-center py-12 text-destructive">Analyze some games first.</div>;

  const data = playstyle.data;
  if (!data) return null;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Playstyle</h2>

      <div className="rounded-lg border bg-card p-8 text-center">
        <div className="inline-block rounded-full bg-primary/10 px-6 py-3 mb-4">
          <span className="text-2xl font-bold text-primary">{data.primary_archetype}</span>
        </div>
        <p className="text-muted-foreground">{data.description}</p>
        <p className="text-sm text-muted-foreground mt-2">Secondary: {data.secondary_archetype}</p>
      </div>

      {/* Radar chart data as bars (real radar chart will use Recharts) */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="text-lg font-semibold mb-4">Skill Profile</h3>
        <div className="space-y-3">
          {data.radar_chart.map((axis) => (
            <div key={axis.label} className="flex items-center gap-3">
              <span className="w-24 text-sm text-right">{axis.label}</span>
              <div className="flex-1 bg-muted rounded-full h-4 overflow-hidden">
                <div className="bg-primary h-full rounded-full transition-all" style={{ width: `${axis.value}%` }} />
              </div>
              <span className="w-10 text-sm text-right">{axis.value.toFixed(0)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Archetype scores */}
      <div className="rounded-lg border bg-card p-6">
        <h3 className="text-lg font-semibold mb-4">Archetype Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {Object.entries(data.archetype_scores).sort(([, a], [, b]) => b - a).map(([name, score]) => (
            <div key={name} className="rounded-lg border p-3 text-center">
              <p className="font-medium text-sm">{name}</p>
              <p className="text-lg font-bold">{score.toFixed(0)}%</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
