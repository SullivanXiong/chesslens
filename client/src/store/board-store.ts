import { create } from 'zustand';

interface BoardState {
  currentMoveIndex: number;
  orientation: 'white' | 'black';
  setMoveIndex: (index: number) => void;
  nextMove: (maxIndex: number) => void;
  prevMove: () => void;
  firstMove: () => void;
  lastMove: (maxIndex: number) => void;
  setOrientation: (o: 'white' | 'black') => void;
  flipBoard: () => void;
}

export const useBoardStore = create<BoardState>((set) => ({
  currentMoveIndex: 0,
  orientation: 'white',
  setMoveIndex: (index) => set({ currentMoveIndex: index }),
  nextMove: (maxIndex) => set((s) => ({ currentMoveIndex: Math.min(s.currentMoveIndex + 1, maxIndex) })),
  prevMove: () => set((s) => ({ currentMoveIndex: Math.max(s.currentMoveIndex - 1, 0) })),
  firstMove: () => set({ currentMoveIndex: 0 }),
  lastMove: (maxIndex) => set({ currentMoveIndex: maxIndex }),
  setOrientation: (o) => set({ orientation: o }),
  flipBoard: () => set((s) => ({ orientation: s.orientation === 'white' ? 'black' : 'white' })),
}));
