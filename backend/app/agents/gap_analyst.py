"""
Gap Analyst Agent.
Deterministic gap scoring; LLM writes only the explanation string.
Input:  GapAnalystInput
Output: GapAnalystOutput
"""
from __future__ import annotations
import json
from pathlib import Path
from pydantic import BaseModel

DATA = Path(__file__).parent.parent.parent.parent / "data"


class GapAnalystInput(BaseModel):
    user_id: int
    role_id: str
    user_skills: dict[str, float]   # skill_id → mastery


class SkillGap(BaseModel):
    skill_id: str
    skill_name: str
    current_mastery: float
    required_mastery: float
    gap: float
    weight: float
    impact_score: float    # weight * gap * dependents_count
    priority: int          # 1 = highest


class GapAnalystOutput(BaseModel):
    role_id: str
    role_name: str
    match_percent: float
    gaps: list[SkillGap]           # sorted by priority
    strengths: list[str]           # skill_ids already meeting required mastery
    explanation: str


def run_gap_analyst(inp: GapAnalystInput) -> GapAnalystOutput:
    from app.graph.loader import GRAPH

    roles = json.loads((DATA / "roles.json").read_text())
    skills_meta = {s["id"]: s for s in json.loads((DATA / "skills.json").read_text())}

    role = next((r for r in roles if r["id"] == inp.role_id), None)
    if not role:
        raise ValueError(f"Role not found: {inp.role_id}")

    role_skills = role["skills"]
    total_weight = sum(rs["weight"] for rs in role_skills)

    gaps: list[SkillGap] = []
    strengths: list[str] = []
    earned_weight = 0.0

    for rs in role_skills:
        sid = rs["skill_id"]
        req  = rs["required_mastery"]
        wt   = rs["weight"]
        cur  = inp.user_skills.get(sid, 0.0)

        if cur >= req:
            strengths.append(sid)
            earned_weight += wt
        else:
            gap = req - cur
            # count how many role skills depend on this skill (graph successors intersect role)
            role_skill_ids = {r["skill_id"] for r in role_skills}
            dependents = len([
                n for n in GRAPH.successors(sid)
                if n in role_skill_ids
            ]) if sid in GRAPH else 0

            impact = wt * gap * (1 + dependents * 0.5)
            gaps.append(SkillGap(
                skill_id=sid,
                skill_name=skills_meta.get(sid, {}).get("name", sid),
                current_mastery=round(cur, 3),
                required_mastery=req,
                gap=round(gap, 3),
                weight=wt,
                impact_score=round(impact, 3),
                priority=0,  # set after sort
            ))
            # partial credit for partial mastery
            if cur > 0:
                earned_weight += wt * (cur / req)

    # sort by impact descending, assign priority rank
    gaps.sort(key=lambda g: g.impact_score, reverse=True)
    for i, g in enumerate(gaps):
        g.priority = i + 1

    match_pct = round((earned_weight / total_weight) * 100, 1) if total_weight else 0.0

    # Simple explanation (no LLM call — saves latency; ponytail: add LLM narration in Phase 8)
    top_gaps = ", ".join(g.skill_name for g in gaps[:3])
    explanation = (
        f"You match {match_pct}% of {role['name']} requirements. "
        f"Top gaps: {top_gaps}. "
        f"You have {len(strengths)} skills already meeting the bar."
    )

    return GapAnalystOutput(
        role_id=inp.role_id,
        role_name=role["name"],
        match_percent=match_pct,
        gaps=gaps,
        strengths=strengths,
        explanation=explanation,
    )
