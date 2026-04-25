from datetime import datetime
from typing_extensions import Optional
from sqlmodel import Field, SQLModel, String, Column, Relationship
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

    tasks: list["Task"] = Relationship(back_populates="user")


class UserCreate(BaseModel):
    username: str
    password: str


class Priority(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    tasks: list["Task"] = Relationship(back_populates="priority")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    priority_id: int = Field(default=1, ge=1, le=3, foreign_key="priority.id")
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")

    priority: Priority = Relationship(back_populates="tasks")
    user: User = Relationship(back_populates="tasks")


class TaskCreate(BaseModel):
    title: str
    priority_id: int = Field(default=1, ge=1, le=3)
    deadline: Optional[datetime] = None
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    priority_id: Optional[int] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None
