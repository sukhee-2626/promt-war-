from pydantic import BaseModel
from typing import List, Dict

class InterviewInput(BaseModel):
    user_id: int
    question_id: str
    transcript_chunk: str
    competencies: List[str] = []

class InterviewOutput(BaseModel):
    user_id: int
    score: float # 0.0 - 1.0
    feedback: str
    competencies: Dict[str, float]

def run_interview_evaluation(inp: InterviewInput) -> InterviewOutput:
    # Simulation: simplistic keyword/length heuristic.
    # ponytail: Need a real LLM evaluation here. Upgrade path: Replace with LLM agent call.
    score = min(1.0, max(0.0, len(inp.transcript_chunk) / 500))
    feedback = "Good response." if score > 0.5 else "Need more detail."
    
    comp_map = {c: score for c in inp.competencies} if inp.competencies else {"clarity": score, "relevance": 0.5}
    
    return InterviewOutput(
        user_id=inp.user_id,
        score=round(score, 2),
        feedback=feedback,
        competencies=comp_map
    )
