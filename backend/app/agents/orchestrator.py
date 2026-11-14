"""
Orchestrator — LangGraph state machine.
Routes events to the right agents, saves all I/O to agent_logs.
Events: assessment_failed, assessment_passed, goal_changed, profile_updated, stalled_7_days
"""
from __future__ import annotations
import json
from datetime import datetime
from typing import TypedDict, Annotated
from pydantic import BaseModel
from langgraph.graph import StateGraph, END


# ── State shared across nodes ─────────────────────────────────────────────────

class OrchestratorState(TypedDict):
    user_id: int
    event_type: str
    payload: dict
    mastery_map: dict          # skill_id → mastery
    role_id: str
    weekly_hours: float
    gaps: list
    plan_nodes: list
    mentor_message: str
    agent_logs: list           # list of {agent, input, output}
    remedial_skill: str        # filled when action==remedial


# ── Helper: log agent call ────────────────────────────────────────────────────

def _log(state: OrchestratorState, agent: str, inp: dict, out: dict) -> None:
    state["agent_logs"].append({
        "agent": agent,
        "input": json.dumps(inp),
        "output": json.dumps(out),
        "ts": datetime.utcnow().isoformat(),
    })


# ── Node functions ────────────────────────────────────────────────────────────

def node_evaluator(state: OrchestratorState) -> OrchestratorState:
    """Update mastery from assessment result if present in payload."""
    from app.agents.evaluator import EvaluatorInput, run_evaluator
    p = state["payload"]
    if "answers" not in p:
        return state

    skill_id = p["skill_id"]
    current  = state["mastery_map"].get(skill_id, 0.3)
    ev_in    = EvaluatorInput(
        user_id=state["user_id"],
        skill_id=skill_id,
        current_mastery=current,
        answers=p["answers"],
    )
    ev_out = run_evaluator(ev_in)
    _log(state, "evaluator", ev_in.model_dump(), ev_out.model_dump())

    state["mastery_map"][skill_id] = ev_out.new_mastery
    if ev_out.action == "remedial":
        state["remedial_skill"] = skill_id
    return state


def node_gap_analyst(state: OrchestratorState) -> OrchestratorState:
    from app.agents.gap_analyst import GapAnalystInput, run_gap_analyst
    ga_in  = GapAnalystInput(
        user_id=state["user_id"],
        role_id=state["role_id"],
        user_skills=state["mastery_map"],
    )
    ga_out = run_gap_analyst(ga_in)
    _log(state, "gap_analyst", ga_in.model_dump(), ga_out.model_dump())
    state["gaps"] = [g.model_dump() for g in ga_out.gaps]
    return state


def node_planner(state: OrchestratorState) -> OrchestratorState:
    from app.agents.planner import PlannerInput, run_planner
    known = [sid for sid, m in state["mastery_map"].items() if m >= 0.4]

    # Insert remedial node at top of gaps if needed
    gaps = list(state["gaps"])
    remedial = state.get("remedial_skill", "")
    if remedial:
        # Insert a "JS fundamentals" remedial variant if JS failed
        remedial_entry = {
            "skill_id": remedial,
            "skill_name": remedial.replace("_", " ").title() + " (Remedial)",
            "current_mastery": state["mastery_map"].get(remedial, 0.2),
            "required_mastery": 0.6,
            "gap": 0.4,
            "weight": 1.5,
            "impact_score": 999,  # sort to top
            "priority": 0,
        }
        gaps = [remedial_entry] + [g for g in gaps if g["skill_id"] != remedial]

    pl_in  = PlannerInput(
        user_id=state["user_id"],
        role_id=state["role_id"],
        gaps=gaps,
        known_skill_ids=known,
        weekly_hours=state["weekly_hours"],
    )
    pl_out = run_planner(pl_in)
    _log(state, "planner", pl_in.model_dump(), pl_out.model_dump())
    state["plan_nodes"] = [n.model_dump() for n in pl_out.nodes]
    return state


def node_curator(state: OrchestratorState) -> OrchestratorState:
    """Fetch resources for top 3 gap skills."""
    from app.agents.resource_curator import CuratorInput, run_curator
    top_gaps = state["gaps"][:3]
    curated = {}
    for g in top_gaps:
        sid = g["skill_id"]
        mastery = state["mastery_map"].get(sid, 0.0)
        level = "beginner" if mastery < 0.4 else "intermediate"
        cur_in  = CuratorInput(skill_id=sid, level=level)
        cur_out = run_curator(cur_in)
        _log(state, "curator", cur_in.model_dump(), cur_out.model_dump())
        curated[sid] = cur_out.model_dump()
    state["payload"]["curated_resources"] = curated
    return state


def node_mentor_message(state: OrchestratorState) -> OrchestratorState:
    evt = state["event_type"]
    remedial = state.get("remedial_skill", "")
    if evt == "assessment_failed" and remedial:
        state["mentor_message"] = (
            f"You struggled with {remedial.replace('_',' ')}. "
            f"I've added a remedial step at the top of your roadmap. "
            f"Focus on the fundamentals first — you've got this! 💪"
        )
    elif evt == "goal_changed":
        state["mentor_message"] = (
            f"Goal updated! I've rebuilt your roadmap for {state['role_id'].replace('_',' ')}. "
            f"Check which skills transfer — your progress isn't wasted."
        )
    elif evt == "assessment_passed":
        state["mentor_message"] = "Great work! Skill mastered. Moving to the next node. 🎉"
    else:
        state["mentor_message"] = "Your roadmap has been updated based on your latest progress."
    return state


# ── Routing ───────────────────────────────────────────────────────────────────

def route_event(state: OrchestratorState) -> str:
    evt = state["event_type"]
    if evt in ("assessment_failed", "assessment_passed"):
        return "evaluator"
    if evt in ("goal_changed", "profile_updated", "stalled_7_days"):
        return "gap_analyst"
    return "gap_analyst"


# ── Build graph ───────────────────────────────────────────────────────────────

def build_orchestrator() -> any:
    g = StateGraph(OrchestratorState)
    g.add_node("evaluator",      node_evaluator)
    g.add_node("gap_analyst",    node_gap_analyst)
    g.add_node("planner",        node_planner)
    g.add_node("curator",        node_curator)
    g.add_node("mentor_message", node_mentor_message)

    g.set_conditional_entry_point(route_event, {
        "evaluator":  "evaluator",
        "gap_analyst":"gap_analyst",
    })
    g.add_edge("evaluator",   "gap_analyst")
    g.add_edge("gap_analyst", "planner")
    g.add_edge("planner",     "curator")
    g.add_edge("curator",     "mentor_message")
    g.add_edge("mentor_message", END)

    return g.compile()


ORCHESTRATOR = build_orchestrator()


def run_orchestrator(
    user_id: int, event_type: str, payload: dict,
    mastery_map: dict, role_id: str, weekly_hours: float,
) -> OrchestratorState:
    init: OrchestratorState = {
        "user_id": user_id,
        "event_type": event_type,
        "payload": payload,
        "mastery_map": mastery_map,
        "role_id": role_id,
        "weekly_hours": weekly_hours,
        "gaps": [],
        "plan_nodes": [],
        "mentor_message": "",
        "agent_logs": [],
        "remedial_skill": "",
    }
    return ORCHESTRATOR.invoke(init)
