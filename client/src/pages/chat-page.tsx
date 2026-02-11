import { useState, useRef, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useChatStore } from '@/store/chat-store';
import { Send, Trash2 } from 'lucide-react';

export default function ChatPage() {
  const { username } = useParams<{ username: string }>();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isStreaming, addMessage, appendToLast, setStreaming, clearMessages, sessionId } = useChatStore();

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || isStreaming) return;
    setInput('');

    addMessage({ role: 'user', content: text });
    addMessage({ role: 'assistant', content: '' });
    setStreaming(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, username, message: text }),
      });

      if (!res.ok) throw new Error('Chat request failed');
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          // Parse SSE data
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              appendToLast(line.slice(6));
            }
          }
        }
      }
    } catch (err) {
      appendToLast('\n\n[Error: Failed to get response. Is the server running?]');
    } finally {
      setStreaming(false);
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)]">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">AI Coach</h2>
        <button onClick={clearMessages} className="flex items-center gap-1 rounded border px-3 py-1 text-sm hover:bg-muted">
          <Trash2 className="h-3 w-3" /> Clear
        </button>
      </div>

      <div className="flex-1 overflow-y-auto rounded-lg border bg-card p-4 space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground py-12">
            <p className="text-lg font-medium">Ask your AI coach anything</p>
            <p className="text-sm mt-2">Try: "Why do I keep blundering in the middlegame?"</p>
            <p className="text-sm">Or: "In my last game, I played Nf3 because I thought it controlled the center. Was that right?"</p>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${m.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
              {m.content || (isStreaming && i === messages.length - 1 ? '...' : '')}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your games, positions, or improvement..."
          disabled={isStreaming}
          className="flex-1 rounded-md border bg-background px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isStreaming || !input.trim()}
          className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
