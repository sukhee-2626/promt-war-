const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = {
  async createProfile(data: {
    name: string; email: string; goal_role: string;
    weekly_hours: number; free_text: string;
    resume_text: string; github_descriptions: string[];
  }) {
    const r = await fetch(`${API}/profile`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },

  async getProfile(userId: number) {
    const r = await fetch(`${API}/profile/${userId}`);
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },

  async skillAnalysis(userId: number) {
    const r = await fetch(`${API}/profile/${userId}/skill-analysis`);
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },
};
