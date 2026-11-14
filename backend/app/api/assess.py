from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from app.db import get_session
from app.models.tables import User, UserSkill, Assessment
from app.agents.assessor import AssessorInput, run_assessor
from app.agents.evaluator import EvaluatorInput, run_evaluator
import json
from pathlib import Path

router = APIRouter(prefix="/assess", tags=["assess"])
DATA = Path(__file__).parent.parent.parent.parent / "data"


@router.get("/{user_id}/{skill_id}")
def get_quiz(user_id: int, skill_id: str, session: Session = Depends(get_session)):
    """Generate quiz questions for a skill."""
    skill_meta = {s["id"]: s for s in json.loads((DATA / "skills.json").read_text())}
    skill = skill_meta.get(skill_id)
    if not skill:
        raise HTTPException(404, f"Skill {skill_id} not found")

    # Determine learner's current level
    us = session.exec(
        select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
    ).first()
    mastery = us.mastery if us else 0.3
    level = "beginner" if mastery < 0.4 else ("intermediate" if mastery < 0.7 else "advanced")

    result = run_assessor(AssessorInput(
        skill_id=skill_id,
        skill_name=skill["name"],
        level=level,
    ))
    return result


class SubmitAnswers(BaseModel):
    answers: list[int]   # selected option indices


@router.post("/{user_id}/{skill_id}")
def submit_quiz(user_id: int, skill_id: str, body: SubmitAnswers,
                session: Session = Depends(get_session)):
    """Submit answers, run BKT, update mastery, return evaluation."""
    # Re-generate same quiz to check answers (deterministic via same seed)
    # ponytail: cache quiz in DB; for now regenerate
    skill_meta = {s["id"]: s for s in json.loads((DATA / "skills.json").read_text())}
    skill = skill_meta.get(skill_id, {})

    us = session.exec(
        select(UserSkill).where(UserSkill.user_id == user_id, UserSkill.skill_id == skill_id)
    ).first()
    mastery = us.mastery if us else 0.3

    quiz = run_assessor(AssessorInput(
        skill_id=skill_id,
        skill_name=skill.get("name", skill_id),
        level="beginner" if mastery < 0.4 else "intermediate",
    ))

    # Evaluate answers
    correct_flags = [
        body.answers[i] == quiz.questions[i].correct_index
        for i in range(min(len(body.answers), len(quiz.questions)))
    ]

    eval_out = run_evaluator(EvaluatorInput(
        user_id=user_id,
        skill_id=skill_id,
        current_mastery=mastery,
        answers=correct_flags,
    ))

    # Persist assessment
    assessment = Assessment(user_id=user_id, skill_id=skill_id, score=eval_out.score)
    session.add(assessment)

    # Update UserSkill mastery
    if us:
        us.mastery = eval_out.new_mastery
        session.add(us)
    else:
        session.add(UserSkill(
            user_id=user_id, skill_id=skill_id,
            mastery=eval_out.new_mastery, source="assessment",
        ))
    session.commit()

    return {**eval_out.model_dump(), "questions": quiz.questions}
