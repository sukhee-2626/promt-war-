# SkillForge Build History

## Session 1 — Project Kickoff & Phase 0+1 Start
Date: 2025-07-15
Tool: DeepSeek Harness / Claude Sonnet

---

### GitHub Setup
- Repo: https://github.com/sukhee-2626/promt-war-.git
- User: sukhee-2626
- Email: sukheesakthivel07@gmail.com
- Push method: fine-grained PAT in remote URL (token in env only, not committed)
- Branch: main

---

### Phase 0 — Monorepo Setup
Status: IN PROGRESS

Files created:
- backend/requirements.txt       — all Python deps (fastapi, sqlmodel, langraph, chromadb, etc.)
- backend/.env.example           — env vars template (LLM_PROVIDER, DB_PATH, CHROMA_PATH, etc.)
- backend/app/main.py            — FastAPI app with CORS + /health router
- backend/app/api/health.py      — GET /health → {status: ok}
- backend/app/db.py              — SQLite engine, create_db(), get_session()
- backend/app/models/tables.py   — All DB tables: User, UserSkill, Skill, SkillEdge, Role,
                                   RoleSkill, Roadmap, RoadmapNode, Assessment, Event, AgentLog

Folders created:
- backend/app/{agents,api,models,graph,rag}
- frontend/src/{app,components,lib}
- data/
- docs/

Done when: GET /health returns 200 + Next.js dev server runs

---

### Phase 1 — Skill Graph & Roles Seed Data
Status: IN PROGRESS

Files created:
- data/skills.json               — 90 skills across web, data, ML, AI, devops, security categories

Files pending:
- data/skill_edges.json          — prerequisite pairs
- data/roles.json                — Full Stack, Data Analyst, ML Engineer, Backend Dev
- backend/app/graph/loader.py    — NetworkX DiGraph builder + prerequisites() + path()
- backend/tests/test_graph.py    — test: JS before React, React before Next.js

---

### Key Decisions
- Stack locked: FastAPI + SQLite + ChromaDB + LangGraph + Ollama + Next.js
- LLM fallback: Groq via LLM_PROVIDER env flag
- Mastery model: Bayesian Knowledge Tracing (prior=0.3, learn=0.15, slip=0.1, guess=0.2)
- Mastery < 0.4 → insert remedial node
- Mastery > 0.8 → skill complete
- RAG guardrail: only return URLs present in ChromaDB vector store (no hallucinated links)
- Agent debate: Planner → Critic (max 2 rounds) → revised plan saved
- Events that trigger replanning: assessment_failed, assessment_passed, goal_changed,
  profile_updated, weekly_time_changed, stalled_7_days

---

### Agents Planned
| Agent           | Responsibility                                      |
|-----------------|-----------------------------------------------------|
| Profiler        | Extract skills from resume/GitHub/form              |
| Gap Analyst     | Compare twin vs role, rank gaps                     |
| Planner         | Build roadmap via graph shortest path               |
| Critic          | Challenge plan, force revision                      |
| Resource Curator| RAG fetch: metadata filter + vector search + rerank |
| Assessor        | Generate quiz/coding tasks, grade                   |
| Evaluator       | Bayesian KT mastery update                          |
| Mentor          | Chat grounded in twin data                          |
| Orchestrator    | LangGraph state machine routing events              |

---

### Data Model Summary
Tables: users, user_skills, skills, skill_edges, roles, role_skills,
        roadmaps, roadmap_nodes, assessments, events, agent_logs

---

## [TO BE APPENDED AFTER EACH PHASE]

## Phase 1 Completion — [date TBD]
## Phase 2 Completion — [date TBD]
## Phase 3 Completion — [date TBD]
## Phase 4 Completion — [date TBD]
## Phase 5 Completion — [date TBD]
## Phase 6 Completion — [date TBD]
## Phase 7 Completion — [date TBD]
## Phase 8 Completion — [date TBD]
## Phase 9 Completion — [date TBD]
## Phase 10 Completion — [date TBD]
