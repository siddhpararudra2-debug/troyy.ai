"""
Agent Scheduler
Schedules agents across available resources
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AgentScheduler:
    """Schedules agent tasks across nodes"""

    def __init__(self):
        self._scheduled_tasks: Dict[str, Dict[str, Any]] = {}

    async def schedule_task(
        self,
        agent_type: str,
        task_name: str,
        input_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Schedule a new agent task"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "agent_type": agent_type,
            "task_name": task_name,
            "input_data": input_data or {},
            "status": "queued",
            "scheduled_at": datetime.utcnow().isoformat(),
        }
        self._scheduled_tasks[task_id] = task
        logger.info(f"Scheduled task {task_name} for agent {agent_type}")
        return task

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a scheduled task"""
        return self._scheduled_tasks.get(task_id)

    async def list_tasks(self) -> List[Dict[str, Any]]:
        """List all scheduled tasks"""
        return list(self._scheduled_tasks.values())
