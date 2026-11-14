"""
Resource Curator Agent.
Retrieves resources from ChromaDB with metadata filter, reranks, returns top 3 + mini-project.
Input:  CuratorInput
Output: CuratorOutput
Guardrail: only URLs from the vector store are returned — no hallucination.
"""
from __future__ import annotations
import json, os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

DATA   = Path(__file__).parent.parent.parent.parent / "data"
CHROMA = os.getenv("CHROMA_PATH", "./chroma_db")
EMBED  = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")

# Mini-project templates per skill category
_PROJECTS: dict[str, str] = {
    "web":          "Build a responsive personal portfolio page using only HTML/CSS.",
    "frontend":     "Build a Todo app with CRUD operations and local storage persistence.",
    "backend":      "Build a REST API with authentication (JWT), CRUD endpoints, and a database.",
    "data":         "Analyze a public dataset (e.g. Titanic) — clean, query, visualize 3 insights.",
    "data_science": "Create a Jupyter notebook analyzing a Kaggle dataset with 5 visualizations.",
    "ml":           "Train a classifier on a public dataset, evaluate with cross-validation, report metrics.",
    "ai":           "Build a simple RAG chatbot over a text document using ChromaDB and an LLM.",
    "devops":       "Containerize a simple web app with Docker and write a docker-compose file.",
    "security":     "Audit a sample web app for OWASP Top 5 vulnerabilities and document findings.",
    "engineering":  "Implement 3 classic data structures (stack, queue, linked list) with unit tests.",
    "programming":  "Build a CLI tool that solves a real problem you face — file renamer, expense tracker, etc.",
    "cloud":        "Deploy a containerized app to AWS/GCP free tier with a CI/CD pipeline.",
}


class CuratorInput(BaseModel):
    skill_id: str
    level: str = "beginner"          # beginner | intermediate | advanced
    max_duration_min: int = 120      # learner time budget per resource
    n_results: int = 3


class Resource(BaseModel):
    id: str
    title: str
    url: str
    type: str
    duration_min: int
    provider: str
    free: bool
    relevance_score: float


class CuratorOutput(BaseModel):
    skill_id: str
    resources: list[Resource]
    mini_project: str
    warning: str = ""


# ── ChromaDB client (lazy) ────────────────────────────────────────────────────

_chroma_col = None

def _get_collection():
    global _chroma_col
    if _chroma_col is None:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA)
        _chroma_col = client.get_or_create_collection("resources")
    return _chroma_col


_embed_model = None

def _embed(text: str) -> list[float]:
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer(EMBED)
    return _embed_model.encode(text, normalize_embeddings=True).tolist()


# ── Core retrieval ────────────────────────────────────────────────────────────

def run_curator(inp: CuratorInput) -> CuratorOutput:
    col = _get_collection()

    # Level fallback: if no advanced resources exist, try intermediate → beginner
    levels_to_try = {
        "advanced":     ["advanced", "intermediate", "beginner"],
        "intermediate": ["intermediate", "beginner"],
        "beginner":     ["beginner"],
    }.get(inp.level, ["beginner"])

    results = None
    used_level = inp.level
    for lvl in levels_to_try:
        try:
            r = col.query(
                query_embeddings=[_embed(f"learn {inp.skill_id} {lvl}")],
                n_results=min(20, col.count()),
                where={"skill_id": {"$eq": inp.skill_id}},
                include=["metadatas", "distances", "documents"],
            )
            if r["ids"][0]:
                results = r
                used_level = lvl
                break
        except Exception:
            continue

    if not results or not results["ids"][0]:
        # Skill not in store — return warning, no hallucinated URLs
        skill_meta = {s["id"]: s for s in json.loads((DATA / "skills.json").read_text())}
        cat = skill_meta.get(inp.skill_id, {}).get("category", "engineering")
        return CuratorOutput(
            skill_id=inp.skill_id,
            resources=[],
            mini_project=_PROJECTS.get(cat, _PROJECTS["engineering"]),
            warning=f"No resources found for skill '{inp.skill_id}' in the store.",
        )

    ids       = results["ids"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    # Filter by duration budget, then pick top N by relevance (1 - distance)
    candidates = []
    for rid, meta, dist in zip(ids, metas, distances):
        if int(meta.get("duration_min", 0)) <= inp.max_duration_min:
            candidates.append((rid, meta, 1.0 - dist))
    # Fallback: if budget filters everything, ignore budget
    if not candidates:
        candidates = [(rid, meta, 1.0 - dist) for rid, meta, dist in zip(ids, metas, distances)]

    # Rerank: prefer variety of types (video, article, exercise, course)
    seen_types: set[str] = set()
    picked: list[Resource] = []
    # First pass: enforce type diversity
    for rid, meta, score in sorted(candidates, key=lambda x: -x[2]):
        if len(picked) >= inp.n_results:
            break
        t = meta.get("type", "")
        if t not in seen_types or len(picked) < inp.n_results:
            seen_types.add(t)
            picked.append(Resource(
                id=rid,
                title=meta["title"],
                url=meta["url"],
                type=t,
                duration_min=int(meta.get("duration_min", 0)),
                provider=meta.get("provider", ""),
                free=meta.get("free", "True") == "True",
                relevance_score=round(score, 3),
            ))

    # Mini-project from category template
    skill_meta = {s["id"]: s for s in json.loads((DATA / "skills.json").read_text())}
    cat = skill_meta.get(inp.skill_id, {}).get("category", "engineering")
    project = _PROJECTS.get(cat, _PROJECTS["engineering"])

    return CuratorOutput(
        skill_id=inp.skill_id,
        resources=picked,
        mini_project=project,
        warning="" if used_level == inp.level else f"No {inp.level} resources; showing {used_level}.",
    )
