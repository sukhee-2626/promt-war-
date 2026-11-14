from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from app.db import get_session
from app.models.tables import User, UserSkill
from app.agents.gap_analyst import GapAnalystInput, run_gap_analyst
from app.agents.planner import PlannerInput, run_planner
import json
from pathlib import Path

router = APIRouter(prefix="/pivot", tags=["pivot"])
DATA = Path(__file__).parent.parent.parent.parent / "data"


class PivotRequest(BaseModel):
    new_role: str


@router.post("/{user_id}")
def career_pivot(user_id: int, body: PivotRequest, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    old_role = user.goal_role
    new_role = body.new_role

    user_skills = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    mastery_map = {us.skill_id: us.mastery for us in user_skills}
    known_ids   = list(mastery_map.keys())

    roles = json.loads((DATA / "roles.json").read_text())
    role_meta  = {r["id"]: {s["skill_id"]: s for s in r["skills"]} for r in roles}

    old_req = role_meta.get(old_role, {})
    new_req = role_meta.get(new_role, {})

    if not new_req:
        raise HTTPException(400, f"Role not found: {new_role}")

    # Classify each skill in the new role
    transferable: list[dict] = []
    partial: list[dict] = []
    new_needed: list[dict] = []
    no_longer_needed: list[dict] = []

    for sid, req in new_req.items():
        cur = mastery_map.get(sid, 0.0)
        if cur >= req["required_mastery"]:
            transferable.append({"skill_id": sid, "mastery": cur, "required": req["required_mastery"]})
        elif cur > 0:
            partial.append({"skill_id": sid, "mastery": cur, "required": req["required_mastery"],
                            "gap": round(req["required_mastery"] - cur, 2)})
        else:
            new_needed.append({"skill_id": sid, "required": req["required_mastery"]})

    # Skills in old role not in new role
    for sid in old_req:
        if sid not in new_req:
            no_longer_needed.append({"skill_id": sid})

    # Hours saved vs starting from scratch
    old_gap_out = run_gap_analyst(GapAnalystInput(user_id=user_id, role_id=old_role, user_skills={}))
    new_gap_out = run_gap_analyst(GapAnalystInput(user_id=user_id, role_id=new_role, user_skills=mastery_map))

    old_plan = run_planner(PlannerInput(
        user_id=user_id, role_id=new_role,
        gaps=[g.model_dump() for g in old_gap_out.gaps],
        known_skill_ids=[], weekly_hours=user.weekly_hours,
    ))
    new_plan = run_planner(PlannerInput(
        user_id=user_id, role_id=new_role,
        gaps=[g.model_dump() for g in new_gap_out.gaps],
        known_skill_ids=known_ids, weekly_hours=user.weekly_hours,
    ))

    hours_saved = sum(n.est_hours for n in old_plan.nodes) - sum(n.est_hours for n in new_plan.nodes)
    transfer_pct = round(len(transferable) / len(new_req) * 100, 1) if new_req else 0

    return {
        "old_role": old_role,
        "new_role": new_role,
        "transfer_percent": transfer_pct,
        "transferable": transferable,
        "partial": partial,
        "new_needed": new_needed,
        "no_longer_needed": no_longer_needed,
        "hours_saved": round(max(0, hours_saved), 1),
        "new_match_percent": new_gap_out.match_percent,
        "new_roadmap_weeks": new_plan.total_weeks,
        "new_plan_nodes": [n.model_dump() for n in new_plan.nodes],
    }
