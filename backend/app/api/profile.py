from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from app.db import get_session
from app.models.tables import User, UserSkill
from app.agents.profiler import ProfilerInput, run_profiler

router = APIRouter(prefix="/profile", tags=["profile"])


class ProfileCreate(BaseModel):
    name: str
    email: str
    goal_role: str
    weekly_hours: float = 10.0
    free_text: str = ""
    resume_text: str = ""
    github_descriptions: list[str] = []


class ProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    goal_role: str
    weekly_hours: float
    skills: list[dict]


@router.post("", response_model=ProfileResponse)
def create_profile(data: ProfileCreate, session: Session = Depends(get_session)):
    user = User(
        name=data.name,
        email=data.email,
        goal_role=data.goal_role,
        weekly_hours=data.weekly_hours,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Run profiler agent
    profiler_out = run_profiler(ProfilerInput(
        free_text=data.free_text,
        resume_text=data.resume_text,
        github_descriptions=data.github_descriptions,
    ))

    skills_saved = []
    for match in profiler_out.skills:
        us = UserSkill(
            user_id=user.id,
            skill_id=match.skill_id,
            mastery=match.mastery,
            confidence=match.confidence,
            source=match.source,
        )
        session.add(us)
        skills_saved.append(match.model_dump())
    session.commit()

    return ProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        goal_role=user.goal_role,
        weekly_hours=user.weekly_hours,
        skills=skills_saved,
    )


@router.get("/{user_id}", response_model=ProfileResponse)
def get_profile(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    skills = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    return ProfileResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        goal_role=user.goal_role,
        weekly_hours=user.weekly_hours,
        skills=[{"skill_id": s.skill_id, "mastery": s.mastery,
                 "confidence": s.confidence, "source": s.source} for s in skills],
    )


@router.get("/{user_id}/skill-analysis")
def skill_analysis(user_id: int, session: Session = Depends(get_session)):
    """Returns radar chart data + graph node colors for the frontend."""
    import json
    from pathlib import Path
    from app.graph.loader import GRAPH

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    skills_data = json.loads((Path(__file__).parent.parent.parent.parent / "data/skills.json").read_text())
    skill_meta = {s["id"]: s for s in skills_data}

    user_skills = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    mastery_map = {us.skill_id: us.mastery for us in user_skills}

    # Node colors: green≥0.8, yellow≥0.4, red<0.4(known), grey=not started
    nodes = []
    for sid in GRAPH.nodes():
        mastery = mastery_map.get(sid, 0.0)
        if sid not in mastery_map:
            color = "grey"
        elif mastery >= 0.8:
            color = "green"
        elif mastery >= 0.4:
            color = "yellow"
        else:
            color = "red"
        nodes.append({
            "id": sid,
            "name": skill_meta.get(sid, {}).get("name", sid),
            "category": skill_meta.get(sid, {}).get("category", ""),
            "mastery": mastery,
            "color": color,
        })

    # Radar chart: group by category, avg mastery
    from collections import defaultdict
    category_scores: dict = defaultdict(list)
    for us in user_skills:
        cat = skill_meta.get(us.skill_id, {}).get("category", "other")
        category_scores[cat].append(us.mastery)

    radar = [
        {"category": cat, "mastery": round(sum(v)/len(v), 2)}
        for cat, v in category_scores.items()
    ]

    return {"nodes": nodes, "radar": radar, "user": {"id": user.id, "goal_role": user.goal_role}}
