"""
Outreach Agent.
Generates cold recruiter email and LinkedIn outreach messages.
"""
from __future__ import annotations
import json, os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class OutreachInput(BaseModel):
    candidate_name: str = "Candidate"
    target_role: str
    company_name: str
    recruiter_name: str = "Hiring Team"
    key_skills: list[str] = []
    portfolio_url: str = ""


class OutreachOutput(BaseModel):
    email_subject: str
    email_body: str
    linkedin_message: str


def _call_llm(prompt: str) -> str:
    provider = os.getenv("LLM_PROVIDER", "ollama")
    if provider == "groq":
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        resp = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp.choices[0].message.content
    import httpx
    resp = httpx.post(
        f"{os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}/api/generate",
        json={"model": os.getenv("OLLAMA_MODEL", "llama3.1:8b"), "prompt": prompt, "stream": False},
        timeout=30,
    )
    return resp.json()["response"]


_PROMPT = """Generate a cold recruiter email and a short LinkedIn connection note (<300 chars).
Candidate: {candidate_name}
Target Role: {target_role}
Company: {company_name}
Recruiter: {recruiter_name}
Key Skills: {skills}
Portfolio: {portfolio_url}

Return ONLY valid JSON in this exact format:
{{
  "email_subject": "...",
  "email_body": "...",
  "linkedin_message": "..."
}}"""


def run_outreach_agent(inp: OutreachInput) -> OutreachOutput:
    skills_str = ", ".join(inp.key_skills) if inp.key_skills else "software engineering"
    prompt = _PROMPT.format(
        candidate_name=inp.candidate_name,
        target_role=inp.target_role,
        company_name=inp.company_name,
        recruiter_name=inp.recruiter_name,
        skills=skills_str,
        portfolio_url=inp.portfolio_url or "N/A",
    )

    try:
        raw = _call_llm(prompt).strip()
        start, end = raw.find("{"), raw.rfind("}") + 1
        if start != -1 and end != -1:
            raw = raw[start:end]
        data = json.loads(raw)
        return OutreachOutput(
            email_subject=data["email_subject"],
            email_body=data["email_body"],
            linkedin_message=data["linkedin_message"],
        )
    except Exception:
        # ponytail: fallback template used when LLM offline; upgrade with scraping company news and personalization hooks.
        portfolio_snippet = f"\nPortfolio: {inp.portfolio_url}" if inp.portfolio_url else ""
        return OutreachOutput(
            email_subject=f"{inp.target_role} Role - {inp.candidate_name}",
            email_body=(
                f"Hi {inp.recruiter_name},\n\n"
                f"I noticed {inp.company_name} is looking for a {inp.target_role}. "
                f"With hands-on experience in {skills_str}, I believe my background aligns well with your team's goals.{portfolio_snippet}\n\n"
                f"Would you be open to a brief 10-minute chat this week?\n\n"
                f"Best regards,\n{inp.candidate_name}"
            ),
            linkedin_message=(
                f"Hi {inp.recruiter_name}, noticed your talent search for {inp.company_name}. "
                f"I'm a {inp.target_role} specializing in {skills_str}. Would love to connect!"
            ),
        )


if __name__ == "__main__":
    out = run_outreach_agent(OutreachInput(
        candidate_name="Alice",
        target_role="Backend Engineer",
        company_name="Acme Corp",
        key_skills=["Python", "FastAPI"],
    ))
    assert out.email_subject and out.email_body and out.linkedin_message
    assert "Acme Corp" in out.email_body
    assert "Backend Engineer" in out.email_subject
    print("Self-check passed.")
