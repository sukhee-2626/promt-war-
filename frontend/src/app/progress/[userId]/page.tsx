"use client";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ProgressPage({ params }: { params: { userId: string } }) {
  const userId = +params.userId;
  const [profile, setProfile] = useState<any>(null);
  const [match, setMatch]     = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/profile/${userId}`).then(r => r.json()),
      fetch(`${API}/match/${userId}`).then(r => r.json()),
    ]).then(([p, m]) => { setProfile(p); setMatch(m); setLoading(false); });
  }, [userId]);

  if (loading) return <main className="p-8 text-gray-400">Loading progress…</main>;

  const skills = profile?.skills ?? [];
  const topSkills = [...skills].sort((a: any, b: any) => b.mastery - a.mastery).slice(0, 10);
  const masteredCount = skills.filter((s: any) => s.mastery >= 0.8).length;
  const inProgressCount = skills.filter((s: any) => s.mastery >= 0.4 && s.mastery < 0.8).length;

  return (
    <main className="min-h-screen p-8 max-w-5xl mx-auto flex flex-col gap-8">
      <div>
        <h1 className="text-3xl font-bold text-indigo-400">📊 Progress Dashboard</h1>
        <p className="text-gray-400 mt-1">{profile?.name} · {profile?.goal_role?.replace(/_/g, " ")}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Match %", value: `${match?.match_percent ?? 0}%`, color: "text-indigo-400" },
          { label: "Mastered", value: masteredCount, color: "text-green-400" },
          { label: "In Progress", value: inProgressCount, color: "text-yellow-400" },
          { label: "Gaps Left", value: match?.gaps?.length ?? 0, color: "text-red-400" },
        ].map(s => (
          <div key={s.label} className="bg-gray-900 rounded-xl p-4">
            <p className="text-gray-400 text-sm">{s.label}</p>
            <p className={`text-3xl font-bold mt-1 ${s.color}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Mastery chart */}
      <div className="bg-gray-900 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">Top Skills by Mastery</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={topSkills.map((s: any) => ({
            name: s.skill_id.replace(/_/g, " ").slice(0, 12),
            mastery: Math.round(s.mastery * 100),
          }))}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: "#9CA3AF", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "#1F2937", border: "none", borderRadius: 8 }}
              formatter={(v: number) => [`${v}%`, "Mastery"]} />
            <Line type="monotone" dataKey="mastery" stroke="#6366F1" strokeWidth={2} dot={{ fill: "#6366F1" }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Top gaps */}
      <div className="bg-gray-900 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">Top Gaps to Close</h2>
        {match?.gaps?.slice(0, 5).map((g: any) => (
          <div key={g.skill_id} className="flex items-center justify-between py-2 border-b border-gray-800">
            <span className="text-white">{g.skill_name}</span>
            <div className="flex items-center gap-3">
              <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-red-500 rounded-full" style={{ width: `${g.current_mastery * 100}%` }} />
              </div>
              <span className="text-xs text-gray-400 w-16 text-right">
                {Math.round(g.current_mastery * 100)}% / {Math.round(g.required_mastery * 100)}%
              </span>
              <a href={`/assess/${userId}/${g.skill_id}`}
                className="text-xs px-2 py-1 bg-indigo-700 hover:bg-indigo-600 rounded-lg text-white">
                Practice
              </a>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
