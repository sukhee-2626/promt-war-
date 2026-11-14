"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const ROLES = [
  { id: "full_stack_developer", label: "Full Stack Developer" },
  { id: "data_analyst", label: "Data Analyst" },
  { id: "ml_engineer", label: "ML Engineer" },
  { id: "backend_developer", label: "Backend Developer" },
];

function MatchRing({ pct }: { pct: number }) {
  const r = 54, circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <svg width={140} height={140} className="mx-auto">
      <circle cx={70} cy={70} r={r} fill="none" stroke="#1F2937" strokeWidth={12} />
      <circle cx={70} cy={70} r={r} fill="none" stroke="#6366F1" strokeWidth={12}
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        transform="rotate(-90 70 70)" />
      <text x={70} y={70} textAnchor="middle" dominantBaseline="central"
        fill="white" fontSize={22} fontWeight="bold">{pct}%</text>
    </svg>
  );
}

export default function MatchPage({ params }: { params: { userId: string } }) {
  const userId = +params.userId;
  const [role, setRole] = useState("full_stack_developer");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchMatch = async (r: string) => {
    setLoading(true);
    const res = await fetch(`${API}/match/${userId}?role=${r}`);
    setData(await res.json());
    setLoading(false);
  };

  useEffect(() => { fetchMatch(role); }, [role]);

  return (
    <main className="min-h-screen p-8 max-w-4xl mx-auto flex flex-col gap-8">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-3xl font-bold text-indigo-400">Career Match</h1>
        <select value={role} onChange={e => setRole(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white">
          {ROLES.map(r => <option key={r.id} value={r.id}>{r.label}</option>)}
        </select>
      </div>

      {loading && <p className="text-gray-400">Analyzing gaps…</p>}
      {data && !loading && (
        <>
          <div className="bg-gray-900 rounded-2xl p-6 flex flex-col md:flex-row items-center gap-8">
            <div className="flex-1">
              <MatchRing pct={data.match_percent} />
              <p className="text-center text-gray-400 mt-2 text-sm">{data.role_name}</p>
            </div>
            <div className="flex-1">
              <p className="text-gray-300 leading-relaxed">{data.explanation}</p>
              <p className="mt-3 text-green-400 text-sm font-medium">
                ✓ {data.strengths?.length ?? 0} skills meeting the bar
              </p>
            </div>
          </div>

          <div className="bg-gray-900 rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-gray-200 mb-4">Top Gaps (by Impact)</h2>
            <div className="flex flex-col gap-3">
              {data.gaps?.map((g: any) => (
                <div key={g.skill_id} className="bg-gray-800 rounded-xl px-4 py-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium text-white">
                      #{g.priority} {g.skill_name}
                    </span>
                    <span className="text-xs text-gray-400">
                      {Math.round(g.current_mastery * 100)}% → {Math.round(g.required_mastery * 100)}%
                    </span>
                  </div>
                  <div className="relative h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="absolute h-full bg-red-500 rounded-full"
                      style={{ width: `${g.current_mastery * 100}%` }} />
                    <div className="absolute h-full border-r-2 border-indigo-400"
                      style={{ left: `${g.required_mastery * 100}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <a href={`/roadmap/${userId}`}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold text-white transition w-fit">
            Build My Roadmap →
          </a>
        </>
      )}
    </main>
  );
}
