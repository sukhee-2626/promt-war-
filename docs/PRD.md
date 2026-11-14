# SkillForge PRD

Copied from session. Full source of truth.

See: https://github.com/sukhee-2626/promt-war-/blob/main/docs/PRD.md

---

## 1. The Different Idea
SkillForge treats every learner as a living Skill Digital Twin on a Skill Knowledge Graph.
Every learning step = verified mini-project, not a course link.

4 differentiators:
1. Skill Graph (not list) — prerequisites as edges, roadmap = shortest path
2. Mastery as probability (0–1) via Bayesian Knowledge Tracing, not checkbox
3. Agent Debate — Planner proposes, Critic attacks, revised plan shown
4. Career Pivot Diff — transfers/wastes/new skills on goal change

## 2. Problem Statement
Organizations and universities cannot see skill gaps for career goals.
Traditional platforms give everyone the same courses.
SkillForge: personal skill graph → gap analysis → adaptive roadmap → verified tasks → auto-replan.

## 3. Demo Scenario
Student: knows Python, SQL, basic HTML
Target: Full Stack Developer
Gaps: JavaScript, React, Node.js
Event: fails JavaScript assessment → inserts remedial JS node (closures, async)
Pivot: switches to Data Analyst → 70% progress transfers

## 4. Features
F1  User Profile       — details, skills, certs, projects, goal, weekly hours, resume/GitHub upload
F2  Skill Analysis     — radar chart, graph nodes colored by mastery
F3  Career Matching    — match%, gap list, role selector
F4  Learning Recs      — RAG resources + 1 hands-on mini-project per node
F5  Progress Tracking  — mastery trend, streak, assessment history, ETA
F6  AI Mentor          — grounded chat, hints before answers, cites graph data
F7  Adaptive Replan    — triggered by poor assessment or goal change
F8  Agent Debate View  — Planner vs Critic transcript
F9  Career Pivot Diff  — transfer/waste/new comparison
F10 Project Reviewer   — GitHub/code review agent → updates mastery
F11 Admin Cohort View  — heatmap of skill gaps

## 5. Agentic Architecture
Agents: Profiler, Gap Analyst, Planner, Critic, Resource Curator (RAG),
        Assessor, Evaluator, Mentor, Orchestrator (LangGraph)

Events: assessment_failed, assessment_passed, goal_changed,
        profile_updated, weekly_time_changed, stalled_7_days

Flow: Event → Orchestrator → Evaluator → Gap Analyst → Planner ⇄ Critic (max 2 rounds)
      → Curator (RAG) → save roadmap → Mentor explains

## 6. Stack
Backend: FastAPI, SQLModel, SQLite, NetworkX, ChromaDB, bge-small embeddings,
         LangGraph, Ollama (llama3.1:8b), Groq fallback
Frontend: Next.js, Tailwind, shadcn/ui, Recharts, React Flow
Resume: pdfplumber + LLM
Code sandbox: Piston API or Judge0 CE

## 7. Data Model
users, user_skills, certifications, projects,
skills, skill_edges, roles, role_skills,
roadmaps, roadmap_nodes, assessments, events, agent_logs

## 8. Mastery Model (BKT)
Parameters: prior=0.3, learn=0.15, slip=0.1, guess=0.2
Correct:  P = P*(1-slip) / (P*(1-slip) + (1-P)*guess)
Wrong:    P = P*slip / (P*slip + (1-P)*(1-guess))
Learn:    P = P + (1-P)*learn
Thresholds: <0.4 → remedial node | >0.8 → complete

## 9. Build Order (Phases 0–10)
Phase 0:  Monorepo, env, /health
Phase 1:  Skill graph + roles seed data
Phase 2:  F1 Profile + F2 Skill Analysis
Phase 3:  F3 Career Matching
Phase 4:  F4 Resource RAG
Phase 5:  Planner + Roadmap UI
Phase 6:  Assessor + Evaluator + F5 Progress
Phase 7:  Orchestrator + F7 Replanning
Phase 8:  Critic (F8) + Mentor (F6)
Phase 9:  Pivot Diff (F9)
Phase 10: Polish + demo seed data

## 10. Session Starter Prompt (paste into any tool)
You are continuing SkillForge. Read PRD.md, CONTEXT.md, last 3 HISTORY.md entries.
Do not redo finished work. Do not change the stack. Work only on the task I give.
At the end output: (1) files changed, (2) new HISTORY.md entry, (3) updated CONTEXT.md.
