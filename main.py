from fastapi import FastAPI, HTTPException, Depends, Query
from typing import Annotated, Optional
from sqlmodel import select
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import models as m
import db
import re

app = FastAPI()
security = HTTPBasic(auto_error=False)


def check_auth(
    session: db.SessionDependency,
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization required")
    user = session.exec(
        select(m.User).where(
            m.User.username == credentials.username,
            m.User.password == credentials.password,
        )
    ).first()
    if not user:
        raise HTTPException(status_code=403, detail="Wrong username or password")
    return credentials


@app.post("/registration/", response_model=m.UserCreate, tags=["User"])
def registration(
    user: m.UserCreate,
    session: db.SessionDependency,
) -> m.UserCreate:
    if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$", user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain at least one letter and one digit.",
        )
    existing_user = session.exec(
        select(m.User).where(m.User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists.",
        )
    user = m.User(username=user.username, password=user.password)
    session.add(user)
    session.commit()
    return user


@app.post("/tasks/", response_model=m.TaskCreate, tags=["Task"])
def create_task(
    task: m.TaskCreate,
    session: db.SessionDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(check_auth)],
) -> m.TaskCreate:
    new_task = m.Task(
        title=task.title,
        priority=task.priority,
        deadline=task.deadline,
        description=task.description,
        owner_id=session.exec(
            select(m.User).where(m.User.username == credentials.username)
        )
        .first()
        .id,
    )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return new_task


@app.put("/tasks/{task_id}/", response_model=m.TaskUpdate, tags=["Task"])
def update_task(
    task_id: int,
    task_update: m.TaskUpdate,
    session: db.SessionDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(check_auth)],
) -> m.TaskUpdate:
    task = session.get(m.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if (
        task.owner_id
        != session.exec(select(m.User).where(m.User.username == credentials.username))
        .first()
        .id
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task"
        )
    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}/", tags=["Task"])
def delete_task(
    task_id: int,
    session: db.SessionDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(check_auth)],
):
    task = session.get(m.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if (
        task.owner_id
        != session.exec(select(m.User).where(m.User.username == credentials.username))
        .first()
        .id
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this task"
        )
    session.delete(task)
    session.commit()
    return {"detail": "Task deleted successfully"}


@app.get("/tasks/", response_model=list[m.Task], tags=["Task"])
def get_tasks(
    session: db.SessionDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(check_auth)],
    count: Optional[int] = 5,
    page: Optional[int] = 1,
    priority: Optional[int] = Query(
        None, description="Filter tasks by priority (1-3)", ge=1, le=3
    ),
    sort_by_deadline: bool = Query(False, description="Sort by deadline (ascending)"),
):
    user_id = (
        session.exec(select(m.User).where(m.User.username == credentials.username))
        .first()
        .id
    )

    query = select(m.Task).where(m.Task.owner_id == user_id)
    if priority is not None:
        query = query.where(m.Task.priority == priority)

    tasks = session.exec(query).all()

    if sort_by_deadline:
        tasks = sorted(tasks, key=lambda t: t.deadline if t.deadline else float("inf"))

    paginated_tasks = tasks[(page - 1) * count : page * count]
    return paginated_tasks


@app.get("/tasks/{task_id}/", response_model=m.Task, tags=["Task"])
def get_task(
    task_id: int,
    session: db.SessionDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(check_auth)],
):
    task = session.get(m.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if (
        task.owner_id
        != session.exec(select(m.User).where(m.User.username == credentials.username))
        .first()
        .id
    ):
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return task
