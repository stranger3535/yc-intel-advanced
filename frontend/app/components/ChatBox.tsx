"use client";

import { useState, useRef, useEffect } from "react";
import { chat as askChat } from "../../lib/api";
import ExampleQuestions from "./ExampleQuestions";
import MessageBubble from "./MessageBubble";

type Message = {
  role: "user" | "bot";
  text: string;
};

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(question?: string) {
    if (loading) return;

    const q = (question ?? input).trim();
    if (!q) return;

    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setInput("");
    setLoading(true);

    try {
      const data = await askChat(q);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.answer },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "⚠️ Backend not reachable. Is FastAPI running?",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-3xl mx-auto bg-slate-950 rounded-xl shadow-lg p-6">
      <h1 className="text-2xl font-bold mb-4">YC Intel Chat</h1>

      <ExampleQuestions onSelect={send} />

      <div className="mt-4 space-y-3 min-h-[300px] max-h-[420px] overflow-y-auto">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} text={m.text} />
        ))}
        {loading && <div className="text-slate-400 text-sm">Thinking…</div>}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2 mt-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask about YC companies…"
          disabled={loading}
          className="flex-1 px-3 py-2 rounded bg-slate-800 text-white"
        />
        <button
          onClick={() => send()}
          disabled={loading}
          className="px-4 py-2 bg-green-500 rounded text-black font-semibold"
        >
          Send
        </button>
      </div>
    </div>
  );
}
