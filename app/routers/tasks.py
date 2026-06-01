from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.schemas import TaskCreate, TaskOut, TaskStatusUpdate
from app.dependencies import get_current_user, get_storage
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=201)
def create_task(
    data: TaskCreate,
    user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    return storage.create(data, owner_id=user.id)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    status: Optional[str] = None,
    min_priority: Optional[int] = None,
    user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    return storage.get_all(user.id, status=status, min_priority=min_priority)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    task = storage.get_by_id(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    task = storage.get_by_id(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return storage.update_status(task_id, body.status)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage),
):
    task = storage.get_by_id(task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.delete(task_id)
