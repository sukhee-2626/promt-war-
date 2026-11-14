"""
Phase 1 graph tests.
Run: pytest backend/tests/test_graph.py -v
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from app.graph.loader import learning_path, prerequisites, GRAPH


def test_js_before_react():
    path = learning_path(known_ids=[], target_ids=["react"])
    assert path.index("javascript") < path.index("react"), \
        "javascript must come before react"


def test_react_before_nextjs():
    path = learning_path(known_ids=[], target_ids=["nextjs"])
    assert path.index("react") < path.index("nextjs"), \
        "react must come before nextjs"


def test_demo_scenario():
    """Student knows python, sql, html → Full Stack gaps."""
    known = ["python", "sql", "html"]
    targets = ["javascript", "react", "nodejs"]
    path = learning_path(known_ids=known, target_ids=targets)
    # html already known → not in path
    assert "html" not in path
    # python already known → not in path
    assert "python" not in path
    # javascript before react
    assert path.index("javascript") < path.index("react")


def test_known_skills_excluded():
    path = learning_path(known_ids=["javascript"], target_ids=["react"])
    assert "javascript" not in path


def test_prerequisites_react():
    prereqs = prerequisites("react")
    assert "javascript" in prereqs
    assert "html" in prereqs


if __name__ == "__main__":
    test_js_before_react()
    test_react_before_nextjs()
    test_demo_scenario()
    test_known_skills_excluded()
    test_prerequisites_react()
    print("All graph tests passed.")
