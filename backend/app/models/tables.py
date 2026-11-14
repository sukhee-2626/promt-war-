from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    goal_role: str
    weekly_hours: float = 10.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserSkill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    skill_id: str
    mastery: float = 0.3
    confidence: float = 0.5
    source: str = "inferred"
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Skill(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    category: str
    description: str

class SkillEdge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    from_skill: str = Field(foreign_key="skill.id")
    to_skill: str = Field(foreign_key="skill.id")

class Role(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str

class RoleSkill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: str = Field(foreign_key="role.id")
    skill_id: str = Field(foreign_key="skill.id")
    required_mastery: float = 0.7
    weight: float = 1.0

class Roadmap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    version: int = 1
    status: str = "active"
    reason: str = "initial"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RoadmapNode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    roadmap_id: int = Field(foreign_key="roadmap.id")
    skill_id: str
    order: int
    status: str = "pending"
    est_hours: float = 10.0

class Assessment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    skill_id: str
    score: float
    taken_at: datetime = Field(default_factory=datetime.utcnow)

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    type: str
    payload: str = "{}"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    agent: str
    input: str
    output: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
