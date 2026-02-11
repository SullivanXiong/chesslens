import { useParams } from 'react-router-dom';
import { useOpenings } from '@/hooks/use-queries';

export default function OpeningsPage() {
  const { username } = useParams<{ username: string }>();
  const openings = useOpenings(username!);

  if (openings.isLoading) return <div className="text-center py-12 text-muted-foreground">Loading openings...</div>;
  if (openings.error) return <div className="text-center py-12 text-destructive">Analyze some games first to see opening data.</div>;

  const data = openings.data;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Opening Repertoire</h2>
      {data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">Repertoire breadth</p>
              <p className="text-2xl font-bold">{data.repertoire_breadth} openings</p>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">Most played</p>
              <p className="text-lg font-semibold">{data.most_played}</p>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">Best performing</p>
              <p className="text-lg font-semibold">{data.best_performing}</p>
            </div>
          </div>
          <div className="rounded-lg border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-left px-4 py-2">ECO</th>
                  <th className="text-left px-4 py-2">Opening</th>
                  <th className="text-right px-4 py-2">Games</th>
                  <th className="text-right px-4 py-2">Win%</th>
                  <th className="text-right px-4 py-2">W/D/L</th>
                  <th className="text-right px-4 py-2">Avg Deviation</th>
                </tr>
              </thead>
              <tbody>
                {data.openings.map((o) => (
                  <tr key={o.eco} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="px-4 py-2 font-mono">{o.eco}</td>
                    <td className="px-4 py-2">{o.name}</td>
                    <td className="px-4 py-2 text-right">{o.games_played}</td>
                    <td className="px-4 py-2 text-right">{(o.win_rate * 100).toFixed(0)}%</td>
                    <td className="px-4 py-2 text-right">{o.wins}/{o.draws}/{o.losses}</td>
                    <td className="px-4 py-2 text-right">Move {o.avg_deviation_move.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
