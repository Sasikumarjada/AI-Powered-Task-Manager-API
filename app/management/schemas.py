from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Allowed task statuses"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    """Allowed task priorities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskCreate(BaseModel):
    """Schema for creating a new task"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Detailed task description"
    )
    status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description="Current status of the task"
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        description="Task priority (if not provided, AI will suggest)"
    )

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip()

    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip()


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)"""
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=5000
    )
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v.strip() if v else None

    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Description cannot be empty or whitespace only')
        return v.strip() if v else None


class TaskResponse(BaseModel):
    """Schema for task responses"""
    id: int
    title: str
    description: str
    status: str
    priority: str
    ai_summary: Optional[str] = None
    ai_suggested_priority: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskWithAI(TaskResponse):
    """Extended response schema highlighting AI features"""
    pass
