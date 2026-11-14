const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function req<T>(path: string, opts?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

export const api = {
  health: () => req('/health'),

  createProfile: (d: {
    name: string; email: string; goal_role: string;
    weekly_hours: number; free_text: string;
    resume_text?: string; github_descriptions?: string[]
  }) => req('/profile', { method: 'POST', body: JSON.stringify(d) }),

  getProfile:   (id: number) => req(`/profile/${id}`),
  skillAnalysis:(id: number) => req(`/profile/${id}/skill-analysis`),
  match:        (id: number, role?: string) => req(`/match/${id}${role ? `?role=${role}` : ''}`),
  roadmap:      (id: number, role?: string) => req(`/roadmap/${id}${role ? `?role=${role}` : ''}`),
  getQuiz:      (uid: number, skill: string) => req(`/assess/${uid}/${skill}`),
  submitQuiz:   (uid: number, skill: string, answers: number[]) =>
    req(`/assess/${uid}/${skill}`, { method: 'POST', body: JSON.stringify({ answers }) }),
  postEvent:    (uid: number, event_type: string, payload?: object) =>
    req(`/events/${uid}`, { method: 'POST', body: JSON.stringify({ event_type, payload: payload ?? {} }) }),
  agentLogs:    (uid: number) => req(`/events/${uid}/logs`),
  mentorChat:   (uid: number, message: string) =>
    req(`/mentor/${uid}`, { method: 'POST', body: JSON.stringify({ message }) }),
  debate:       (uid: number, roadmapId: number) => req(`/mentor/${uid}/debate/${roadmapId}`),
  pivot:        (uid: number, new_role: string) =>
    req(`/pivot/${uid}`, { method: 'POST', body: JSON.stringify({ new_role }) }),

  createBoard: (d: { user_id: number; title: string }) =>
    req('/tracker/boards', { method: 'POST', body: JSON.stringify(d) }),
  getBoards:   (user_id: number) => req(`/tracker/boards/${user_id}`),
  createTask:  (d: { board_id: number; title: string; status: string }) =>
    req('/tracker/tasks', { method: 'POST', body: JSON.stringify(d) }),
  getTasks:    (board_id: number) => req(`/tracker/boards/${board_id}/tasks`),
  updateTask:  (task_id: number, status: string) =>
    req(`/tracker/tasks/${task_id}`, { method: 'PATCH', body: JSON.stringify({ status }) }),
}

export const ROLES = [
  { id: 'full_stack_developer',  label: 'Full Stack Developer' },
  { id: 'data_analyst',          label: 'Data Analyst' },
  { id: 'ml_engineer',           label: 'ML Engineer' },
  { id: 'backend_developer',     label: 'Backend Developer' },
]

export const fmtRole = (r: string) =>
  r.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
