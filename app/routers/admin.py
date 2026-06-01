from fastapi import APIRouter, Depends, HTTPException
from app.schemas import AdminStats, UserOut
from app.dependencies import require_admin, get_storage
from app.storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
def get_stats(
    admin: UserOut = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
):
    tasks = storage.get_all_tasks()
    by_status: dict[str, int] = {"todo": 0, "in_progress": 0, "done": 0}
    for t in tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1
    return AdminStats(total_tasks=len(tasks), by_status=by_status)


@router.delete("/tasks/{task_id}", status_code=204)
def admin_delete_task(
    task_id: int,
    admin: UserOut = Depends(require_admin),
    storage: TaskStorage = Depends(get_storage),
):
    task = storage.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.delete(task_id)
