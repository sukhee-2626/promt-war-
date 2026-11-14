from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/aptitude", tags=["aptitude"])

# ponytail: move to DB or JSON file.
QUESTIONS = [
    {"id": 1, "text": "2+2?", "options": ["3", "4", "5"], "correct_index": 1},
    {"id": 2, "text": "Capital of France?", "options": ["London", "Paris", "Berlin"], "correct_index": 1}
]

class Question(BaseModel):
    id: int
    text: str
    options: List[str]

class Submission(BaseModel):
    answers: List[int]

@router.get("/", response_model=List[Question])
def get_questions():
    """Fetch aptitude questions."""
    return [{"id": q["id"], "text": q["text"], "options": q["options"]} for q in QUESTIONS]

@router.post("/submit")
def submit_answers(submission: Submission):
    """Submit answers and return score."""
    score = 0
    for i, ans in enumerate(submission.answers):
        if i < len(QUESTIONS) and ans == QUESTIONS[i]["correct_index"]:
            score += 1
    return {"score": score, "total": len(QUESTIONS)}
