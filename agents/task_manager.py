"""
Task manager for the Engineering OS multi-agent framework.
Handles task creation, delegation, tracking, and lifecycle management.
"""
import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from agents.base_agent import AgentContext, AgentResult
from agents.agent_registry import AgentRegistry
from agents.communication_bus import CommunicationBus

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task to be executed by an agent."""
    task_id: str
    project_id: str
    agent_type: str
    title: str
    description: str
    input_data: dict
    status: str = "pending"  # pending, assigned, running, completed, failed
    priority: int = 0
    assigned_agent: Optional[str] = None
    result: Optional[AgentResult] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskManager:
    """
    Manages agent task lifecycle: creation, assignment, execution tracking.
    """

    def __init__(
        self,
        agent_registry: AgentRegistry,
        communication_bus: CommunicationBus,
    ):
        self.registry = agent_registry
        self.bus = communication_bus
        self._tasks: dict[str, Task] = {}
        self._lock = asyncio.Lock()

    async def create_task(
        self,
        project_id: str,
        agent_type: str,
        title: str,
        description: str,
        input_data: dict,
        priority: int = 0,
    ) -> Task:
        """Create a new task for an agent."""
        task = Task(
            task_id=str(uuid.uuid4()),
            project_id=project_id,
            agent_type=agent_type,
            title=title,
            description=description,
            input_data=input_data,
            priority=priority,
        )
        async with self._lock:
            self._tasks[task.task_id] = task
        logger.info(f"Created task {task.task_id}: {title} for {agent_type}")
        return task

    async def execute_task(self, task_id: str) -> AgentResult:
        """Execute a task by finding and delegating to the appropriate agent."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")
            
            task.status = "assigned"
            task.started_at = datetime.utcnow()

        # Find appropriate agent
        agent = self.registry.get_agent(task.agent_type)
        if not agent:
            # Try to find any agent that can handle this
            agent = self.registry.find_agent_for_task(task.agent_type)
        
        if not agent:
            error_msg = f"No agent available for task type: {task.agent_type}"
            logger.error(error_msg)
            result = AgentResult(
                task_id=task_id,
                agent_type=task.agent_type,
                status="failed",
                output={},
                summary=error_msg,
                error_message=error_msg,
                started_at=task.started_at,
                completed_at=datetime.utcnow(),
            )
            async with self._lock:
                task.status = "failed"
                task.result = result
                task.completed_at = datetime.utcnow()
            return result

        # Execute
        try:
            task.status = "running"
            context = AgentContext(
                task_id=task_id,
                project_id=task.project_id,
                input_data=task.input_data,
            )
            
            result = await agent.execute(context)
            
            async with self._lock:
                task.status = "completed" if result.status == "success" else "failed"
                task.result = result
                task.completed_at = datetime.utcnow()
            
            logger.info(f"Task {task_id} completed: {result.status}")
            return result
            
        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            logger.error(error_msg)
            result = AgentResult(
                task_id=task_id,
                agent_type=task.agent_type,
                status="failed",
                output={},
                summary=error_msg,
                error_message=error_msg,
                started_at=task.started_at,
                completed_at=datetime.utcnow(),
            )
            async with self._lock:
                task.status = "failed"
                task.result = result
                task.completed_at = datetime.utcnow()
            return result

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get task details."""
        async with self._lock:
            return self._tasks.get(task_id)

    async def get_project_tasks(
        self, project_id: str, status: Optional[str] = None
    ) -> list[Task]:
        """Get all tasks for a project."""
        async with self._lock:
            tasks = [
                t for t in self._tasks.values()
                if t.project_id == project_id
            ]
            if status:
                tasks = [t for t in tasks if t.status == status]
            return sorted(tasks, key=lambda t: t.priority, reverse=True)

    async def get_agent_tasks(
        self, agent_type: str, status: Optional[str] = None
    ) -> list[Task]:
        """Get tasks for a specific agent type."""
        async with self._lock:
            tasks = [
                t for t in self._tasks.values()
                if t.agent_type == agent_type
            ]
            if status:
                tasks = [t for t in tasks if t.status == status]
            return tasks

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if task and task.status in ("pending", "assigned", "running"):
                task.status = "cancelled"
                task.completed_at = datetime.utcnow()
                return True
            return False

    async def get_statistics(self) -> dict:
        """Get task execution statistics."""
        async with self._lock:
            total = len(self._tasks)
            completed = sum(1 for t in self._tasks.values() if t.status == "completed")
            failed = sum(1 for t in self._tasks.values() if t.status == "failed")
            running = sum(1 for t in self._tasks.values() if t.status == "running")
            pending = sum(1 for t in self._tasks.values() if t.status == "pending")
            
            return {
                "total_tasks": total,
                "completed": completed,
                "failed": failed,
                "running": running,
                "pending": pending,
                "success_rate": (completed / total * 100) if total > 0 else 0,
            }