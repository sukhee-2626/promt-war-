"""
Aptitude Agent.
Generates aptitude test questions.
"""
from __future__ import annotations
import json, os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Question(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str

class AptitudeInput(BaseModel):
    category: str
    n_questions: int = 5

class AptitudeOutput(BaseModel):
    questions: list[Question]

def _call_llm(prompt: str) -> str:
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

_PROMPT = """Generate {n} aptitude test questions in the category: "{cat}".

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correct_index": 0,
      "explanation": "..."
    }}
  ]
}}"""

def run_aptitude_agent(inp: AptitudeInput) -> AptitudeOutput:
    prompt = _PROMPT.format(n=inp.n_questions, cat=inp.category)
    try:
        raw = _call_llm(prompt).strip()
        start, end = raw.find("{"), raw.rfind("}") + 1
        if start != -1 and end != -1: raw = raw[start:end]
        data = json.loads(raw)
        questions = [Question(**q) for q in data["questions"]]
    except Exception:
        questions = [Question(question="What is 1+1?", options=["1", "2", "3", "4"], correct_index=1, explanation="Basic arithmetic.")]
    return AptitudeOutput(questions=questions)
