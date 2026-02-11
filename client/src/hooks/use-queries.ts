import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/api/client';

export function usePlayer(username: string) {
  return useQuery({ queryKey: ['player', username], queryFn: () => api.getPlayer(username), enabled: !!username });
}

export function useSyncPlayer(username: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.syncPlayer(username),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['player', username] }); qc.invalidateQueries({ queryKey: ['games', username] }); },
  });
}

export function useGames(username: string, params?: { page?: number; time_class?: string; result?: string }) {
  return useQuery({ queryKey: ['games', username, params], queryFn: () => api.getGames(username, params), enabled: !!username });
}

export function useGame(username: string, gameId: number) {
  return useQuery({ queryKey: ['game', username, gameId], queryFn: () => api.getGame(username, gameId), enabled: !!username && !!gameId });
}

export function useTriggerAnalysis() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (gameId: number) => api.triggerAnalysis(gameId), onSuccess: () => { qc.invalidateQueries({ queryKey: ['games'] }); } });
}

export function useOpenings(username: string) {
  return useQuery({ queryKey: ['openings', username], queryFn: () => api.getOpenings(username), enabled: !!username });
}

export function useWeaknesses(username: string) {
  return useQuery({ queryKey: ['weaknesses', username], queryFn: () => api.getWeaknesses(username), enabled: !!username });
}

export function usePlaystyle(username: string) {
  return useQuery({ queryKey: ['playstyle', username], queryFn: () => api.getPlaystyle(username), enabled: !!username });
}

export function useCoaching(username: string) {
  return useQuery({ queryKey: ['coaching', username], queryFn: () => api.getCoaching(username), enabled: !!username });
}
