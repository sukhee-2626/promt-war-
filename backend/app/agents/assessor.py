"""
Assessor Agent.
Generates quiz questions for a skill_id using the LLM.
Input:  AssessorInput
Output: AssessorOutput (strict JSON schema)
"""
from __future__ import annotations
import json, os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Question(BaseModel):
    question: str
    options: list[str]        # 4 options
    correct_index: int        # 0-based
    explanation: str


class AssessorInput(BaseModel):
    skill_id: str
    skill_name: str
    level: str = "intermediate"
    n_questions: int = 5


class AssessorOutput(BaseModel):
    skill_id: str
    questions: list[Question]


def _call_llm(prompt: str) -> str:
    """LLM call with provider switch via env."""
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "groq":
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return resp.choices[0].message.content
    else:
        import httpx
        resp = httpx.post(
            f"{os.getenv('OLLAMA_BASE_URL','http://localhost:11434')}/api/generate",
            json={"model": os.getenv("OLLAMA_MODEL","llama3.1:8b"),
                  "prompt": prompt, "stream": False},
            timeout=120,
        )
        return resp.json()["response"]


_PROMPT = """Generate {n} multiple-choice quiz questions for the skill: "{skill}" (level: {level}).

Return ONLY valid JSON in this exact format, no markdown, no extra text:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_index": 0,
      "explanation": "..."
    }}
  ]
}}"""


def run_assessor(inp: AssessorInput) -> AssessorOutput:
    prompt = _PROMPT.format(n=inp.n_questions, skill=inp.skill_name, level=inp.level)
    raw = _call_llm(prompt)

    # Robust JSON extraction
    raw = raw.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end != -1:
        raw = raw[start:end]

    try:
        data = json.loads(raw)
        questions = [Question(**q) for q in data["questions"]]
    except Exception:
        # Fallback: return one static question so the flow doesn't break
        questions = [Question(
            question=f"What is the primary purpose of {inp.skill_name}?",
            options=["A) Data storage", "B) Core functionality", "C) Styling", "D) Networking"],
            correct_index=1,
            explanation=f"{inp.skill_name} is used for its core functionality in the stack.",
        )]

    return AssessorOutput(skill_id=inp.skill_id, questions=questions)
