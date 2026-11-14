"""
Skill Knowledge Graph loader.
Builds a NetworkX DiGraph from seed JSON files.
Provides: prerequisites(skill_id), learning_path(known, targets)
"""
import json
from pathlib import Path
import networkx as nx

DATA = Path(__file__).parent.parent.parent.parent / "data"


def build_graph() -> nx.DiGraph:
    skills = json.loads((DATA / "skills.json").read_text())
    edges  = json.loads((DATA / "skill_edges.json").read_text())
    G = nx.DiGraph()
    for s in skills:
        G.add_node(s["id"], **s)
    for src, dst in edges:
        G.add_edge(src, dst)   # src must be learned before dst
    return G


# Singleton — build once per process
GRAPH: nx.DiGraph = build_graph()


def prerequisites(skill_id: str) -> list[str]:
    """All ancestors of skill_id (must be learned first)."""
    return list(nx.ancestors(GRAPH, skill_id))


def learning_path(known_ids: list[str], target_ids: list[str]) -> list[str]:
    """
    Ordered list of skills to learn to reach all targets from known skills.
    Uses topological sort over the subgraph of required nodes.
    """
    required: set[str] = set()
    for target in target_ids:
        required.add(target)
        for prereq in nx.ancestors(GRAPH, target):
            required.add(prereq)

    # Remove already-known skills
    to_learn = required - set(known_ids)

    # Subgraph of skills still needed, topologically sorted
    sub = GRAPH.subgraph(to_learn | set(target_ids))
    ordered = [n for n in nx.topological_sort(sub) if n in to_learn]
    return ordered


def role_skills(role_name: str) -> list[dict]:
    """Load required skills for a role from roles.json."""
    roles = json.loads((DATA / "roles.json").read_text())
    for r in roles:
        if r["id"] == role_name or r["name"].lower() == role_name.lower():
            return r["skills"]
    return []
