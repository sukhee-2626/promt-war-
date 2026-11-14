# SkillForge — CONTEXT (always current, under 1 page)

## Project
SkillForge: AI-powered personalized learning platform.
Each learner = Skill Digital Twin on a Knowledge Graph.
Mastery = Bayesian probability (not checkbox).
Agents debate roadmap. RAG fetches only real resources.

## Stack
| Layer       | Choice                                         |
|-------------|------------------------------------------------|
| Backend     | FastAPI + SQLModel + SQLite                    |
| Graph       | NetworkX (in-memory DiGraph)                   |
| Vector DB   | ChromaDB + bge-small-en-v1.5 embeddings        |
| Agents      | LangGraph orchestrator                         |
| LLM         | Ollama llama3.1:8b (fallback: Groq via env)    |
| Frontend    | Next.js + Tailwind + shadcn/ui + Recharts + React Flow |
| Resume parse| pdfplumber + LLM extraction                   |

## Repo
https://github.com/sukhee-2626/promt-war-.git
Branch: main | User: sukhee-2626 | Email: sukheesakthivel07@gmail.com

## Current Phase
Phase 1 — Skill Graph & Roles Seed Data (IN PROGRESS)

## Done
- [x] Monorepo folders: backend/, frontend/, data/, docs/
- [x] requirements.txt, .env.example
- [x] FastAPI app + CORS + GET /health
- [x] SQLite DB setup (db.py)
- [x] All DB table models (tables.py)
- [x] data/skills.json (90 skills: web, data, ML, AI, devops, security)
- [x] docs/HISTORY.md, docs/CONTEXT.md created

## In Progress
- [ ] data/skill_edges.json (prerequisite pairs)
- [ ] data/roles.json (4 roles with required skills)
- [ ] backend/app/graph/loader.py (NetworkX loader + path functions)
- [ ] backend/tests/test_graph.py

## Pending Phases
- Phase 2: Profile + Skill Analysis (F1, F2) — radar chart, profiler agent
- Phase 3: Career Matching (F3) — gap analyst agent, match %
- Phase 4: Resource RAG (F4) — 150+ resources, ChromaDB ingestion
- Phase 5: Planner + Roadmap UI
- Phase 6: Assessor + Evaluator + Progress dashboard
- Phase 7: Orchestrator + Adaptive Replanning
- Phase 8: Critic Debate + Mentor chat
- Phase 9: Career Pivot Diff
- Phase 10: Polish + demo seed data

## Known Bugs
None yet.

## Key Decisions
- Mastery thresholds: <0.4 → remedial node, >0.8 → complete
- BKT params: prior=0.3, learn=0.15, slip=0.1, guess=0.2
- RAG guardrail: reject any URL not in ChromaDB store
- Agent debate max 2 rounds
- LLM_PROVIDER env flag switches ollama ↔ groq

## File Map
```
backend/
  app/
    main.py          — FastAPI entry, CORS, router registration
    db.py            — SQLite engine + session
    api/             — Route handlers (health.py, profile.py, ...)
    models/
      tables.py      — All SQLModel table definitions
    agents/          — One file per agent (profiler, gap_analyst, planner, ...)
    graph/
      loader.py      — NetworkX DiGraph + path functions
    rag/             — ChromaDB ingestion + retrieval
  requirements.txt
  .env.example
frontend/
  src/
    app/             — Next.js pages
    components/      — Shared UI components
    lib/             — API client, utils
data/
  skills.json        — 90 skill nodes
  skill_edges.json   — prerequisite edges
  roles.json         — role → required skills map
  resources.json     — 150+ real learning resources
docs/
  PRD.md             — Full product requirements
  CONTEXT.md         — This file (always current)
  HISTORY.md         — Append-only build log
```
