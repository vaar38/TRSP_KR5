from pydantic import BaseModel, Field
from typing import Optional, Literal


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: int = Field(..., ge=1, le=5)


class TaskStatusUpdate(BaseModel):
    status: Literal["todo", "in_progress", "done"]


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    priority: int
    owner_id: int


class UserOut(BaseModel):
    id: int
    role: str


class HealthOut(BaseModel):
    status: str
    env: str


class RoomUsersOut(BaseModel):
    room_id: str
    users: list[str]


class AdminStats(BaseModel):
    total_tasks: int
    by_status: dict[str, int]
