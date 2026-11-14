from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, profile
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

@app.on_event("startup")
def on_startup():
    create_db()
