from typing import Optional
from app.schemas import TaskCreate, TaskOut


class TaskStorage:
    def __init__(self):
        self._tasks: dict[int, TaskOut] = {}
        self._counter: int = 0

    def create(self, data: TaskCreate, owner_id: int) -> TaskOut:
        self._counter += 1
        task = TaskOut(
            id=self._counter,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            owner_id=owner_id,
        )
        self._tasks[self._counter] = task
        return task

    def get_all(
        self,
        owner_id: int,
        status: Optional[str] = None,
        min_priority: Optional[int] = None,
    ) -> list[TaskOut]:
        result = [t for t in self._tasks.values() if t.owner_id == owner_id]
        if status:
            result = [t for t in result if t.status == status]
        if min_priority is not None:
            result = [t for t in result if t.priority >= min_priority]
        return result

    def get_by_id(self, task_id: int) -> Optional[TaskOut]:
        return self._tasks.get(task_id)

    def update_status(self, task_id: int, new_status: str) -> Optional[TaskOut]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        updated = task.model_copy(update={"status": new_status})
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def get_all_tasks(self) -> list[TaskOut]:
        return list(self._tasks.values())

    def clear(self):
        self._tasks.clear()
        self._counter = 0


task_storage = TaskStorage()
