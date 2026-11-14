# SkillForge — CONTEXT (always current)

## Project
SkillForge: AI-powered personalized learning platform.
Each learner = Skill Digital Twin on a Knowledge Graph.
Mastery = Bayesian probability (not checkbox).
Agents debate roadmap. RAG fetches only real resources.

## Stack (LOCKED)
| Layer | Choice |
|---|---|
| Backend | FastAPI + SQLModel + SQLite |
| Graph | NetworkX DiGraph (singleton) |
| Vector DB | ChromaDB + bge-small-en-v1.5 |
| Agents | LangGraph orchestrator |
| LLM | Ollama llama3.1:8b (env: LLM_PROVIDER=groq → Groq) |
| Frontend | Next.js 14 + Tailwind + Recharts |

## Repo
https://github.com/sukhee-2626/promt-war-.git
Branch: main | User: sukhee-2626 | Email: sukheesakthivel07@gmail.com

## Status: ALL 10 PHASES COMPLETE ✅

## Phases Completed
- [x] Phase 0: Monorepo, FastAPI, /health, all 11 DB tables
- [x] Phase 1: skills.json (90), skill_edges.json (88), roles.json (4), graph/loader.py, test_graph.py
- [x] Phase 2: Profiler Agent, /profile API, onboarding + dashboard (radar chart, skill twin)
- [x] Phase 3: Gap Analyst Agent, /match API, Career Match page (% ring + ranked gap list)
- [x] Phase 4: resources.json (120), rag/ingest.py, Resource Curator Agent (RAG + guardrail)
- [x] Phase 5: Planner Agent, /roadmap API (prerequisite-ordered, week estimates), Roadmap UI
- [x] Phase 6: Assessor Agent (LLM MCQ), Evaluator Agent (BKT), /assess API, Quiz + Progress UI
- [x] Phase 7: Orchestrator (LangGraph), /events API, adaptive replanning (assessment_failed, goal_changed)
- [x] Phase 8: Critic Agent (prereq/hours/failure checks), Mentor Agent (grounded chat), Debate UI + Chat widget
- [x] Phase 9: Pivot Diff (/pivot API + UI: transfer/partial/new 3-column + hours saved)
- [x] Phase 10: seed_demo.py, README.md with full docs

## Run Instructions
```bash
# Backend
cd backend && cp .env.example .env
pip install -r requirements.txt
python -m app.rag.ingest      # one-time ChromaDB setup
uvicorn app.main:app --reload

# Frontend
cd frontend && npm install && npm run dev

# Seed demo
python backend/seed_demo.py
```

## All API Endpoints
GET  /health
POST /profile  |  GET /profile/{id}  |  GET /profile/{id}/skill-analysis
GET  /match/{id}?role=
GET  /roadmap/{id}
GET  /assess/{id}/{skill}  |  POST /assess/{id}/{skill}
POST /events/{id}  |  GET /events/{id}/logs
POST /mentor/{id}  |  GET /mentor/{id}/debate/{roadmap_id}
POST /pivot/{id}

## All Frontend Pages
/  →  /onboarding  →  /dashboard/[userId]  →  /match/[userId]
→  /roadmap/[userId]  →  /assess/[userId]/[skillId]  →  /progress/[userId]
→  /agent-activity/[userId]/[roadmapId]  →  /pivot/[userId]

## Key Files
```
backend/app/agents/     — 9 agents: profiler, gap_analyst, planner, critic,
                          resource_curator, assessor, evaluator, mentor, orchestrator
backend/app/api/        — 8 routers: health, profile, match, roadmap, assess, events, mentor, pivot
backend/app/graph/      — NetworkX loader + path functions
backend/app/rag/        — ChromaDB ingestion
data/                   — skills.json, skill_edges.json, roles.json, resources.json
docs/                   — PRD.md, CONTEXT.md (this), HISTORY.md
README.md               — Full setup + demo guide
backend/seed_demo.py    — Demo data seeder
```
