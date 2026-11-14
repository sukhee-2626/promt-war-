"use client";
import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function AssessPage({ params }: { params: { userId: string; skillId: string } }) {
  const { userId, skillId } = params;
  const [quiz, setQuiz] = useState<any>(null);
  const [selected, setSelected] = useState<number[]>([]);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetch(`${API}/assess/${userId}/${skillId}`)
      .then(r => r.json())
      .then(d => { setQuiz(d); setSelected(Array(d.questions?.length ?? 0).fill(-1)); setLoading(false); });
  }, [userId, skillId]);

  const submit = async () => {
    setSubmitting(true);
    const r = await fetch(`${API}/assess/${userId}/${skillId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers: selected }),
    });
    setResult(await r.json());
    setSubmitting(false);
  };

  if (loading) return <main className="p-8 text-gray-400">Generating quiz…</main>;

  const ACTION_STYLE: Record<string, string> = {
    complete: "text-green-400",
    remedial: "text-red-400",
    continue: "text-yellow-400",
  };
  const ACTION_MSG: Record<string, string> = {
    complete: "🎉 Skill mastered! Moving on.",
    remedial: "⚠️ Needs reinforcement. A remedial node will be added.",
    continue: "📈 Good progress! Keep going.",
  };

  return (
    <main className="min-h-screen p-8 max-w-3xl mx-auto flex flex-col gap-8">
      <h1 className="text-3xl font-bold text-indigo-400">
        Assessment: {skillId.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}
      </h1>

      {!result ? (
        <>
          <div className="flex flex-col gap-6">
            {quiz?.questions?.map((q: any, qi: number) => (
              <div key={qi} className="bg-gray-900 rounded-2xl p-6">
                <p className="font-medium text-white mb-4">{qi + 1}. {q.question}</p>
                <div className="flex flex-col gap-2">
                  {q.options.map((opt: string, oi: number) => (
                    <button key={oi}
                      onClick={() => setSelected(s => { const n = [...s]; n[qi] = oi; return n; })}
                      className={`text-left px-4 py-3 rounded-xl border transition ${
                        selected[qi] === oi
                          ? "border-indigo-500 bg-indigo-900/40 text-white"
                          : "border-gray-700 bg-gray-800 text-gray-300 hover:border-gray-500"
                      }`}
                    >{opt}</button>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={submit}
            disabled={selected.some(s => s === -1) || submitting}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-xl font-semibold text-white transition"
          >{submitting ? "Submitting…" : "Submit Answers"}</button>
        </>
      ) : (
        <div className="bg-gray-900 rounded-2xl p-8 flex flex-col gap-6">
          <div className="text-center">
            <p className="text-5xl font-bold text-white mb-2">{Math.round(result.score * 100)}%</p>
            <p className={`text-lg font-semibold ${ACTION_STYLE[result.action]}`}>
              {ACTION_MSG[result.action]}
            </p>
          </div>

          <div className="flex justify-between text-sm text-gray-400 bg-gray-800 rounded-xl p-4">
            <span>Previous mastery: <strong className="text-white">{Math.round(result.old_mastery * 100)}%</strong></span>
            <span>New mastery: <strong className="text-white">{Math.round(result.new_mastery * 100)}%</strong></span>
          </div>

          <div className="flex flex-col gap-3">
            {result.questions?.map((q: any, qi: number) => (
              <div key={qi} className="bg-gray-800 rounded-xl p-4">
                <p className="text-sm text-white mb-1">{q.question}</p>
                <p className="text-xs text-gray-400">{q.explanation}</p>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <a href={`/roadmap/${userId}`}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold text-white transition">
              Back to Roadmap
            </a>
            <a href={`/progress/${userId}`}
              className="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-xl font-semibold text-white transition">
              Progress Dashboard
            </a>
          </div>
        </div>
      )}
    </main>
  );
}
