"use client";

import { useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

export default function ChatPage() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim()) return;

    const question = input;
    setInput("");
    setLoading(true);

    setMessages((m) => [...m, { role: "user", text: question }]);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      setMessages((m) => [...m, { role: "bot", text: data.answer }]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "bot", text: "⚠️ Server error" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
  <main>
    <div className="page">
      <div className="chat-box">
        <h1>YC Intel Chat</h1>

        <div className="examples">
          {[
            "Top fast-growing YC startups",
            "YC companies working on AI",
            "Recent stage changes in YC companies",
            "Fastest growing tags in YC",
          ].map((q) => (
            <div key={q} className="example" onClick={() => setInput(q)}>
              {q}
            </div>
          ))}
        </div>

        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={m.role}>
              <strong>{m.role === "user" ? "You:" : "Bot:"}</strong> {m.text}
            </div>
          ))}
          {loading && <div className="thinking">Thinking…</div>}
        </div>

        <div className="input-row">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about YC companies..."
          />
          <button onClick={send} disabled={loading}>
            Send
          </button>
        </div>
      </div>
    </div>
  </main>
);
}