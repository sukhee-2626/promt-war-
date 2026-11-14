"""
Evaluator Agent — Bayesian Knowledge Tracing.
Updates mastery after each quiz answer.
Params: prior=0.3, learn=0.15, slip=0.1, guess=0.2 (all configurable via env)
"""
from __future__ import annotations
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

P_PRIOR = float(os.getenv("BKT_PRIOR", "0.3"))
P_LEARN = float(os.getenv("BKT_LEARN", "0.15"))
P_SLIP  = float(os.getenv("BKT_SLIP",  "0.1"))
P_GUESS = float(os.getenv("BKT_GUESS", "0.2"))

MASTERY_COMPLETE  = 0.8
MASTERY_REMEDIAL  = 0.4


class EvaluatorInput(BaseModel):
    user_id: int
    skill_id: str
    current_mastery: float
    answers: list[bool]       # True = correct, False = wrong


class EvaluatorOutput(BaseModel):
    user_id: int
    skill_id: str
    old_mastery: float
    new_mastery: float
    score: float              # fraction correct
    action: str               # "complete" | "remedial" | "continue"
    bkt_trace: list[float]    # mastery after each answer


def bkt_update(p: float, correct: bool,
               slip=P_SLIP, guess=P_GUESS, learn=P_LEARN) -> float:
    """One BKT step."""
    if correct:
        p_obs = p * (1 - slip) + (1 - p) * guess
        p_new = (p * (1 - slip)) / p_obs if p_obs > 0 else p
    else:
        p_obs = p * slip + (1 - p) * (1 - guess)
        p_new = (p * slip) / p_obs if p_obs > 0 else p
    # Apply learning
    p_new = p_new + (1 - p_new) * learn
    return min(1.0, max(0.0, p_new))


def run_evaluator(inp: EvaluatorInput) -> EvaluatorOutput:
    p = inp.current_mastery if inp.current_mastery > 0 else P_PRIOR
    trace = []
    for correct in inp.answers:
        p = bkt_update(p, correct)
        trace.append(round(p, 3))

    score = sum(inp.answers) / len(inp.answers) if inp.answers else 0.0
    new_p = round(p, 3)

    if new_p >= MASTERY_COMPLETE:
        action = "complete"
    elif new_p < MASTERY_REMEDIAL:
        action = "remedial"
    else:
        action = "continue"

    return EvaluatorOutput(
        user_id=inp.user_id,
        skill_id=inp.skill_id,
        old_mastery=inp.current_mastery,
        new_mastery=new_p,
        score=round(score, 2),
        action=action,
        bkt_trace=trace,
    )
