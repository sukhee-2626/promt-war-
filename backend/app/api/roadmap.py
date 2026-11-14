from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.tables import User, UserSkill, Roadmap, RoadmapNode
from app.agents.gap_analyst import GapAnalystInput, run_gap_analyst
from app.agents.planner import PlannerInput, run_planner

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.get("/{user_id}")
def get_roadmap(user_id: int, role: str = "", session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    role_id = role or user.goal_role
    user_skills = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    mastery_map = {us.skill_id: us.mastery for us in user_skills}
    known_ids   = [us.skill_id for us in user_skills]

    # Gap analysis first
    gap_out = run_gap_analyst(GapAnalystInput(
        user_id=user_id, role_id=role_id, user_skills=mastery_map
    ))

    # Build plan
    plan = run_planner(PlannerInput(
        user_id=user_id,
        role_id=role_id,
        gaps=[g.model_dump() for g in gap_out.gaps],
        known_skill_ids=known_ids,
        weekly_hours=user.weekly_hours,
    ))

    # Persist roadmap (new version each call)
    existing = session.exec(
        select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.status == "active")
    ).all()
    version = len(existing) + 1
    # Deactivate old
    for r in existing:
        r.status = "archived"
        session.add(r)

    roadmap = Roadmap(user_id=user_id, version=version, status="active", reason=plan.reason)
    session.add(roadmap)
    session.commit()
    session.refresh(roadmap)

    for node in plan.nodes:
        rn = RoadmapNode(
            roadmap_id=roadmap.id,
            skill_id=node.skill_id,
            order=node.order,
            status=node.status,
            est_hours=node.est_hours,
        )
        session.add(rn)
    session.commit()

    return {
        "roadmap_id": roadmap.id,
        "version": version,
        "total_weeks": plan.total_weeks,
        "role": role_id,
        "nodes": [n.model_dump() for n in plan.nodes],
        "match_percent": gap_out.match_percent,
    }
