from pydantic import BaseModel, Field, conint, constr, ConfigDict
from typing import Optional, Dict, List

class TaskBase(BaseModel):
    title: constr(min_length=3, max_length=80) = Field(..., description="Название задачи, от 3 до 80 символов")
    description: Optional[str] = Field(None, description="Описание задачи")
    status: str = Field("todo", description="Статус задачи: todo, in_progress, done")
    priority: conint(ge=1, le=5) = Field(..., description="Приоритет от 1 до 5")

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int
    model_config = ConfigDict(from_attributes=True)

class User(BaseModel):
    id: int
    role: str

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    error_type: str