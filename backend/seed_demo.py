"""
Demo seed script.
Creates demo learner: Python, SQL, basic HTML → target Full Stack Developer.
Run: python backend/seed_demo.py
"""
import httpx, json

API = "http://localhost:8000"

def seed():
    # Create demo profile
    resp = httpx.post(f"{API}/profile", json={
        "name": "Alex Demo",
        "email": "alex@skillforge.demo",
        "goal_role": "full_stack_developer",
        "weekly_hours": 10,
        "free_text": (
            "I know Python well and have been using it for 2 years. "
            "I have intermediate SQL skills and have worked with PostgreSQL. "
            "I know basic HTML and some CSS. I've built Flask APIs. "
            "I understand Git and use it daily. I'm familiar with REST APIs."
        ),
        "resume_text": "",
        "github_descriptions": [
            "A REST API built with FastAPI and SQLite for task management",
            "Data analysis notebook using pandas and matplotlib on sales data",
            "Personal portfolio website with HTML and CSS",
        ],
    }, timeout=60)

    if resp.status_code != 200:
        print(f"Failed to create profile: {resp.text}")
        return

    user = resp.json()
    user_id = user["id"]
    print(f"Created demo user: ID={user_id}")
    print(f"Detected {len(user['skills'])} skills")

    # Trigger roadmap build
    road = httpx.get(f"{API}/roadmap/{user_id}", timeout=30).json()
    print(f"Roadmap: {road['nodes_count'] if 'nodes_count' in road else len(road.get('nodes',[]))} nodes, "
          f"{road.get('total_weeks')} weeks")

    print(f"\n🎯 Demo user ready!")
    print(f"   Profile:   http://localhost:3000/dashboard/{user_id}")
    print(f"   Match:     http://localhost:3000/match/{user_id}")
    print(f"   Roadmap:   http://localhost:3000/roadmap/{user_id}")
    print(f"   Assess JS: http://localhost:3000/assess/{user_id}/javascript")
    print(f"   Progress:  http://localhost:3000/progress/{user_id}")
    print(f"   Pivot:     http://localhost:3000/pivot/{user_id}")
    print(f"\n   User ID: {user_id}  (use this in all URLs above)")

    return user_id


if __name__ == "__main__":
    seed()
