"""
Mentor Agent — grounded conversational guide.
Has tools: get_twin, get_roadmap, explain_recommendation, get_hint.
Rules: hints before answers, cites graph data, refuses to invent resources.
"""
import os, json, chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
DATA = Path(__file__).parent.parent.parent.parent / "data"
CHROMA = os.getenv("CHROMA_PATH", "./chroma_db")
EMBED = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")


class MentorInput(BaseModel):
    user_id: int
    message: str
    twin_skills: dict       # skill_id → mastery
    roadmap_nodes: list     # current roadmap node dicts
    goal_role: str


class MentorOutput(BaseModel):
    reply: str
    cited_skills: list[str]
    cited_resources: list[str]


def _retrieve_resources(weak_skills: list) -> list:
    if not weak_skills: return []
    client = chromadb.PersistentClient(path=CHROMA)
    col = client.get_collection("resources")
    # Query for resources matching any of the weak skills
    res = col.query(
        query_texts=[f"skill:{s}" for s in weak_skills],
        n_results=3,
        where={"skill_id": {"$in": weak_skills}} if weak_skills else None
    )
    return [meta["title"] for meta in res.get("metadatas", [[]])[0]]


def _get_twin_summary(twin_skills: dict) -> tuple:
    mastered = [sid for sid, m in twin_skills.items() if m >= 0.8]
    learning = [sid for sid, m in twin_skills.items() if 0.4 <= m < 0.8]
    weak     = [sid for sid, m in twin_skills.items() if m < 0.4]
    summary = (
        f"Mastered: {', '.join(mastered[:5]) or 'none'}. "
        f"Learning: {', '.join(learning[:5]) or 'none'}. "
        f"Weak: {', '.join(weak[:5]) or 'none'}."
    )
    return summary, weak


def _get_next_steps(roadmap_nodes: list) -> str:
    pending = [n for n in roadmap_nodes if n.get("status") == "pending"][:3]
    return "Next: " + ", ".join(n["skill_name"] for n in pending) if pending else "Roadmap complete!"


def _call_llm(prompt: str) -> str:
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "groq":
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
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
        return resp.json().get("response", "I'm here to help! Could you rephrase that?")


_SYSTEM = """You are SkillForge Mentor, a personalized learning guide.

RULES (never break):
1. Give HINTS before full answers. Ask what they've tried first.
2. ALWAYS cite which skill from the learner's graph you're referencing.
3. NEVER invent course links or resource URLs. Only mention resources that exist in the system.
4. Keep replies under 150 words.
5. Be encouraging but honest.

LEARNER CONTEXT:
{context}

USER MESSAGE: {message}

Reply as the Mentor:"""


def run_mentor(inp: MentorInput) -> MentorOutput:
    twin_summary, weak_skills = _get_twin_summary(inp.twin_skills)
    next_steps    = _get_next_steps(inp.roadmap_nodes)
    resources     = _retrieve_resources(weak_skills)

    context = (
        f"Goal: {inp.goal_role.replace('_',' ')}. "
        f"{twin_summary} "
        f"{next_steps} "
        f"Recommended resources: {', '.join(resources)}"
    )

    prompt = _SYSTEM.format(context=context, message=inp.message)

    # Detect cited skills from message
    all_skills = json.loads((DATA / "skills.json").read_text())
    cited_skills = [
        s["id"] for s in all_skills
        if s["name"].lower() in inp.message.lower() or s["id"] in inp.message.lower()
    ]

    try:
        reply = _call_llm(prompt)
    except Exception as e:
        reply = (
            f"I'm having trouble connecting to the AI right now. "
            f"Based on your profile: {next_steps}. "
            f"Focus on your top gap skill first!"
        )

    return MentorOutput(
        reply=reply.strip(),
        cited_skills=cited_skills[:5],
        cited_resources=resources,   # Populated now.
    )
