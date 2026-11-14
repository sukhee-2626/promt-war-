# SkillForge — CONTEXT (always current, under 1 page)

## Project
SkillForge: AI-powered personalized learning platform.
Each learner = Skill Digital Twin on a Knowledge Graph.
Mastery = Bayesian probability (not checkbox).
Agents debate roadmap. RAG fetches only real resources.

## Stack (LOCKED — do not change)
| Layer       | Choice                                                        |
|-------------|---------------------------------------------------------------|
| Backend     | FastAPI + SQLModel + SQLite                                   |
| Graph       | NetworkX DiGraph (singleton, build once)                      |
| Vector DB   | ChromaDB + bge-small-en-v1.5 embeddings                       |
| Agents      | LangGraph orchestrator                                        |
| LLM         | Ollama llama3.1:8b (env flag: LLM_PROVIDER=groq → Groq API)  |
| Frontend    | Next.js + Tailwind + shadcn/ui + Recharts + React Flow        |
| Resume      | pdfplumber + LLM extraction                                   |

## Repo
https://github.com/sukhee-2626/promt-war-.git
Branch: main | User: sukhee-2626 | Email: sukheesakthivel07@gmail.com

## Current Phase
**Phase 7 — Orchestrator + Adaptive Replanning** (NEXT)

## Completed
- [x] Phase 0: Monorepo, FastAPI, /health, all 11 DB tables
- [x] Phase 1: skills.json (90), skill_edges.json (88), roles.json (4), graph/loader.py, test_graph.py
- [x] Phase 2: Profiler Agent, /profile API, onboarding + dashboard (radar chart, skill twin)
- [x] Phase 3: Gap Analyst Agent, /match API, Career Match page (% ring + ranked gap list)
- [x] Phase 4: resources.json (120), rag/ingest.py, Resource Curator Agent (RAG + guardrail)
- [x] Phase 5: Planner Agent, /roadmap API (prerequisite-ordered, week estimates), Roadmap UI
- [x] Phase 6: Assessor Agent (LLM MCQ), Evaluator Agent (BKT), /assess API, Quiz + Progress UI

## In Progress
- Nothing — ready for Phase 7

## Up Next: Phase 7
- POST /events endpoint
- LangGraph orchestrator state machine
- assessment_failed → Evaluator → Gap Analyst → Planner (insert remedial) → Curator
- goal_changed → Gap Analyst → Planner → Curator
- Save all agent I/O to agent_logs table
- Test: fail JS quiz → roadmap v2 with remedial JS node

## Remaining
8: Critic Debate (Planner ⇄ Critic max 2 rounds) + Mentor chat
9: Career Pivot Diff
10: Polish + demo seed data

## Known Bugs
None.

## Key Decisions
- BKT params in .env.example (prior=0.3, learn=0.15, slip=0.1, guess=0.2)
- Mastery thresholds: <0.4 → remedial, >0.8 → complete
- RAG guardrail: returns [] + warning if skill not in ChromaDB store
- Topological sort for path order (not Dijkstra)
- Agent debate max 2 rounds (Phase 8)

## File Map
```
backend/app/main.py              — FastAPI + all routers registered
backend/app/db.py                — SQLite engine + session
backend/app/api/health.py        — GET /health ✅
backend/app/api/profile.py       — POST/GET /profile, GET /profile/{id}/skill-analysis ✅
backend/app/api/match.py         — GET /match/{user_id} ✅
backend/app/api/roadmap.py       — GET /roadmap/{user_id} ✅
backend/app/api/assess.py        — GET/POST /assess/{user_id}/{skill_id} ✅
backend/app/models/tables.py     — 11 SQLModel tables ✅
backend/app/graph/loader.py      — NetworkX DiGraph ✅
backend/app/rag/ingest.py        — ChromaDB ingestion script ✅
backend/app/agents/profiler.py   — Profiler Agent ✅
backend/app/agents/gap_analyst.py— Gap Analyst Agent ✅
backend/app/agents/planner.py    — Planner Agent ✅
backend/app/agents/resource_curator.py — Curator Agent (RAG) ✅
backend/app/agents/assessor.py   — Assessor Agent (LLM MCQ) ✅
backend/app/agents/evaluator.py  — Evaluator Agent (BKT) ✅
backend/tests/test_graph.py      — Phase 1 tests ✅
data/skills.json                 — 90 skill nodes ✅
data/skill_edges.json            — 88 prerequisite edges ✅
data/roles.json                  — 4 roles ✅
data/resources.json              — 120 real resources ✅
frontend/src/app/page.tsx        — Landing ✅
frontend/src/app/onboarding/     — Onboarding form ✅
frontend/src/app/dashboard/      — Skill twin + radar ✅
frontend/src/app/match/          — Career match % + gaps ✅
frontend/src/app/roadmap/        — Timeline roadmap ✅
frontend/src/app/assess/         — Quiz page ✅
frontend/src/app/progress/       — Progress dashboard ✅
```
