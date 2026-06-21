from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class TaskState(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"

class ProjectState(str, Enum):
    INITIATED = "INITIATED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    RELEASED = "RELEASED"

class ExecutionTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    domain: str
    dependencies: List[str] = Field(default_factory=list)
    state: TaskState = TaskState.PENDING
    iteration: int = 0
    max_iterations: int = 3
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ProjectWorkflow(BaseModel):
    project_id: str
    name: str
    state: ProjectState = ProjectState.INITIATED
    tasks: List[ExecutionTask] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class Milestone(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    target_date: datetime
    achieved_date: Optional[datetime] = None
    criteria: List[str] = Field(default_factory=list)
    status: str = "PENDING"
