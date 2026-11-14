from app.agents.planner import PlannerInput, run_planner

def test_planner_basic():
    inp = PlannerInput(
        user_id=1,
        role_id="fullstack",
        gaps=[{"skill_id": "react", "current_mastery": 0.1}, {"skill_id": "javascript", "current_mastery": 0.0}],
        known_skill_ids=[],
        weekly_hours=10.0
    )
    output = run_planner(inp)
    assert len(output.nodes) > 0
    assert output.nodes[0].skill_id == "javascript" # Should come before react due to topology
    print("Planner test passed.")

if __name__ == "__main__":
    test_planner_basic()
