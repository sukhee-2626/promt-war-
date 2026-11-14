from app.agents.aptitude_agent import run_aptitude_agent, AptitudeInput
from app.agents.resume_agent import run_resume_agent, ResumeAgentInput
from app.agents.outreach_agent import run_outreach_agent, OutreachInput

def test_resume_agent():
    inp = ResumeAgentInput(
        resume_text="I know python and javascript.",
        job_description="We need python, javascript, and typescript developer."
    )
    output = run_resume_agent(inp)
    assert output.match_score > 0
    assert "typescript" in output.missing_keywords


def test_resume_agent_deep_ats():
    resume = """
    Jane Developer
    jane@example.com | 555-0199

    Professional Summary
    Senior full-stack engineer with 6 years experience building distributed backend systems.

    Experience
    Senior Engineer, CloudTech
    - Architected REST APIs with Python and FastAPI handling 10M requests daily.
    - Led Docker and Kubernetes container deployment across AWS clusters.
    - Optimized PostgreSQL and Redis data layer for low-latency queries.

    Skills
    Python, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, REST APIs

    Education
    B.S. Computer Science, University of Technology
    """

    jd = """
    We are seeking a Senior Backend Engineer to join our team.
    Requirements:
    - Strong proficiency in Python, FastAPI, and REST APIs
    - Hands-on experience with Docker, Kubernetes, and AWS
    - Knowledge of PostgreSQL and Redis
    - Excellent leadership and communication skills
    """

    inp = ResumeAgentInput(resume_text=resume, job_description=jd)
    output = run_resume_agent(inp)

    # Keyword mapping assertions
    assert output.keyword_mapping
    mapping_by_kw = {m.keyword: m for m in output.keyword_mapping}
    assert "python" in mapping_by_kw
    assert mapping_by_kw["python"].in_resume is True
    assert mapping_by_kw["python"].resume_count >= 1
    assert "leadership" in mapping_by_kw
    assert mapping_by_kw["leadership"].in_resume is False
    assert mapping_by_kw["leadership"].category == "soft_skill"

    # Deep ATS metrics
    assert "python" in output.matched_keywords
    assert "leadership" in output.missing_keywords
    assert output.section_analysis["experience"] is True
    assert output.section_analysis["education"] is True
    assert output.section_analysis["skills"] is True
    assert output.section_analysis["contact_info"] is True
    assert output.formatting.has_contact_info is True
    assert output.formatting.has_bullet_points is True
    assert output.ats_score > 0
    assert output.section_score > 0


def test_aptitude_agent():
    # This should trigger the fallback due to LLM not being available in test env
    inp = AptitudeInput(category="python", n_questions=1)
    output = run_aptitude_agent(inp)
    assert len(output.questions) == 1
    assert output.questions[0].question == "What is 1+1?"

def test_outreach_agent():
    inp = OutreachInput(
        candidate_name="Alice",
        target_role="Backend Engineer",
        company_name="Acme Corp",
        recruiter_name="Bob",
        key_skills=["Python", "FastAPI"],
    )
    output = run_outreach_agent(inp)
    assert output.email_subject
    assert output.email_body
    assert output.linkedin_message
    assert "Acme Corp" in output.email_body
    assert "Bob" in output.linkedin_message
