from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.tables import User, UserSkill
from app.agents.gap_analyst import GapAnalystInput, run_gap_analyst

router = APIRouter(prefix="/match", tags=["match"])


@router.get("/{user_id}")
def career_match(user_id: int, role: str = "", session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    role_id = role or user.goal_role
    user_skills_rows = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    mastery_map = {us.skill_id: us.mastery for us in user_skills_rows}

    result = run_gap_analyst(GapAnalystInput(
        user_id=user_id,
        role_id=role_id,
        user_skills=mastery_map,
    ))
    return result
