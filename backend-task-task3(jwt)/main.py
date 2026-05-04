from fastapi import FastAPI, HTTPException, Depends, Query
from typing_extensions import Annotated, Optional
from sqlmodel import select, Session

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security import (
    decode_access_token,
    get_password_hash,
    verify_password,
    create_access_token,
)
import models as m
from enum import Enum
import db
import re

app = FastAPI()


class PriorityEnum(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"

    @property
    def id(self) -> int:
        return {"Low": 1, "Medium": 2, "High": 3}[self.value]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    session: db.SessionDependency,
    token: str = Depends(oauth2_scheme),
) -> m.User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token missing user id")
    user = session.get(m.User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_admin_user(current_user: m.User = Depends(get_current_user)) -> m.User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


@app.post("/registration/", response_model=m.UserRead, tags=["User"])
def registration(
    user: m.UserCreate,
    session: db.SessionDependency,
):
    if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d).{8,72}$", user.password):
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
    new_user = m.User(
        username=user.username, hashed_password=get_password_hash(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@app.post("/login/", tags=["User"])
def login(
    session: db.SessionDependency,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = session.exec(
        select(m.User).where(m.User.username == form_data.username)
    ).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": str(user.id), "is_admin": user.is_admin}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/admin/tasks/", response_model=list[m.Task], tags=["Admin"])
def get_all_tasks(
    session: db.SessionDependency,
    current_admin: m.User = Depends(get_current_admin_user),
):
    tasks = session.exec(select(m.Task)).all()
    return tasks


@app.post("/tasks/", response_model=m.TaskCreate, tags=["Task"])
def create_task(
    task: m.TaskCreate,
    session: db.SessionDependency,
    current_user: m.User = Depends(get_current_user),
):
    new_task = m.Task(
        title=task.title,
        priority_id=task.priority_id,
        deadline=task.deadline,
        description=task.description,
        owner_id=current_user.id,
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
    current_user: m.User = Depends(get_current_user),
):
    task = session.get(m.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
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
    current_user: m.User = Depends(get_current_user),
):
    task = session.get(m.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this task"
        )
    session.delete(task)
    session.commit()
    return {"detail": "Task deleted successfully"}


@app.get("/tasks/", response_model=list[m.Task], tags=["Task"])
def get_tasks(
    session: db.SessionDependency,
    current_user: m.User = Depends(get_current_user),
    count: Optional[int] = 5,
    page: Optional[int] = 1,
    priority: Optional[PriorityEnum] = Query(
        None, description="Filter by priority (Low, Medium, High)"
    ),
    sort_by_deadline: bool = Query(False, description="Sort by deadline (ascending)"),
):

    query = select(m.Task).where(m.Task.owner_id == current_user.id)
    if priority is not None:
        query = query.where(m.Task.priority_id == priority.id)

    tasks = session.exec(query).all()

    if sort_by_deadline:
        tasks = sorted(tasks, key=lambda t: t.deadline if t.deadline else float("inf"))

    paginated_tasks = tasks[(page - 1) * count : page * count]
    return paginated_tasks


@app.get("/tasks/{task_id}/", response_model=m.Task, tags=["Task"])
def get_task(
    task_id: int,
    session: db.SessionDependency,
    current_user: m.User = Depends(get_current_user),
):
    task = session.get(m.Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")
    return task
