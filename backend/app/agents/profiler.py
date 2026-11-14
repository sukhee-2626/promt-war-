"""
Profiler Agent — extracts skills from free text / resume / GitHub descriptions,
maps them to graph skill_ids via embedding similarity, assigns initial mastery.
Input:  ProfilerInput
Output: ProfilerOutput (list of SkillMatch)
"""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

DATA = Path(__file__).parent.parent.parent.parent / "data"
SIMILARITY_THRESHOLD = 0.60   # ponytail: tune per model; bge-small is generous


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ProfilerInput(BaseModel):
    free_text: str = ""          # anything the user typed about themselves
    resume_text: str = ""        # extracted PDF text
    github_descriptions: list[str] = []


class SkillMatch(BaseModel):
    skill_id: str
    skill_name: str
    mastery: float               # initial estimate 0–1
    confidence: float            # embedding similarity score
    source: str                  # "resume" | "github" | "text" | "inferred"


class ProfilerOutput(BaseModel):
    skills: list[SkillMatch]
    raw_mentions: list[str]      # surface skill names before mapping


# ── Embedding helper (lazy-loaded) ────────────────────────────────────────────

_model = None
_skill_embeddings: Optional[dict] = None   # skill_id → embedding


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5"))
    return _model


def _get_skill_embeddings() -> dict:
    """Embed all skill names once, cache in memory."""
    global _skill_embeddings
    if _skill_embeddings is not None:
        return _skill_embeddings
    skills = json.loads((DATA / "skills.json").read_text())
    model = _get_model()
    names = [s["name"] for s in skills]
    ids   = [s["id"]   for s in skills]
    embeddings = model.encode(names, normalize_embeddings=True)
    _skill_embeddings = {sid: emb for sid, emb in zip(ids, embeddings)}
    return _skill_embeddings


# ── Keyword → initial mastery heuristic ──────────────────────────────────────

_MASTERY_HINTS = {
    "expert": 0.85, "advanced": 0.75, "proficient": 0.70,
    "experienced": 0.65, "intermediate": 0.55, "familiar": 0.45,
    "basic": 0.35, "beginner": 0.30, "learning": 0.25,
}

def _initial_mastery(context_text: str, skill_name: str) -> float:
    """Rough mastery from surrounding context words."""
    lower = context_text.lower()
    for kw, score in _MASTERY_HINTS.items():
        if kw in lower:
            return score
    return 0.40   # default: basic familiarity assumed


# ── Core extraction ───────────────────────────────────────────────────────────

def _extract_mentions(text: str) -> list[str]:
    """
    LLM-free: split on commas/newlines/bullets, return candidate phrases.
    ponytail: replace with LLM NER when time allows for better precision.
    """
    import re
    text = re.sub(r"[•\-\*]", ",", text)
    tokens = re.split(r"[,\n;]+", text)
    return [t.strip() for t in tokens if 3 < len(t.strip()) < 60]


def _match_to_graph(mentions: list[str], source: str, context: str) -> list[SkillMatch]:
    """Embed mentions, cosine-sim against skill embeddings, threshold filter."""
    if not mentions:
        return []
    model = _get_model()
    skill_embs = _get_skill_embeddings()
    skills_json = json.loads((DATA / "skills.json").read_text())
    skill_meta  = {s["id"]: s for s in skills_json}

    mention_embs = model.encode(mentions, normalize_embeddings=True)

    matched: dict[str, SkillMatch] = {}   # skill_id → best match
    import numpy as np
    skill_ids  = list(skill_embs.keys())
    skill_mat  = np.array([skill_embs[sid] for sid in skill_ids])

    for mention, m_emb in zip(mentions, mention_embs):
        sims = skill_mat @ m_emb          # cosine similarity (normalized)
        best_idx = int(sims.argmax())
        best_sim = float(sims[best_idx])
        if best_sim < SIMILARITY_THRESHOLD:
            continue
        sid = skill_ids[best_idx]
        if sid in matched and matched[sid].confidence >= best_sim:
            continue
        matched[sid] = SkillMatch(
            skill_id   = sid,
            skill_name = skill_meta[sid]["name"],
            mastery    = _initial_mastery(context, mention),
            confidence = round(best_sim, 3),
            source     = source,
        )
    return list(matched.values())


# ── Public API ────────────────────────────────────────────────────────────────

def run_profiler(inp: ProfilerInput) -> ProfilerOutput:
    all_mentions: list[str] = []
    all_matches:  dict[str, SkillMatch] = {}   # deduplicate by skill_id

    sources = [
        (inp.free_text,  "text"),
        (inp.resume_text, "resume"),
    ]
    for desc in inp.github_descriptions:
        sources.append((desc, "github"))

    for text, source in sources:
        if not text.strip():
            continue
        mentions = _extract_mentions(text)
        all_mentions.extend(mentions)
        for m in _match_to_graph(mentions, source, text):
            # keep highest-confidence match per skill
            if m.skill_id not in all_matches or \
               all_matches[m.skill_id].confidence < m.confidence:
                all_matches[m.skill_id] = m

    return ProfilerOutput(
        skills=list(all_matches.values()),
        raw_mentions=list(set(all_mentions)),
    )
