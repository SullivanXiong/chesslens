import { create } from 'zustand';
import type { ChatMessage } from '@/types';

interface ChatState {
  messages: ChatMessage[];
  isStreaming: boolean;
  sessionId: string;
  addMessage: (msg: ChatMessage) => void;
  appendToLast: (text: string) => void;
  setStreaming: (v: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isStreaming: false,
  sessionId: crypto.randomUUID(),
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  appendToLast: (text) =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0) {
        const last = msgs[msgs.length - 1];
        msgs[msgs.length - 1] = { ...last, content: last.content + text };
      }
      return { messages: msgs };
    }),
  setStreaming: (v) => set({ isStreaming: v }),
  clearMessages: () => set({ messages: [], sessionId: crypto.randomUUID() }),
}));
