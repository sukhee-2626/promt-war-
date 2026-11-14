"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const ROLES = ["full_stack_developer", "data_analyst", "ml_engineer", "backend_developer"];

export default function OnboardingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "", email: "", goal_role: "full_stack_developer",
    weekly_hours: 10, free_text: "", github_descriptions: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const result = await api.createProfile({
        ...form,
        github_descriptions: form.github_descriptions
          ? form.github_descriptions.split("\n").filter(Boolean)
          : [],
        resume_text: "",
      });
      router.push(`/dashboard/${result.id}`);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const field = (label: string, key: keyof typeof form, type = "text", extra?: any) => (
    <div className="flex flex-col gap-1">
      <label className="text-sm text-gray-400">{label}</label>
      <input
        type={type}
        value={form[key] as string}
        onChange={e => setForm(f => ({ ...f, [key]: type === "number" ? +e.target.value : e.target.value }))}
        className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
        {...extra}
      />
    </div>
  );

  return (
    <main className="min-h-screen flex items-center justify-center p-6">
      <form onSubmit={handleSubmit} className="bg-gray-900 rounded-2xl p-8 w-full max-w-lg flex flex-col gap-5 shadow-xl">
        <h1 className="text-2xl font-bold text-indigo-400">Create Your Skill Profile</h1>

        {field("Full Name", "name", "text", { required: true })}
        {field("Email", "email", "email", { required: true })}

        <div className="flex flex-col gap-1">
          <label className="text-sm text-gray-400">Target Role</label>
          <select
            value={form.goal_role}
            onChange={e => setForm(f => ({ ...f, goal_role: e.target.value }))}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
          >
            {ROLES.map(r => <option key={r} value={r}>{r.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</option>)}
          </select>
        </div>

        {field("Weekly Learning Hours", "weekly_hours", "number")}

        <div className="flex flex-col gap-1">
          <label className="text-sm text-gray-400">About You / Current Skills (free text)</label>
          <textarea
            value={form.free_text}
            onChange={e => setForm(f => ({ ...f, free_text: e.target.value }))}
            rows={4}
            placeholder="e.g. I know Python, SQL, basic HTML. I've built a Flask app..."
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500 resize-none"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm text-gray-400">GitHub Repo Descriptions (one per line)</label>
          <textarea
            value={form.github_descriptions}
            onChange={e => setForm(f => ({ ...f, github_descriptions: e.target.value }))}
            rows={3}
            placeholder="e.g. A REST API built with FastAPI and PostgreSQL..."
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500 resize-none"
          />
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}

        <button
          type="submit" disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl py-3 font-semibold text-white transition"
        >
          {loading ? "Analyzing Skills…" : "Build My Skill Twin →"}
        </button>
      </form>
    </main>
  );
}
