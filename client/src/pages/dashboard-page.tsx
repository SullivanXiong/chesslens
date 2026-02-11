import { useParams, Link } from 'react-router-dom';
import { usePlayer, useSyncPlayer, useGames } from '@/hooks/use-queries';
import { RefreshCw, TrendingUp, Swords, Clock } from 'lucide-react';

export default function DashboardPage() {
  const { username } = useParams<{ username: string }>();
  const player = usePlayer(username!);
  const games = useGames(username!, { page: 1 });
  const sync = useSyncPlayer(username!);

  if (player.isLoading) return <div className="text-center py-12 text-muted-foreground">Loading player...</div>;
  if (player.error) return <div className="text-center py-12 text-destructive">Failed to load player. Is the server running?</div>;

  const p = player.data;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          {p?.avatar_url && <img src={p.avatar_url} alt="" className="h-12 w-12 rounded-full" />}
          <div>
            <h2 className="text-2xl font-bold">{p?.username}</h2>
            <p className="text-sm text-muted-foreground">Last synced: {p?.last_synced_at ? new Date(p.last_synced_at).toLocaleDateString() : 'Never'}</p>
          </div>
        </div>
        <button
          onClick={() => sync.mutate()}
          disabled={sync.isPending}
          className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${sync.isPending ? 'animate-spin' : ''}`} />
          {sync.isPending ? 'Syncing...' : 'Sync Games'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard icon={TrendingUp} label="Rapid" value={p?.ratings?.rapid ?? 'N/A'} />
        <StatCard icon={Clock} label="Blitz" value={p?.ratings?.blitz ?? 'N/A'} />
        <StatCard icon={Swords} label="Bullet" value={p?.ratings?.bullet ?? 'N/A'} />
      </div>

      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Recent Games</h3>
          <Link to="games" className="text-sm text-primary hover:underline">View all</Link>
        </div>
        {games.isLoading && <p className="text-muted-foreground">Loading games...</p>}
        {games.data && games.data.games.length === 0 && <p className="text-muted-foreground">No games found. Click "Sync Games" to fetch from Chess.com.</p>}
        {games.data && games.data.games.slice(0, 5).map((g) => (
          <Link key={g.id} to={`games/${g.id}`} className="flex items-center justify-between py-2 border-b last:border-0 hover:bg-muted/50 px-2 rounded">
            <div className="flex items-center gap-3">
              <span className={`text-xs font-medium px-2 py-0.5 rounded ${g.player_result === 'win' ? 'bg-green-100 text-green-800' : g.player_result === 'loss' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {g.player_result}
              </span>
              <span className="text-sm">{g.opening_name || g.eco}</span>
            </div>
            <span className="text-xs text-muted-foreground">{new Date(g.played_at).toLocaleDateString()}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value }: { icon: any; label: string; value: string | number }) {
  return (
    <div className="rounded-lg border bg-card p-4 flex items-center gap-3">
      <Icon className="h-8 w-8 text-muted-foreground" />
      <div>
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
    </div>
  );
}
