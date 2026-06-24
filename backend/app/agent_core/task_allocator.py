"""
Task Allocator for Engineering OS
Assigns tasks to appropriate agents and manages execution.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from agents.agent_runtime import AgentRuntime
from agents.task_manager import TaskManager

logger = logging.getLogger(__name__)


class TaskAllocator:
    """
    Allocates tasks to agents and manages execution lifecycle.
    """

    def __init__(self, agent_runtime: AgentRuntime):
        self.agent_runtime = agent_runtime
        self.task_manager: TaskManager = agent_runtime.task_manager
        self._task_history: List[Dict] = []

    async def allocate_and_execute(
        self,
        task: Dict[str, Any],
        mission_id: str,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Allocate a task to an agent and execute it.
        """
        task_id = task.get("task_id", str(uuid.uuid4()))
        task_type = task.get("task_type", "unknown")
        agent_type = task.get("agent_type", "mechanical")

        logger.info(f"Allocating task {task_id} ({task_type}) to {agent_type}")

        # Create task in TaskManager
        await self.task_manager.create_task(
            task_id=task_id,
            agent_type=agent_type,
            title=task_type,
            description=task.get("requirements", ""),
            input_data=task.get("input_data", {}),
            project_id=project_id,
            priority=task.get("priority", 5),
        )

        # Execute the task
        result = await self.task_manager.execute_task(task_id)

        self._task_history.append({
            "task_id": task_id,
            "mission_id": mission_id,
            "project_id": project_id,
            "status": result.status,
            "started_at": result.started_at.isoformat(),
            "completed_at": result.completed_at.isoformat(),
        })

        return {
            "task_id": task_id,
            "status": result.status,
            "output": result.output,
            "summary": result.summary,
        }
