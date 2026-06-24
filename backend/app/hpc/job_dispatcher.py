"""
Job Dispatcher
Dispatches HPC jobs to compute resources
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class JobDispatcher:
    """Dispatches HPC jobs to compute resources"""

    def __init__(self):
        self._dispatch_history: List[Dict[str, Any]] = []

    async def dispatch_job(
        self,
        job_id: str,
        target_node: str,
    ) -> Dict[str, Any]:
        """Dispatch a job to a node"""
        dispatch_id = str(uuid.uuid4())
        record = {
            "id": dispatch_id,
            "job_id": job_id,
            "target_node": target_node,
            "status": "dispatched",
            "dispatched_at": datetime.utcnow().isoformat(),
        }
        self._dispatch_history.append(record)
        logger.info(f"Dispatched job {job_id} to {target_node}")
        return record
