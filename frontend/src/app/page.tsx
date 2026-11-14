import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-5xl font-bold text-indigo-400">⚡ SkillForge</h1>
      <p className="text-gray-400 text-lg text-center max-w-xl">
        Your personal Skill Digital Twin. Find gaps, build a roadmap, track mastery.
      </p>
      <Link href="/onboarding"
        className="px-8 py-3 bg-indigo-600 hover:bg-indigo-500 rounded-xl font-semibold text-white transition">
        Get Started →
      </Link>
    </main>
  );
}
