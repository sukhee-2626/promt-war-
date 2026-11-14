from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import get_session
from app.models.tables import Board, Task

router = APIRouter(prefix="/tracker", tags=["tracker"])

@router.post("/boards")
def create_board(board: Board, session: Session = Depends(get_session)):
    session.add(board)
    session.commit()
    session.refresh(board)
    return board

@router.get("/boards/{user_id}")
def get_boards(user_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Board).where(Board.user_id == user_id)).all()

@router.post("/tasks")
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/boards/{board_id}/tasks")
def get_tasks(board_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Task).where(Task.board_id == board_id)).all()

@router.patch("/tasks/{task_id}")
def update_task(task_id: int, status: str, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    task.status = status
    session.add(task)
    session.commit()
    return task

@router.get("/boards/{board_id}/progress")
def get_progress(board_id: int, session: Session = Depends(get_session)):
    tasks = session.exec(select(Task).where(Task.board_id == board_id)).all()
    total = len(tasks)
    completed = len([t for t in tasks if t.status == "DONE"])
    return {"total": total, "completed": completed, "percent": (completed / total * 100) if total > 0 else 0}
