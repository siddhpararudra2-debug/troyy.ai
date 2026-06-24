"""
Simulation Scheduler
Schedules HPC simulation jobs (FEA, CFD, Optimization)
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class SimulationScheduler:
    """Schedules HPC simulation jobs"""

    def __init__(self):
        self._sim_jobs: Dict[str, Dict[str, Any]] = {}

    async def submit_job(
        self,
        job_type: str,
        input_data: Dict[str, Any],
        num_nodes: int = 1,
    ) -> Dict[str, Any]:
        """Submit a new HPC simulation job"""
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "type": job_type,
            "input_data": input_data,
            "num_nodes": num_nodes,
            "status": "queued",
            "submitted_at": datetime.utcnow().isoformat(),
        }
        self._sim_jobs[job_id] = job
        logger.info(f"Submitted HPC job {job_id} of type {job_type}")
        return job

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job details"""
        return self._sim_jobs.get(job_id)
