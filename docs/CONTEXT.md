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
**Phase 3 — Career Matching / Gap Analyst** (NEXT)

## Completed
- [x] Phase 0: Monorepo folders, requirements.txt, .env.example, FastAPI + /health, SQLite + all 11 tables
- [x] Phase 1: data/skills.json (90), data/skill_edges.json (88 edges), data/roles.json (4 roles),
               graph/loader.py (build_graph, prerequisites, learning_path, role_skills), test_graph.py
- [x] Phase 2: Profiler Agent (embedding-based skill extraction), POST/GET /profile,
               GET /profile/{id}/skill-analysis, Next.js frontend — onboarding form,
               dashboard with radar chart + skill list + mastery bars

## Remaining Phases
3: Career Matching — gap analyst agent, match %
4: Resource RAG — 150+ resources, ChromaDB ingestion, curator agent
5: Planner + Roadmap UI
6: Assessor + Evaluator + Progress dashboard
7: Orchestrator + Adaptive Replanning
8: Critic Debate + Mentor chat
9: Career Pivot Diff
10: Polish + demo seed data

## Known Bugs
None.

## Key Decisions
- Mastery thresholds: <0.4 → remedial node, >0.8 → complete
- BKT params: prior=0.3, learn=0.15, slip=0.1, guess=0.2
- RAG guardrail: reject any URL not in ChromaDB store
- Agent debate max 2 rounds (Planner ⇄ Critic)
- Topological sort (not Dijkstra) for path ordering — correct for DAG, simpler

## File Map
```
backend/app/main.py          — FastAPI entry + CORS
backend/app/db.py            — SQLite engine + session
backend/app/api/health.py    — GET /health
backend/app/models/tables.py — 11 SQLModel tables
backend/app/graph/loader.py  — NetworkX graph + path functions ✅
backend/tests/test_graph.py  — Phase 1 tests ✅
data/skills.json             — 90 skill nodes ✅
data/skill_edges.json        — 88 prerequisite edges ✅
data/roles.json              — 4 roles ✅
docs/PRD.md                  — Full PRD
docs/CONTEXT.md              — This file
docs/HISTORY.md              — Append-only build log
```
