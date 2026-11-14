"use client";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const ROLES = [
  { id: "full_stack_developer", label: "Full Stack Developer" },
  { id: "data_analyst", label: "Data Analyst" },
  { id: "ml_engineer", label: "ML Engineer" },
  { id: "backend_developer", label: "Backend Developer" },
];

export default function PivotPage({ params }: { params: { userId: string } }) {
  const userId = +params.userId;
  const [newRole, setNewRole] = useState("data_analyst");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [confirmed, setConfirmed] = useState(false);

  const analyze = async () => {
    setLoading(true); setData(null); setConfirmed(false);
    const r = await fetch(`${API}/pivot/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_role: newRole }),
    });
    setData(await r.json());
    setLoading(false);
  };

  const confirm = async () => {
    await fetch(`${API}/events/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event_type: "goal_changed", payload: { role_id: newRole } }),
    });
    setConfirmed(true);
  };

  return (
    <main className="min-h-screen p-8 max-w-5xl mx-auto flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold text-indigo-400">🔄 Career Pivot</h1>
        <p className="text-gray-400 mt-1">See what transfers, what's new, and how much progress you keep.</p>
      </div>

      <div className="flex gap-4 items-end flex-wrap">
        <div className="flex flex-col gap-1">
          <label className="text-sm text-gray-400">New Target Role</label>
          <select value={newRole} onChange={e => setNewRole(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white">
            {ROLES.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
          </select>
        </div>
        <button onClick={analyze} disabled={loading}
          className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl text-white font-semibold transition">
          {loading ? "Analyzing…" : "Analyze Pivot"}
        </button>
      </div>

      {data && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Transfers", value: `${data.transfer_percent}%`, color: "text-green-400", sub: `${data.transferable.length} skills` },
              { label: "Hours Saved", value: `${data.hours_saved}h`, color: "text-indigo-400", sub: "vs. starting fresh" },
              { label: "New Match", value: `${data.new_match_percent}%`, color: "text-yellow-400", sub: "immediately" },
              { label: "Weeks Needed", value: data.new_roadmap_weeks, color: "text-white", sub: "to reach goal" },
            ].map(s => (
              <div key={s.label} className="bg-gray-900 rounded-xl p-4">
                <p className="text-gray-400 text-sm">{s.label}</p>
                <p className={`text-3xl font-bold mt-1 ${s.color}`}>{s.value}</p>
                <p className="text-xs text-gray-500 mt-1">{s.sub}</p>
              </div>
            ))}
          </div>

          {/* Three-column diff */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Section title="✅ Transfers" color="green" items={data.transferable}
              render={(s: any) => `${s.skill_id.replace(/_/g," ")} (${Math.round(s.mastery*100)}%)`} />
            <Section title="🔄 Partial / Needs Work" color="yellow" items={data.partial}
              render={(s: any) => `${s.skill_id.replace(/_/g," ")} (+${Math.round(s.gap*100)}% needed)`} />
            <Section title="🆕 New Skills" color="red" items={data.new_needed}
              render={(s: any) => `${s.skill_id.replace(/_/g," ")} (target: ${Math.round(s.required*100)}%)`} />
          </div>

          {!confirmed ? (
            <button onClick={confirm}
              className="px-8 py-3 bg-green-600 hover:bg-green-500 rounded-xl font-semibold text-white transition w-fit">
              Confirm Pivot → Rebuild Roadmap
            </button>
          ) : (
            <div className="text-green-400 font-semibold">
              ✅ Goal updated! <a href={`/roadmap/${userId}`} className="underline">View new roadmap →</a>
            </div>
          )}
        </>
      )}
    </main>
  );
}

function Section({ title, color, items, render }: {
  title: string; color: string; items: any[]; render: (s: any) => string;
}) {
  const colorMap: Record<string, string> = {
    green: "border-green-700 bg-green-900/20",
    yellow: "border-yellow-700 bg-yellow-900/20",
    red: "border-red-700 bg-red-900/20",
  };
  return (
    <div className={`border rounded-2xl p-4 flex flex-col gap-2 ${colorMap[color]}`}>
      <h3 className="font-semibold text-white text-sm">{title} ({items.length})</h3>
      {items.length === 0
        ? <p className="text-gray-500 text-xs">None</p>
        : items.map((s: any) => (
          <p key={s.skill_id} className="text-xs text-gray-300">{render(s)}</p>
        ))
      }
    </div>
  );
}
