import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useGames } from '@/hooks/use-queries';

export default function GamesPage() {
  const { username } = useParams<{ username: string }>();
  const [page, setPage] = useState(1);
  const [timeClass, setTimeClass] = useState<string | undefined>();
  const [result, setResult] = useState<string | undefined>();
  const games = useGames(username!, { page, time_class: timeClass, result });

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Games</h2>
      <div className="flex gap-2 flex-wrap">
        {['all', 'rapid', 'blitz', 'bullet'].map((tc) => (
          <button
            key={tc}
            onClick={() => { setTimeClass(tc === 'all' ? undefined : tc); setPage(1); }}
            className={`rounded-full px-3 py-1 text-sm border ${(tc === 'all' && !timeClass) || timeClass === tc ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`}
          >
            {tc}
          </button>
        ))}
        <span className="border-l mx-2" />
        {['all', 'win', 'loss', 'draw'].map((r) => (
          <button
            key={r}
            onClick={() => { setResult(r === 'all' ? undefined : r); setPage(1); }}
            className={`rounded-full px-3 py-1 text-sm border ${(r === 'all' && !result) || result === r ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}`}
          >
            {r}
          </button>
        ))}
      </div>

      {games.isLoading && <p className="text-muted-foreground py-4">Loading...</p>}
      {games.data && (
        <>
          <div className="rounded-lg border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="text-left px-4 py-2">Date</th>
                  <th className="text-left px-4 py-2">Color</th>
                  <th className="text-left px-4 py-2">Opponent</th>
                  <th className="text-left px-4 py-2">Result</th>
                  <th className="text-left px-4 py-2">Opening</th>
                  <th className="text-left px-4 py-2">Moves</th>
                  <th className="text-left px-4 py-2">Analyzed</th>
                </tr>
              </thead>
              <tbody>
                {games.data.games.map((g) => (
                  <tr key={g.id} className="border-b last:border-0 hover:bg-muted/50">
                    <td className="px-4 py-2"><Link to={String(g.id)} className="hover:underline">{new Date(g.played_at).toLocaleDateString()}</Link></td>
                    <td className="px-4 py-2">{g.player_color}</td>
                    <td className="px-4 py-2">{g.opponent_username} ({g.opponent_rating})</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${g.player_result === 'win' ? 'bg-green-100 text-green-800' : g.player_result === 'loss' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {g.player_result}
                      </span>
                    </td>
                    <td className="px-4 py-2 truncate max-w-[200px]">{g.opening_name || g.eco}</td>
                    <td className="px-4 py-2">{Math.ceil(g.total_moves / 2)}</td>
                    <td className="px-4 py-2">{g.is_analyzed ? '✓' : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">{games.data.total} games total</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="rounded border px-3 py-1 text-sm disabled:opacity-50">Prev</button>
              <span className="px-3 py-1 text-sm">Page {page}</span>
              <button onClick={() => setPage(page + 1)} disabled={games.data.games.length < (games.data.per_page || 20)} className="rounded border px-3 py-1 text-sm disabled:opacity-50">Next</button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
