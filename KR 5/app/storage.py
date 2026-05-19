from typing import Dict, List
from .schemas import Task

class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create(self, task_data: dict, owner_id: int) -> Task:
        task_id = self._next_id
        self._next_id += 1
        new_task = Task(id=task_id, owner_id=owner_id, **task_data)
        self._tasks[task_id] = new_task
        return new_task

    def get_by_id(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def get_all(self, owner_id: int, status: str = None, min_priority: int = None) -> List[Task]:
        tasks = [t for t in self._tasks.values() if t.owner_id == owner_id]
        if status:
            tasks = [t for t in tasks if t.status == status]
        if min_priority:
            tasks = [t for t in tasks if t.priority >= min_priority]
        return tasks

    def update_status(self, task_id: int, new_status: str) -> Task | None:
        task = self._tasks.get(task_id)
        if task:
            task.status = new_status
        return task

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def get_all_tasks_for_stats(self) -> List[Task]:
        return list(self._tasks.values())

    def clear(self):
        self._tasks.clear()
        self._next_id = 1



storage = TaskStorage()