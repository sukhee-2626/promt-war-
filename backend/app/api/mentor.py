from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from app.db import get_session
from app.models.tables import User, UserSkill, Roadmap, RoadmapNode, AgentLog
from app.agents.mentor import MentorInput, run_mentor
from app.agents.critic import CriticInput, run_critic
from app.agents.planner import PlannerInput, run_planner
from app.agents.gap_analyst import GapAnalystInput, run_gap_analyst
import json

router = APIRouter(prefix="/mentor", tags=["mentor"])


class ChatMessage(BaseModel):
    message: str


@router.post("/{user_id}")
def chat(user_id: int, body: ChatMessage, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    user_skills = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    twin_skills = {us.skill_id: us.mastery for us in user_skills}

    # Get active roadmap nodes
    active_roadmap = session.exec(
        select(Roadmap).where(Roadmap.user_id == user_id, Roadmap.status == "active")
    ).first()
    roadmap_nodes = []
    if active_roadmap:
        rn = session.exec(
            select(RoadmapNode).where(RoadmapNode.roadmap_id == active_roadmap.id)
        ).all()
        roadmap_nodes = [{"skill_id": n.skill_id, "skill_name": n.skill_id.replace("_"," ").title(),
                          "status": n.status, "order": n.order} for n in rn]

    result = run_mentor(MentorInput(
        user_id=user_id,
        message=body.message,
        twin_skills=twin_skills,
        roadmap_nodes=roadmap_nodes,
        goal_role=user.goal_role,
    ))

    # Log
    session.add(AgentLog(
        user_id=user_id, agent="mentor",
        input=body.message, output=result.reply,
    ))
    session.commit()

    return result


@router.get("/{user_id}/debate/{roadmap_id}")
def get_debate(user_id: int, roadmap_id: int, session: Session = Depends(get_session)):
    """Run Planner ⇄ Critic debate and return transcript."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")

    user_skills = session.exec(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    mastery_map = {us.skill_id: us.mastery for us in user_skills}
    known_ids   = [us.skill_id for us in user_skills]

    gap_out = run_gap_analyst(GapAnalystInput(
        user_id=user_id, role_id=user.goal_role, user_skills=mastery_map
    ))

    # Recent failures (mastery < 0.4 from assessments)
    recent_failures = [g.skill_id for g in gap_out.gaps if g.current_mastery < 0.4][:3]

    transcript = []
    plan_nodes = None
    plan_out   = None

    for round_num in range(1, 3):   # max 2 rounds
        # Planner
        pl_in  = PlannerInput(
            user_id=user_id, role_id=user.goal_role,
            gaps=[g.model_dump() for g in gap_out.gaps],
            known_skill_ids=known_ids, weekly_hours=user.weekly_hours,
        )
        plan_out = run_planner(pl_in)
        plan_nodes = [n.model_dump() for n in plan_out.nodes]

        transcript.append({
            "speaker": "Planner",
            "round": round_num,
            "content": f"Proposed {len(plan_nodes)} nodes over {plan_out.total_weeks} weeks.",
            "nodes": plan_nodes[:5],
        })

        # Critic
        cr_in  = CriticInput(
            plan_nodes=plan_nodes,
            weekly_hours=user.weekly_hours,
            recent_failures=recent_failures,
            round=round_num,
        )
        cr_out = run_critic(cr_in)

        transcript.append({
            "speaker": "Critic",
            "round": round_num,
            "content": cr_out.summary,
            "issues": [i.model_dump() for i in cr_out.issues],
            "approved": cr_out.approved,
        })

        # Save to agent_logs
        session.add(AgentLog(user_id=user_id, agent="planner",
                             input=pl_in.model_dump_json(), output=json.dumps(plan_nodes[:3])))
        session.add(AgentLog(user_id=user_id, agent="critic",
                             input=cr_in.model_dump_json(), output=cr_out.model_dump_json()))

        if cr_out.approved:
            break

    session.commit()
    return {"transcript": transcript, "final_nodes": plan_nodes, "total_weeks": plan_out.total_weeks if plan_out else 0}
