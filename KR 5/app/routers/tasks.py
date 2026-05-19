from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from ..schemas import Task, TaskCreate, ErrorResponse
from ..dependencies import get_current_user, get_storage
from ..storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    new_task = storage.create(task_data.model_dump(), current_user.id)
    return new_task

@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[str] = None,
    min_priority: Optional[int] = None,
    current_user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    tasks = storage.get_all(current_user.id, status, min_priority)
    return tasks

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    current_user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_by_id(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: int,
    status_update: dict,
    current_user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_by_id(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    new_status = status_update.get("status")
    if not new_status:
        raise HTTPException(status_code=422, detail="Status field is required")
    
    updated_task = storage.update_status(task_id, new_status)
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user=Depends(get_current_user),
    storage: TaskStorage = Depends(get_storage)
):
    task = storage.get_by_id(task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    storage.delete(task_id)
    return