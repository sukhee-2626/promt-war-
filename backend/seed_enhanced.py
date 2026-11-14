import json
import sys
import os

# Add backend to PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__)))

from sqlmodel import Session
from app.db import engine, create_db
from app.models.new_tables import AptitudeQuestion, DSAQuestion, SQLChallenge

def seed():
    create_db()
    with Session(engine) as session:
        # Aptitude
        with open("content/aptitude/sets.json") as f:
            data = json.load(f)
            for item in data:
                q = AptitudeQuestion(question=item["question"], answer=item["answer"])
                session.add(q)
        
        # DSA
        with open("content/dsa/data.json") as f:
            data = json.load(f)
            for item in data:
                q = DSAQuestion(title=item["title"], difficulty=item["difficulty"], topic=item["topic"])
                session.add(q)
        
        # SQL
        with open("content/sql/challenges.json") as f:
            data = json.load(f)
            for item in data:
                # Tags is a list. Need to convert to string.
                tags = ",".join(item.get("tags", []))
                q = SQLChallenge(title=item["title"], difficulty=item["difficulty"], tags=tags)
                session.add(q)
        
        session.commit()
    print("Database seeded.")

if __name__ == "__main__":
    seed()
