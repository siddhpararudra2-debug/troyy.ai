"""
Execution Monitor for Engineering OS
Monitors task and workflow execution, tracks status and issues.
"""
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ExecutionMonitor:
    """
    Tracks execution of tasks and workflows, records status and errors.
    """

    def __init__(self):
        self._task_history: Dict[str, List[Dict[str, Any]]] = {}
        self._workflow_status: Dict[str, Any] = {}

    def record_task_completion(
        self,
        task_id: str,
        task_type: str,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
    ):
        """
        Record task completion status.
        """
        if task_id not in self._task_history:
            self._task_history[task_id] = []
        record = {
            "task_id": task_id,
            "task_type": task_type,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
            "error": error,
        }
        self._task_history[task_id].append(record)
        if status == "success":
            logger.info(f"Task {task_id} completed successfully")
        elif status == "failed":
            logger.error(f"Task {task_id} failed: {error}")

    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """
        Get all history events for a given task.
        """
        return self._task_history.get(task_id, [])

    def get_workflow_status(self, mission_id: str) -> Dict[str, Any]:
        """
        Get current status of a mission/workflow.
        """
        return self._workflow_status.get(
            mission_id,
            {"status": "unknown", "tasks_completed": 0, "tasks_total": 0}
        )
