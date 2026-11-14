from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from app.db import get_session
from app.models.tables import User, UserSkill, Roadmap, RoadmapNode, Event, AgentLog
from app.agents.orchestrator import run_orchestrator
import json

router = APIRouter(prefix="/events", tags=["events"])


class EventRequest(BaseModel):
    event_type: str    # assessment_failed | assessment_passed | goal_changed | profile_updated | stalled_7_days | interview | outreach
    # ponytail: Events documented, not strictly validated; add Literal[...] for strictness.
    payload: dict = {}


@router.post("/{user_id}")
def post_event(user_id: int, body: EventRequest, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    # Build mastery map
    user_skills = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    mastery_map = {us.skill_id: us.mastery for us in user_skills}

    # Store event
    ev = Event(user_id=user_id, type=body.event_type, payload=json.dumps(body.payload))
    session.add(ev)
    session.commit()

    # Run orchestrator
    result = run_orchestrator(
        user_id=user_id,
        event_type=body.event_type,
        payload=body.payload,
        mastery_map=mastery_map,
        role_id=body.payload.get("role_id", user.goal_role),
        weekly_hours=user.weekly_hours,
    )

    # Update goal role if changed
    if body.event_type == "goal_changed" and "role_id" in body.payload:
        user.goal_role = body.payload["role_id"]
        session.add(user)

    # Update mastery in DB from orchestrator result
    for sid, new_mastery in result["mastery_map"].items():
        us = session.exec(
            select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == sid)
        ).first()
        if us:
            us.mastery = new_mastery
            session.add(us)
        else:
            session.add(UserSkill(user_id=user_id, skill_id=sid, mastery=new_mastery, source="orchestrator"))

    # Persist new roadmap version
    existing = session.exec(
        select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.status == "active")
    ).all()
    version = len(existing) + 1
    for r in existing:
        r.status = "archived"
        session.add(r)

    roadmap = Roadmap(
        user_id=user_id, version=version, status="active",
        reason=body.event_type,
    )
    session.add(roadmap)
    session.commit()
    session.refresh(roadmap)

    for node in result["plan_nodes"]:
        rn = RoadmapNode(
            roadmap_id=roadmap.id,
            skill_id=node["skill_id"],
            order=node["order"],
            status=node["status"],
            est_hours=node["est_hours"],
        )
        session.add(rn)

    # Save agent logs
    for log in result["agent_logs"]:
        session.add(AgentLog(
            user_id=user_id,
            agent=log["agent"],
            input=log["input"],
            output=log["output"],
        ))

    session.commit()

    return {
        "event_type": body.event_type,
        "roadmap_version": version,
        "roadmap_id": roadmap.id,
        "nodes_count": len(result["plan_nodes"]),
        "mentor_message": result["mentor_message"],
        "remedial_skill": result.get("remedial_skill", ""),
    }


@router.get("/{user_id}/logs")
def get_agent_logs(user_id: int, session: Session = Depends(get_session)):
    logs = session.exec(
        select(AgentLog).where(AgentLog.user_id == user_id)
    ).all()
    return [{"agent": l.agent, "input": l.input, "output": l.output,
             "created_at": l.created_at.isoformat()} for l in logs]
