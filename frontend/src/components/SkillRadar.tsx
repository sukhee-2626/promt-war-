"use client";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";

interface RadarData { category: string; mastery: number; }

export function SkillRadar({ data }: { data: RadarData[] }) {
  if (!data?.length) return <p className="text-gray-500 text-sm">No skills mapped yet.</p>;
  return (
    <ResponsiveContainer width="100%" height={320}>
      <RadarChart data={data}>
        <PolarGrid stroke="#374151" />
        <PolarAngleAxis dataKey="category" tick={{ fill: "#9CA3AF", fontSize: 12 }} />
        <Radar name="Mastery" dataKey="mastery" stroke="#6366F1" fill="#6366F1" fillOpacity={0.4} />
        <Tooltip
          contentStyle={{ background: "#1F2937", border: "none", borderRadius: 8 }}
          formatter={(v: number) => [`${Math.round(v * 100)}%`, "Mastery"]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
