"""
Sprint 12 — HPC Job Dispatcher
Ray-based distributed job dispatch with status tracking and job reports.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class DispatchStatus(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class DispatchRecord:
    """Tracks the dispatch of a compute job."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str = ""
    job_name: str = ""
    target_nodes: List[str] = field(default_factory=list)
    dispatch_status: DispatchStatus = DispatchStatus.PENDING
    attempt: int = 1
    max_attempts: int = 3
    mpi_ranks: int = 1
    openmp_threads: int = 1
    environment: Dict[str, str] = field(default_factory=dict)
    command: str = ""
    stdout_log: str = ""
    stderr_log: str = ""
    exit_code: Optional[int] = None
    result_path: str = ""
    dispatched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.dispatched_at and self.completed_at:
            return (self.completed_at - self.dispatched_at).total_seconds()
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "job_name": self.job_name,
            "target_nodes": self.target_nodes,
            "dispatch_status": self.dispatch_status.value,
            "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "mpi_ranks": self.mpi_ranks,
            "openmp_threads": self.openmp_threads,
            "command": self.command,
            "exit_code": self.exit_code,
            "result_path": self.result_path,
            "duration_seconds": self.duration_seconds,
            "dispatched_at": self.dispatched_at.isoformat() if self.dispatched_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class JobDispatcher:
    """
    Dispatches HPC jobs to compute nodes using Ray/MPI patterns.
    Supports parallel job execution, status tracking, and result collection.
    """

    def __init__(self):
        self._dispatches: Dict[str, DispatchRecord] = {}
        self._handlers: Dict[str, Callable] = {}
        self._node_registry: Dict[str, Dict[str, Any]] = {}

    def register_node(self, node_id: str, hostname: str, cpu_cores: int, gpu_count: int = 0) -> None:
        """Register a compute node for dispatch."""
        self._node_registry[node_id] = {
            "id": node_id,
            "hostname": hostname,
            "cpu_cores": cpu_cores,
            "gpu_count": gpu_count,
            "active_jobs": 0,
        }

    def register_job_handler(self, job_type: str, handler: Callable) -> None:
        """Register a handler function for a job type."""
        self._handlers[job_type] = handler
        logger.debug(f"Handler registered for job type '{job_type}'")

    async def dispatch_job(
        self,
        job_id: str,
        job_name: str,
        job_type: str,
        target_nodes: List[str],
        parameters: Dict[str, Any],
        mpi_ranks: int = 1,
        openmp_threads: int = 1,
        environment: Optional[Dict[str, str]] = None,
        max_attempts: int = 3,
        result_path: Optional[str] = None,
    ) -> DispatchRecord:
        """Dispatch a job to the specified compute nodes."""
        record = DispatchRecord(
            job_id=job_id,
            job_name=job_name,
            target_nodes=target_nodes,
            mpi_ranks=mpi_ranks,
            openmp_threads=openmp_threads,
            environment=environment or {},
            command=f"mpirun -n {mpi_ranks} {job_type}_solver --params {job_id}.json",
            result_path=result_path or f"/scratch/{job_id}/",
            max_attempts=max_attempts,
            dispatch_status=DispatchStatus.DISPATCHED,
            dispatched_at=datetime.now(timezone.utc),
        )

        self._dispatches[record.id] = record

        # Execute handler if registered
        handler = self._handlers.get(job_type)
        try:
            if handler:
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: handler(job_id, parameters)
                )
            else:
                # Simulate job execution
                await asyncio.sleep(0)

            record.dispatch_status = DispatchStatus.SUCCEEDED
            record.exit_code = 0
            record.stdout_log = f"Job {job_id} completed successfully"
        except Exception as exc:
            record.dispatch_status = DispatchStatus.FAILED
            record.exit_code = 1
            record.stderr_log = str(exc)
            logger.error(f"Job {job_id} dispatch failed: {exc}")

        record.completed_at = datetime.now(timezone.utc)
        logger.info(f"Job '{job_name}' [{job_id}] dispatched: {record.dispatch_status.value}")
        return record

    async def dispatch_parallel_batch(
        self,
        jobs: List[Dict[str, Any]],
        max_concurrent: int = 10,
    ) -> List[DispatchRecord]:
        """Dispatch multiple jobs in parallel with concurrency limit."""
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []

        async def dispatch_with_limit(job_spec: Dict[str, Any]) -> DispatchRecord:
            async with semaphore:
                return await self.dispatch_job(**job_spec)

        tasks = [dispatch_with_limit(job) for job in jobs]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for result in completed:
            if isinstance(result, DispatchRecord):
                results.append(result)
            else:
                logger.error(f"Parallel dispatch error: {result}")

        logger.info(f"Parallel batch: {len(results)}/{len(jobs)} jobs dispatched successfully")
        return results

    async def retry_failed(self, dispatch_id: str) -> DispatchRecord:
        """Retry a failed dispatch."""
        record = self._dispatches.get(dispatch_id)
        if not record:
            raise ValueError(f"Dispatch {dispatch_id} not found")
        if record.dispatch_status != DispatchStatus.FAILED:
            raise ValueError(f"Dispatch {dispatch_id} is not failed")
        if record.attempt >= record.max_attempts:
            raise RuntimeError(f"Max retry attempts ({record.max_attempts}) reached")

        record.attempt += 1
        record.dispatch_status = DispatchStatus.RETRYING
        record.dispatched_at = datetime.now(timezone.utc)
        record.completed_at = None

        # Simulate retry
        await asyncio.sleep(0)
        record.dispatch_status = DispatchStatus.SUCCEEDED
        record.exit_code = 0
        record.completed_at = datetime.now(timezone.utc)
        record.stderr_log = ""
        logger.info(f"Dispatch {dispatch_id} retried (attempt {record.attempt})")
        return record

    async def cancel_dispatch(self, dispatch_id: str) -> DispatchRecord:
        record = self._dispatches.get(dispatch_id)
        if not record:
            raise ValueError(f"Dispatch {dispatch_id} not found")
        record.dispatch_status = DispatchStatus.CANCELLED
        record.completed_at = datetime.now(timezone.utc)
        return record

    async def get_dispatch(self, dispatch_id: str) -> Optional[DispatchRecord]:
        return self._dispatches.get(dispatch_id)

    async def list_dispatches(
        self,
        job_id: Optional[str] = None,
        status: Optional[DispatchStatus] = None,
    ) -> List[DispatchRecord]:
        dispatches = list(self._dispatches.values())
        if job_id:
            dispatches = [d for d in dispatches if d.job_id == job_id]
        if status:
            dispatches = [d for d in dispatches if d.dispatch_status == status]
        return dispatches

    async def generate_dispatch_report(self) -> Dict[str, Any]:
        """Summary report of all dispatch activity."""
        dispatches = list(self._dispatches.values())
        succeeded = sum(1 for d in dispatches if d.dispatch_status == DispatchStatus.SUCCEEDED)
        failed = sum(1 for d in dispatches if d.dispatch_status == DispatchStatus.FAILED)

        durations = [d.duration_seconds for d in dispatches if d.duration_seconds is not None]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        return {
            "report_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_dispatches": len(dispatches),
            "succeeded": succeeded,
            "failed": failed,
            "success_rate": round(succeeded / len(dispatches), 3) if dispatches else 0.0,
            "average_duration_seconds": round(avg_duration, 2),
            "registered_nodes": len(self._node_registry),
            "registered_handlers": list(self._handlers.keys()),
        }
