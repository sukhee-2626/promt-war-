from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, profile, match, roadmap, assess, events, mentor, pivot
from app.db import create_db

app = FastAPI(title="SkillForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(profile.router)
app.include_router(match.router)
app.include_router(roadmap.router)
app.include_router(assess.router)
app.include_router(events.router)
app.include_router(mentor.router)
app.include_router(pivot.router)

@app.on_event("startup")
def on_startup():
    create_db()
