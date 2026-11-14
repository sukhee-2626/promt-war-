"""
Planner Agent.
Builds an ordered roadmap from gap list respecting prerequisites and weekly hours.
Input:  PlannerInput
Output: PlannerOutput
"""
from __future__ import annotations
import math
from pydantic import BaseModel
from app.graph.loader import learning_path, GRAPH


class PlannerInput(BaseModel):
    user_id: int
    role_id: str
    gaps: list[dict]           # list of SkillGap dicts (from GapAnalystOutput)
    known_skill_ids: list[str]
    weekly_hours: float = 10.0


class RoadmapNode(BaseModel):
    order: int
    skill_id: str
    skill_name: str
    est_hours: float
    week_start: int
    week_end: int
    milestone: str
    status: str = "pending"


class PlannerOutput(BaseModel):
    user_id: int
    role_id: str
    nodes: list[RoadmapNode]
    total_weeks: int
    reason: str


# Hours per skill level heuristic
_HOURS: dict[str, float] = {
    "beginner": 8, "intermediate": 15, "advanced": 25,
}

def _skill_level(skill_id: str, current_mastery: float) -> str:
    if current_mastery < 0.2: return "beginner"
    if current_mastery < 0.5: return "intermediate"
    return "advanced"


def run_planner(inp: PlannerInput) -> PlannerOutput:
    # 1. Get ordered path respecting prerequisites
    gap_ids = [g["skill_id"] for g in inp.gaps]
    ordered = learning_path(known_ids=inp.known_skill_ids, target_ids=gap_ids)

    # Build mastery lookup
    mastery_map = {g["skill_id"]: g["current_mastery"] for g in inp.gaps}

    # 2. Assign hours + week windows
    nodes: list[RoadmapNode] = []
    cumulative_hours = 0.0
    for i, sid in enumerate(ordered):
        cur = mastery_map.get(sid, 0.0)
        level = _skill_level(sid, cur)
        est = _HOURS[level] * (1.0 - cur)   # less time if partially known
        est = max(2.0, round(est, 1))

        week_start = math.ceil(cumulative_hours / inp.weekly_hours) + 1
        cumulative_hours += est
        week_end = math.ceil(cumulative_hours / inp.weekly_hours)

        # Milestone grouping: every 4 skills = new milestone
        milestone_num = (i // 4) + 1
        milestone = f"Milestone {milestone_num}"

        # Get skill name from GRAPH node data
        node_data = GRAPH.nodes.get(sid, {})
        skill_name = node_data.get("name", sid)

        nodes.append(RoadmapNode(
            order=i + 1,
            skill_id=sid,
            skill_name=skill_name,
            est_hours=est,
            week_start=week_start,
            week_end=week_end,
            milestone=milestone,
            status="pending",
        ))

    total_weeks = math.ceil(cumulative_hours / inp.weekly_hours) if inp.weekly_hours else 0

    return PlannerOutput(
        user_id=inp.user_id,
        role_id=inp.role_id,
        nodes=nodes,
        total_weeks=total_weeks,
        reason="initial_plan",
    )
