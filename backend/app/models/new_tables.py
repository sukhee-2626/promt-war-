from typing import Optional
from sqlmodel import Field, SQLModel

class AptitudeQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    answer: str

class DSAQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    difficulty: str
    topic: str

class SQLChallenge(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    difficulty: str
    tags: str

class TrackerTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    completed: bool = False
