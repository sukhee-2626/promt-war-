"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AgentActivityPage({ params }: { params: { userId: string; roadmapId: string } }) {
  const { userId, roadmapId } = params;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/mentor/${userId}/debate/${roadmapId}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); });
  }, [userId, roadmapId]);

  if (loading) return <main className="p-8 text-gray-400">Running agent debate…</main>;

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold text-indigo-400">🤖 Agent Debate</h1>
        <p className="text-gray-400 mt-1">Planner proposes · Critic reviews · Best plan wins</p>
      </div>

      <div className="flex flex-col gap-4">
        {data?.transcript?.map((turn: any, i: number) => (
          <div key={i} className={`rounded-2xl p-5 border ${
            turn.speaker === "Planner"
              ? "border-indigo-600 bg-indigo-900/20"
              : turn.approved
                ? "border-green-600 bg-green-900/20"
                : "border-red-600 bg-red-900/20"
          }`}>
            <div className="flex items-center gap-3 mb-3">
              <span className={`text-sm font-bold px-3 py-1 rounded-full ${
                turn.speaker === "Planner" ? "bg-indigo-700 text-white" : "bg-orange-700 text-white"
              }`}>{turn.speaker}</span>
              <span className="text-gray-400 text-sm">Round {turn.round}</span>
              {turn.approved !== undefined && (
                <span className={`text-sm font-semibold ${turn.approved ? "text-green-400" : "text-red-400"}`}>
                  {turn.approved ? "✅ Approved" : "❌ Issues Found"}
                </span>
              )}
            </div>
            <p className="text-white">{turn.content}</p>
            {turn.issues?.length > 0 && (
              <ul className="mt-3 flex flex-col gap-1">
                {turn.issues.map((issue: any, ii: number) => (
                  <li key={ii} className="text-sm text-red-300">
                    ⚠️ [{issue.type}] {issue.description}
                  </li>
                ))}
              </ul>
            )}
            {turn.nodes && (
              <div className="mt-3 flex flex-wrap gap-2">
                {turn.nodes.map((n: any) => (
                  <span key={n.skill_id} className="text-xs bg-gray-800 px-2 py-1 rounded-lg text-gray-300">
                    #{n.order} {n.skill_name}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {data?.final_nodes && (
        <div className="bg-gray-900 rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-3">
            Final Plan — {data.total_weeks} weeks, {data.final_nodes.length} skills
          </h2>
          <div className="flex flex-wrap gap-2">
            {data.final_nodes.map((n: any) => (
              <span key={n.skill_id} className="text-xs bg-indigo-900/50 border border-indigo-700 px-3 py-1 rounded-lg text-indigo-300">
                {n.order}. {n.skill_name}
              </span>
            ))}
          </div>
        </div>
      )}

      <a href={`/roadmap/${userId}`}
        className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold text-white transition w-fit">
        ← Back to Roadmap
      </a>
    </main>
  );
}
