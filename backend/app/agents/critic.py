"""
Critic Agent.
Reviews Planner output for: prerequisite violations, unrealistic hours,
ignoring recent failures, low resource variety.
Returns issues as JSON. Planner revises (max 2 rounds).
"""
from __future__ import annotations
from pydantic import BaseModel
from app.graph.loader import GRAPH


class CriticInput(BaseModel):
    plan_nodes: list[dict]
    weekly_hours: float
    recent_failures: list[str]   # skill_ids failed recently
    round: int = 1


class CriticIssue(BaseModel):
    type: str          # "prereq_violation" | "unrealistic_hours" | "ignores_failure" | "low_variety"
    description: str
    affected_skill: str = ""
    suggested_fix: str = ""


class CriticOutput(BaseModel):
    issues: list[CriticIssue]
    approved: bool      # True if no blocking issues
    summary: str
    round: int


def run_critic(inp: CriticInput) -> CriticOutput:
    issues: list[CriticIssue] = []
    nodes = inp.plan_nodes

    # 1. Prerequisite violation check
    seen: set[str] = set()
    for node in nodes:
        sid = node["skill_id"]
        for prereq in GRAPH.predecessors(sid):
            if prereq not in seen and GRAPH.has_node(prereq):
                # Check if prereq appears later in the plan
                later = [n["skill_id"] for n in nodes[nodes.index(node)+1:]]
                if prereq in later:
                    issues.append(CriticIssue(
                        type="prereq_violation",
                        description=f"{prereq} is a prerequisite of {sid} but appears after it.",
                        affected_skill=sid,
                        suggested_fix=f"Move {sid} after {prereq}.",
                    ))
        seen.add(sid)

    # 2. Unrealistic weekly hours (>40h/week is a red flag)
    total_hours = sum(n.get("est_hours", 0) for n in nodes)
    if nodes:
        last_week = max(n.get("week_end", 1) for n in nodes)
        if last_week > 0:
            avg_weekly = total_hours / last_week
            if avg_weekly > 40:
                issues.append(CriticIssue(
                    type="unrealistic_hours",
                    description=f"Plan requires ~{avg_weekly:.0f}h/week. Learner budget is {inp.weekly_hours}h/week.",
                    affected_skill="",
                    suggested_fix="Increase plan duration by adding more weeks.",
                ))

    # 3. Recent failure ignored (failed skill not at top of plan)
    for fail_sid in inp.recent_failures:
        plan_sids = [n["skill_id"] for n in nodes]
        if fail_sid in plan_sids:
            idx = plan_sids.index(fail_sid)
            if idx > 2:  # not in top 3
                issues.append(CriticIssue(
                    type="ignores_failure",
                    description=f"{fail_sid} was recently failed but appears at position {idx+1} instead of top.",
                    affected_skill=fail_sid,
                    suggested_fix=f"Prioritize {fail_sid} to start.",
                ))

    # 4. Plan too long without milestones (>10 skills per milestone)
    if len(nodes) > 10:
        milestone_counts: dict[str, int] = {}
        for n in nodes:
            ms = n.get("milestone", "M1")
            milestone_counts[ms] = milestone_counts.get(ms, 0) + 1
        for ms, count in milestone_counts.items():
            if count > 10:
                issues.append(CriticIssue(
                    type="low_variety",
                    description=f"{ms} has {count} skills — consider splitting into sub-milestones.",
                    affected_skill="",
                    suggested_fix="Split into smaller milestones.",
                ))

    blocking = [i for i in issues if i.type in ("prereq_violation", "unrealistic_hours")]
    approved = len(blocking) == 0

    summary = (
        "✅ Plan looks good — approved." if approved
        else f"⚠️ {len(issues)} issue(s) found: " + "; ".join(i.description[:60] for i in issues[:2])
    )

    return CriticOutput(issues=issues, approved=approved, summary=summary, round=inp.round)
