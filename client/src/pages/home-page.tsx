import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [recent, setRecent] = useState<string[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem('chesslens:recent');
    if (saved) setRecent(JSON.parse(saved));
  }, []);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = username.trim().toLowerCase();
    if (!trimmed) return;
    const updated = [trimmed, ...recent.filter((r) => r !== trimmed)].slice(0, 5);
    localStorage.setItem('chesslens:recent', JSON.stringify(updated));
    navigate(`/${trimmed}`);
  }

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="w-full max-w-md space-y-8 text-center">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">ChessLens</h1>
          <p className="mt-2 text-muted-foreground">Deep analysis of your Chess.com games</p>
        </div>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Chess.com username"
            className="flex-1 rounded-md border bg-background px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
          <button type="submit" className="rounded-md bg-primary px-6 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
            Analyze
          </button>
        </form>
        {recent.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">Recent:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {recent.map((r) => (
                <button key={r} onClick={() => navigate(`/${r}`)} className="rounded-full border px-3 py-1 text-sm hover:bg-muted">
                  {r}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
