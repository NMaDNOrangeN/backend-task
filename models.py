from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, String, Column
from pydantic import BaseModel
import db


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=Column(
            String(collation="NOCASE"),
            index=True,
            unique=True,
            nullable=False,
        )
    )
    password: str = Field(regex=r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$")


class UserCreate(BaseModel):
    username: str
    password: str


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    priority: int = Field(default=1, ge=1, le=3, foreign_key="priority.id")
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")


class TaskCreate(BaseModel):
    title: str
    priority: int = Field(default=1, ge=1, le=3)
    deadline: Optional[datetime] = None
    description: Optional[str] = None


class Priority(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[int] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None
