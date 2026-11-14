"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { SkillRadar } from "@/components/SkillRadar";

const COLOR_DOT: Record<string, string> = {
  green: "bg-green-500", yellow: "bg-yellow-400",
  red: "bg-red-500", grey: "bg-gray-600",
};
const COLOR_LABEL: Record<string, string> = {
  green: "Mastered", yellow: "Learning", red: "Gap", grey: "Locked",
};

export default function DashboardPage({ params }: { params: { userId: string } }) {
  const userId = +params.userId;
  const [profile, setProfile] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getProfile(userId), api.skillAnalysis(userId)])
      .then(([p, a]) => { setProfile(p); setAnalysis(a); })
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <main className="p-8 text-gray-400">Loading your Skill Twin…</main>;
  if (!profile) return <main className="p-8 text-red-400">Profile not found.</main>;

  const knownNodes = analysis?.nodes?.filter((n: any) => n.color !== "grey") ?? [];
  const byColor = knownNodes.reduce((acc: any, n: any) => {
    acc[n.color] = (acc[n.color] || 0) + 1; return acc;
  }, {});

  return (
    <main className="min-h-screen p-8 max-w-5xl mx-auto flex flex-col gap-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-indigo-400">⚡ {profile.name}'s Skill Twin</h1>
        <p className="text-gray-400 mt-1">Goal: <span className="text-white font-medium">
          {profile.goal_role.replace(/_/g, " ").replace(/\b\w/g, (c: string) => c.toUpperCase())}
        </span> · {profile.weekly_hours}h/week</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(COLOR_LABEL).map(([color, label]) => (
          <div key={color} className="bg-gray-900 rounded-xl p-4 flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${COLOR_DOT[color]}`} />
              <span className="text-gray-400 text-sm">{label}</span>
            </div>
            <span className="text-2xl font-bold text-white">{byColor[color] ?? 0}</span>
          </div>
        ))}
      </div>

      {/* Radar */}
      <div className="bg-gray-900 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">Skill Strength Radar</h2>
        <SkillRadar data={analysis?.radar ?? []} />
      </div>

      {/* Skill list */}
      <div className="bg-gray-900 rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">Detected Skills</h2>
        {profile.skills.length === 0
          ? <p className="text-gray-500">No skills detected. Try adding more context in onboarding.</p>
          : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {profile.skills.map((s: any) => (
                <div key={s.skill_id} className="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3">
                  <span className="text-white font-medium">{s.skill_id.replace(/_/g, " ")}</span>
                  <div className="flex items-center gap-3">
                    <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-500 rounded-full"
                        style={{ width: `${Math.round(s.mastery * 100)}%` }} />
                    </div>
                    <span className="text-gray-400 text-sm w-10 text-right">{Math.round(s.mastery * 100)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
      </div>

      <div className="flex gap-3">
        <a href={`/match/${userId}`}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold text-white transition">
          Career Match →
        </a>
      </div>
    </main>
  );
}
