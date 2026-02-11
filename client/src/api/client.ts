import type { Player, GameList, GameDetail, AnalysisStatus, AnalysisSummary, OpeningReport, WeaknessReport, PlaystyleReport, CoachingSummary, SyncStatus } from '@/types';

const BASE = '/api';

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, init);
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  getPlayer: (username: string) => fetchJson<Player>(`/player/${username}`),
  syncPlayer: (username: string) => fetchJson<SyncStatus>(`/player/${username}/sync`, { method: 'POST' }),
  getSyncStatus: (username: string) => fetchJson<SyncStatus>(`/player/${username}/sync/status`),

  getGames: (username: string, params?: { page?: number; time_class?: string; result?: string }) => {
    const search = new URLSearchParams();
    if (params?.page) search.set('page', String(params.page));
    if (params?.time_class) search.set('time_class', params.time_class);
    if (params?.result) search.set('result', params.result);
    const qs = search.toString();
    return fetchJson<GameList>(`/player/${username}/games${qs ? `?${qs}` : ''}`);
  },
  getGame: (username: string, gameId: number) => fetchJson<GameDetail>(`/player/${username}/games/${gameId}`),

  triggerAnalysis: (gameId: number) => fetchJson<AnalysisStatus>(`/analysis/game/${gameId}`, { method: 'POST' }),
  getAnalysisStatus: (gameId: number) => fetchJson<AnalysisStatus>(`/analysis/game/${gameId}/status`),
  getAnalysisResult: (gameId: number) => fetchJson<AnalysisSummary>(`/analysis/game/${gameId}/result`),

  getOpenings: (username: string) => fetchJson<OpeningReport>(`/player/${username}/openings`),
  getWeaknesses: (username: string) => fetchJson<WeaknessReport>(`/player/${username}/weaknesses`),
  getPlaystyle: (username: string) => fetchJson<PlaystyleReport>(`/player/${username}/playstyle`),
  getCoaching: (username: string) => fetchJson<CoachingSummary>(`/player/${username}/coaching`),
};
