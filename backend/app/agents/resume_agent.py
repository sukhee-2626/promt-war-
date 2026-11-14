"""
Resume Agent.
Deep ATS analysis: keyword mapping, section completeness, formatting checks.
"""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path
from pydantic import BaseModel, Field

DATA = Path(__file__).resolve().parent.parent.parent.parent / "data"

STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "cannot", "could", "couldn", "did", "didn", "do", "does", "doesn", "doing", "don", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn", "has", "hasn", "have", "haven",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in",
    "into", "is", "isn", "it", "its", "itself", "just", "me", "more", "most", "mustn", "my", "myself",
    "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves",
    "out", "over", "own", "same", "she", "should", "shouldn", "so", "some", "such", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "wasn", "we", "were", "weren", "what", "when",
    "where", "which", "while", "who", "whom", "why", "with", "won", "would", "wouldn", "you", "your",
    "yours", "yourself", "yourselves", "will", "need", "needs", "needed", "must", "help", "plus", "ideal",
    "candidate", "looking", "seeking", "role", "team", "across", "well", "using", "uses", "including",
    "etc", "per", "strong", "experience", "experienced", "knowledge", "years", "work", "working", "ability",
    "skill", "skills", "technologies", "proficient", "proficiency"
}

SOFT_SKILLS = {
    "communication": "soft_skill",
    "leadership": "soft_skill",
    "collaboration": "soft_skill",
    "problem solving": "soft_skill",
    "critical thinking": "soft_skill",
    "mentorship": "soft_skill",
    "agile": "soft_skill",
    "scrum": "soft_skill",
    "teamwork": "soft_skill",
    "adaptability": "soft_skill",
    "time management": "soft_skill",
}

ALIASES = {
    "nodejs": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue.js",
    "nextjs": "next.js",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "cicd": "ci/cd",
    "restful api": "rest apis",
    "restful apis": "rest apis",
    "rest api": "rest apis",
}


class KeywordMapping(BaseModel):
    keyword: str
    category: str = "technical"
    in_resume: bool
    resume_count: int = 0
    job_count: int = 1


class FormattingAnalysis(BaseModel):
    word_count: int = 0
    has_bullet_points: bool = False
    has_contact_info: bool = False
    issues: list[str] = []


class ResumeAgentInput(BaseModel):
    resume_text: str
    job_description: str


class ResumeAgentOutput(BaseModel):
    match_score: float
    keyword_score: float = 0.0
    section_score: float = 0.0
    ats_score: float = 0.0
    matched_keywords: list[str] = []
    missing_keywords: list[str] = []
    keyword_mapping: list[KeywordMapping] = []
    section_analysis: dict[str, bool] = {}
    formatting: FormattingAnalysis = Field(default_factory=FormattingAnalysis)
    suggestions: str = ""


def _load_known_skills() -> dict[str, str]:
    skills: dict[str, str] = {}
    skills_file = DATA / "skills.json"
    if skills_file.is_file():
        try:
            for s in json.loads(skills_file.read_text(encoding="utf-8")):
                cat = s.get("category", "technical")
                skills[s["name"].lower()] = cat
                skills[s["id"].replace("_", " ").lower()] = cat
        except Exception:
            pass
    skills.update(SOFT_SKILLS)
    skills["machine learning"] = "ml"
    skills["ci/cd"] = "devops"
    return skills


def run_resume_agent(inp: ResumeAgentInput) -> ResumeAgentOutput:
    # 1. Formatting checks & section parsing
    words = inp.resume_text.split()
    word_count = len(words)
    has_bullets = bool(re.search(r"[\u2022\*\-\–]", inp.resume_text))
    has_contact = bool(
        re.search(r"[\w\.-]+@[\w\.-]+\.\w+", inp.resume_text)
        or re.search(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", inp.resume_text)
    )

    fmt_issues: list[str] = []
    if word_count < 100 and inp.resume_text.strip():
        fmt_issues.append("Resume word count is low (< 100 words). Add project and impact details.")
    if not has_bullets and inp.resume_text.strip():
        fmt_issues.append("No bullet points detected. Use bulleted lists for ATS readability.")
    if not has_contact and inp.resume_text.strip():
        fmt_issues.append("No contact information (email/phone) detected.")

    formatting = FormattingAnalysis(
        word_count=word_count,
        has_bullet_points=has_bullets,
        has_contact_info=has_contact,
        issues=fmt_issues,
    )

    section_patterns = {
        "contact_info": has_contact,
        "experience": bool(re.search(r"(?i)\b(experience|work history|employment)\b", inp.resume_text)),
        "education": bool(re.search(r"(?i)\b(education|degree|university|college|bachelor|master|phd)\b", inp.resume_text)),
        "skills": bool(re.search(r"(?i)\b(skills|technologies|tech stack|competencies)\b", inp.resume_text)),
        "projects": bool(re.search(r"(?i)\b(projects|portfolio)\b", inp.resume_text)),
        "summary": bool(re.search(r"(?i)\b(summary|objective|about me|profile)\b", inp.resume_text)),
    }
    present_sections = sum(1 for v in section_patterns.values() if v)
    section_score = round((present_sections / len(section_patterns)) * 100, 1)

    # 2. Keyword mapping
    # ponytail: add LLM embeddings / NER when taxonomy misses niche terminology
    known_skills = _load_known_skills()

    def normalize(text: str) -> str:
        t = text.lower()
        for alias, canon in ALIASES.items():
            t = re.sub(rf"(?<!\w){re.escape(alias)}(?!\w)", canon, t)
        return t

    norm_jd = normalize(inp.job_description)
    norm_res = normalize(inp.resume_text)

    mapping_dict: dict[str, KeywordMapping] = {}

    # Multi-word skills first (longest first)
    multi_words = [k for k in known_skills if " " in k or "-" in k]
    multi_words.sort(key=len, reverse=True)
    mask_jd = norm_jd
    for phrase in multi_words:
        pat = rf"(?<!\w){re.escape(phrase)}(?!\w)"
        jd_cnt = len(re.findall(pat, mask_jd))
        if jd_cnt > 0:
            res_cnt = len(re.findall(pat, norm_res))
            mapping_dict[phrase] = KeywordMapping(
                keyword=phrase,
                category=known_skills[phrase],
                in_resume=res_cnt > 0,
                resume_count=res_cnt,
                job_count=jd_cnt,
            )
            mask_jd = re.sub(pat, " ", mask_jd)

    # Single tokens from remaining JD
    tokens = re.findall(r"[a-zA-Z0-9\+\#\.\/\-]{2,}", mask_jd)
    jd_token_counts: Counter[str] = Counter()
    for tok in tokens:
        c = tok.strip(".,;:!?()[]{}\'\"")
        if (
            len(c) >= 2
            and c not in STOPWORDS
            and not c.isdigit()
            and not re.match(r"^\d+\+?$", c)
            and c not in mapping_dict
        ):
            jd_token_counts[c] += 1

    res_tokens = [w.strip(".,;:!?()[]{}\'\"") for w in re.findall(r"[a-zA-Z0-9\+\#\.\/\-]{2,}", norm_res)]
    res_counter = Counter(res_tokens)

    for word, cnt in jd_token_counts.items():
        res_cnt = res_counter.get(word, 0)
        cat = known_skills.get(word, "domain")
        mapping_dict[word] = KeywordMapping(
            keyword=word,
            category=cat,
            in_resume=res_cnt > 0,
            resume_count=res_cnt,
            job_count=cnt,
        )

    if not mapping_dict:
        return ResumeAgentOutput(
            match_score=0.0,
            keyword_score=0.0,
            section_score=section_score,
            ats_score=round(0.25 * section_score, 1),
            matched_keywords=[],
            missing_keywords=[],
            keyword_mapping=[],
            section_analysis=section_patterns,
            formatting=formatting,
            suggestions="No job description keywords found.",
        )

    mapping_list = sorted(mapping_dict.values(), key=lambda m: (-m.job_count, m.keyword))
    matched = sorted([m.keyword for m in mapping_list if m.in_resume])
    missing = sorted([m.keyword for m in mapping_list if not m.in_resume])

    kw_score = round((len(matched) / len(mapping_list)) * 100, 1)
    ats_score = round(0.75 * kw_score + 0.25 * section_score, 1)

    sugg_parts: list[str] = []
    if missing:
        sugg_parts.append(f"Include missing keywords: {', '.join(missing[:5])}.")
    missing_secs = [k for k, v in section_patterns.items() if not v]
    if missing_secs and inp.resume_text.strip():
        sugg_parts.append(f"Add missing sections: {', '.join(missing_secs[:3])}.")
    if fmt_issues:
        sugg_parts.append(fmt_issues[0])

    suggestions = " ".join(sugg_parts) if sugg_parts else "Resume matches all extracted job keywords and sections."

    return ResumeAgentOutput(
        match_score=kw_score,
        keyword_score=kw_score,
        section_score=section_score,
        ats_score=ats_score,
        matched_keywords=matched,
        missing_keywords=missing,
        keyword_mapping=mapping_list,
        section_analysis=section_patterns,
        formatting=formatting,
        suggestions=suggestions,
    )


if __name__ == "__main__":
    _inp = ResumeAgentInput(
        resume_text="I know python and javascript.",
        job_description="We need python, javascript, and typescript developer.",
    )
    _out = run_resume_agent(_inp)
    assert _out.match_score > 0
    assert "typescript" in _out.missing_keywords
    assert any(m.keyword == "typescript" and not m.in_resume for m in _out.keyword_mapping)
    print("Resume agent checks passed.")
