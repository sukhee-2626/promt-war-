"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STATUS_COLOR: Record<string, string> = {
  pending:    "border-gray-600 bg-gray-800",
  in_progress:"border-indigo-500 bg-indigo-900/30",
  complete:   "border-green-500 bg-green-900/30",
};

export default function RoadmapPage({ params }: { params: { userId: string } }) {
  const userId = +params.userId;
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/roadmap/${userId}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); });
  }, [userId]);

  if (loading) return <main className="p-8 text-gray-400">Building your roadmap…</main>;
  if (!data)   return <main className="p-8 text-red-400">Failed to load roadmap.</main>;

  // Group nodes by milestone
  const milestones: Record<string, any[]> = {};
  for (const node of data.nodes) {
    if (!milestones[node.milestone]) milestones[node.milestone] = [];
    milestones[node.milestone].push(node);
  }

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold text-indigo-400">📍 Your Learning Roadmap</h1>
        <p className="text-gray-400 mt-1">
          {data.total_weeks} weeks · {data.nodes.length} skills · {Math.round(data.match_percent)}% match so far
        </p>
      </div>

      {/* Timeline */}
      <div className="flex flex-col gap-6">
        {Object.entries(milestones).map(([ms, nodes]) => (
          <div key={ms} className="flex flex-col gap-3">
            <h2 className="text-indigo-300 font-semibold text-sm uppercase tracking-wider">{ms}</h2>
            {nodes.map((node: any) => (
              <div key={node.skill_id}
                className={`border rounded-xl p-4 flex items-start gap-4 ${STATUS_COLOR[node.status] || STATUS_COLOR.pending}`}>
                <div className="w-8 h-8 rounded-full bg-indigo-700 flex items-center justify-center text-xs font-bold text-white shrink-0">
                  {node.order}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start flex-wrap gap-2">
                    <span className="font-semibold text-white">{node.skill_name}</span>
                    <span className="text-xs text-gray-400">
                      Week {node.week_start}–{node.week_end} · ~{node.est_hours}h
                    </span>
                  </div>
                  <div className="mt-2 flex gap-2">
                    <a href={`/assess/${userId}/${node.skill_id}`}
                      className="text-xs px-3 py-1 rounded-lg bg-indigo-700 hover:bg-indigo-600 text-white transition">
                      Take Assessment
                    </a>
                    <a href={`/resources/${node.skill_id}`}
                      className="text-xs px-3 py-1 rounded-lg bg-gray-700 hover:bg-gray-600 text-white transition">
                      Resources
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="flex gap-3 flex-wrap">
        <a href={`/assess/${userId}/javascript`}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold text-white transition">
          Start First Assessment →
        </a>
        <a href={`/pivot/${userId}`}
          className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-xl font-semibold text-white transition">
          Change Goal
        </a>
      </div>
    </main>
  );
}
