from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from ..dependencies import require_admin, get_storage
from ..storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
async def get_stats(
    admin=Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
):
    all_tasks = storage.get_all_tasks_for_stats()
    total_tasks = len(all_tasks)
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for task in all_tasks:
        if task.status in by_status:
            by_status[task.status] += 1
    return {"total_tasks": total_tasks, "by_status": by_status}

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_task(
    task_id: int,
    admin=Depends(require_admin),
    storage: TaskStorage = Depends(get_storage)
):
    if not storage.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return