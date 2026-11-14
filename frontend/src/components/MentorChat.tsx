"use client";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Message { role: "user" | "mentor"; text: string; }

export function MentorChat({ userId }: { userId: number }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "mentor", text: "Hi! I'm your SkillForge Mentor. Ask me anything about your learning path." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setMessages(m => [...m, { role: "user", text: userMsg }]);
    setInput("");
    setLoading(true);
    try {
      const r = await fetch(`${API}/mentor/${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await r.json();
      setMessages(m => [...m, { role: "mentor", text: data.reply }]);
    } catch {
      setMessages(m => [...m, { role: "mentor", text: "Connection error. Try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 w-80 bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl flex flex-col" style={{ maxHeight: 480 }}>
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
        <span className="text-indigo-400 font-semibold text-sm">⚡ Mentor</span>
        <span className="text-xs text-gray-500">AI-powered guide</span>
      </div>

      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2" style={{ minHeight: 200 }}>
        {messages.map((m, i) => (
          <div key={i} className={`text-xs rounded-xl px-3 py-2 max-w-[90%] ${
            m.role === "user"
              ? "bg-indigo-700 text-white self-end"
              : "bg-gray-800 text-gray-200 self-start"
          }`}>{m.text}</div>
        ))}
        {loading && <div className="text-xs text-gray-500 self-start px-3">Thinking…</div>}
      </div>

      <div className="p-3 border-t border-gray-700 flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          placeholder="Ask your mentor…"
          className="flex-1 bg-gray-800 text-white text-xs rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button onClick={send} disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-3 py-2 rounded-lg disabled:opacity-50">
          →
        </button>
      </div>
    </div>
  );
}
