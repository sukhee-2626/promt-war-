# SkillForge — CONTEXT (always current)

## Project
SkillForge: High-end AI-powered Career Copilot (Syllabus tracking, Virtual Interviews, ATS Resume optimization, RAG resources).

## Stack (LOCKED)
| Layer | Choice |
|---|---|
| Backend | FastAPI + SQLModel + SQLite |
| Deployment | Vercel (Serverless Functions) |
| Vector DB | ChromaDB + bge-small-en-v1.5 |
| Agents | LangGraph + Custom (Interview, Resume, Aptitude, Outreach) |
| Frontend | React + Vite + Tailwind + Recharts |

## Status: Enhanced Deployment Ready ✅

## Completed Enhancements
- [x] Vercel serverless integration (`vercel.json`, `backend/api/index.py`)
- [x] Interview Agent (competence-aware evaluation)
- [x] Resume Agent (deep ATS analysis, keyword mapping)
- [x] Syllabus Tracking (Tracker API + Progress UI)
- [x] Guided Tour (intro.js integration)
- [x] Enhanced UI: Skeletons, professional navigation, interactive components
- [x] Practice Engine (HackerRank-like syllabus tracking)

## Run Instructions
```bash
# Build
npm run build # (in frontend/)

# Deploy
vercel --prod
```
