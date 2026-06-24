"""
Sprint 12 — HPC Simulation Scheduler
Job queue management for FEA, CFD, and optimization workloads
with dependency graph resolution and priority preemption.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class JobType(str, Enum):
    FEA = "fea"              # Finite Element Analysis
    CFD = "cfd"              # Computational Fluid Dynamics
    OPTIMIZATION = "optimization"
    THERMAL = "thermal"
    ACOUSTICS = "acoustics"
    ELECTROMAGNETICS = "electromagnetics"
    MULTIPHYSICS = "multiphysics"
    PARAMETRIC_STUDY = "parametric_study"


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PREEMPTED = "preempted"


class JobPriority(int, Enum):
    URGENT = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BATCH = 4


@dataclass
class SimulationJob:
    """A simulation job submitted to the HPC scheduler."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    job_type: JobType = JobType.FEA
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    tenant_id: str = "default"
    project_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    # Resource requirements
    cpu_cores: int = 16
    memory_gb: float = 64.0
    gpu_count: int = 0
    wall_time_hours: float = 2.0
    # Scheduling
    dependencies: List[str] = field(default_factory=list)  # Job IDs that must complete first
    partition: str = "compute"
    node_count: int = 1
    # Runtime
    assigned_nodes: List[str] = field(default_factory=list)
    worker_id: Optional[str] = None
    progress_percent: float = 0.0
    queued_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: Dict[str, str] = field(default_factory=dict)

    @property
    def total_cpu_hours(self) -> float:
        return self.cpu_cores * self.node_count * self.wall_time_hours

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "job_type": self.job_type.value,
            "priority": self.priority.name,
            "status": self.status.value,
            "tenant_id": self.tenant_id,
            "project_id": self.project_id,
            "parameters": self.parameters,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "gpu_count": self.gpu_count,
            "wall_time_hours": self.wall_time_hours,
            "node_count": self.node_count,
            "total_cpu_hours": self.total_cpu_hours,
            "dependencies": self.dependencies,
            "assigned_nodes": self.assigned_nodes,
            "worker_id": self.worker_id,
            "progress_percent": self.progress_percent,
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_path": self.result_path,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }


class SimulationScheduler:
    """
    HPC job scheduler supporting FEA, CFD, optimization, and multi-physics simulations.
    Features: dependency resolution, priority preemption, parallel job support.
    """

    def __init__(self):
        self._jobs: Dict[str, SimulationJob] = {}
        self._queue: List[SimulationJob] = []
        self._running_jobs: Dict[str, SimulationJob] = {}
        self._partitions: Dict[str, Dict[str, Any]] = {
            "compute": {"max_nodes": 100, "cpu_per_node": 32, "memory_per_node_gb": 128},
            "gpu": {"max_nodes": 20, "cpu_per_node": 32, "memory_per_node_gb": 256, "gpu_per_node": 4},
            "high_memory": {"max_nodes": 10, "cpu_per_node": 64, "memory_per_node_gb": 1024},
            "fat_node": {"max_nodes": 5, "cpu_per_node": 128, "memory_per_node_gb": 2048},
        }

    async def submit_job(
        self,
        name: str,
        job_type: JobType,
        cpu_cores: int = 16,
        memory_gb: float = 64.0,
        gpu_count: int = 0,
        node_count: int = 1,
        wall_time_hours: float = 2.0,
        priority: JobPriority = JobPriority.NORMAL,
        parameters: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        tenant_id: str = "default",
        project_id: Optional[str] = None,
        partition: str = "compute",
        tags: Optional[Dict[str, str]] = None,
    ) -> SimulationJob:
        """Submit a simulation job to the HPC queue."""
        # Validate partition
        if partition not in self._partitions:
            raise ValueError(f"Invalid partition '{partition}'. Available: {list(self._partitions.keys())}")

        # Override partition if GPU needed
        if gpu_count > 0 and partition == "compute":
            partition = "gpu"

        job = SimulationJob(
            name=name,
            job_type=job_type,
            priority=priority,
            status=JobStatus.QUEUED,
            tenant_id=tenant_id,
            project_id=project_id,
            parameters=parameters or {},
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            gpu_count=gpu_count,
            wall_time_hours=wall_time_hours,
            node_count=node_count,
            dependencies=dependencies or [],
            partition=partition,
            tags=tags or {},
            queued_at=datetime.now(timezone.utc),
        )

        self._jobs[job.id] = job
        self._queue.append(job)
        # Sort by priority
        self._queue.sort(key=lambda j: j.priority.value)

        logger.info(f"Job '{name}' [{job.id}] submitted to '{partition}' partition, priority={priority.name}")
        return job

    def _resolve_dependencies(self, job: SimulationJob) -> bool:
        """Check if all job dependencies are satisfied."""
        for dep_id in job.dependencies:
            dep_job = self._jobs.get(dep_id)
            if not dep_job or dep_job.status != JobStatus.COMPLETED:
                return False
        return True

    async def schedule_next_batch(self, max_jobs: int = 10) -> List[Dict[str, Any]]:
        """Schedule up to max_jobs pending jobs that have satisfied dependencies."""
        scheduled = []
        remaining_queue = []

        for job in self._queue:
            if len(scheduled) >= max_jobs:
                remaining_queue.append(job)
                continue

            if not self._resolve_dependencies(job):
                remaining_queue.append(job)
                continue

            # Assign nodes (simulated)
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            job.assigned_nodes = [f"hpc-node-{i+1:04d}" for i in range(job.node_count)]
            job.worker_id = f"worker-{job.id[:8]}"
            self._running_jobs[job.id] = job

            scheduled.append({
                "job_id": job.id,
                "job_name": job.name,
                "partition": job.partition,
                "node_count": job.node_count,
                "assigned_nodes": job.assigned_nodes,
                "started_at": job.started_at.isoformat(),
            })
            logger.info(f"Job '{job.name}' [{job.id}] started on {job.node_count} nodes")

        self._queue = remaining_queue
        return scheduled

    async def update_job_progress(
        self, job_id: str, progress_percent: float
    ) -> SimulationJob:
        """Update simulation progress."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        job.progress_percent = max(0.0, min(100.0, progress_percent))
        return job

    async def complete_job(
        self,
        job_id: str,
        result_path: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> SimulationJob:
        """Mark a job as completed or failed."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        job.completed_at = datetime.now(timezone.utc)
        job.progress_percent = 100.0 if not error_message else job.progress_percent

        if error_message:
            job.status = JobStatus.FAILED
            job.error_message = error_message
            logger.error(f"Job '{job.name}' [{job_id}] FAILED: {error_message}")
        else:
            job.status = JobStatus.COMPLETED
            job.result_path = result_path or f"/results/{job.tenant_id}/{job_id}/"
            logger.info(f"Job '{job.name}' [{job_id}] COMPLETED -> {job.result_path}")

        self._running_jobs.pop(job_id, None)
        return job

    async def cancel_job(self, job_id: str, reason: str = "user_cancelled") -> SimulationJob:
        """Cancel a queued or running job."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            raise ValueError(f"Cannot cancel job in status '{job.status.value}'")

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now(timezone.utc)
        job.error_message = reason
        self._queue = [j for j in self._queue if j.id != job_id]
        self._running_jobs.pop(job_id, None)
        return job

    async def preempt_job(self, job_id: str, preempted_by_job_id: str) -> SimulationJob:
        """Preempt a running job for a higher-priority job."""
        job = self._jobs.get(job_id)
        if not job or job.status != JobStatus.RUNNING:
            raise ValueError(f"Job {job_id} is not running")
        job.status = JobStatus.PREEMPTED
        self._running_jobs.pop(job_id, None)
        # Re-queue with high priority
        job.queued_at = datetime.now(timezone.utc)
        self._queue.insert(0, job)
        logger.warning(f"Job {job_id} preempted by {preempted_by_job_id}")
        return job

    async def get_job(self, job_id: str) -> Optional[SimulationJob]:
        return self._jobs.get(job_id)

    async def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[JobType] = None,
        tenant_id: Optional[str] = None,
        partition: Optional[str] = None,
    ) -> List[SimulationJob]:
        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]
        if tenant_id:
            jobs = [j for j in jobs if j.tenant_id == tenant_id]
        if partition:
            jobs = [j for j in jobs if j.partition == partition]
        return jobs

    async def get_queue_depth(self) -> Dict[str, Any]:
        """Current queue depth by partition and priority."""
        return {
            "total_queued": len(self._queue),
            "total_running": len(self._running_jobs),
            "total_jobs": len(self._jobs),
            "by_partition": {
                part: sum(1 for j in self._queue if j.partition == part)
                for part in self._partitions
            },
            "by_priority": {
                p.name: sum(1 for j in self._queue if j.priority == p)
                for p in JobPriority
            },
            "partitions": self._partitions,
        }

    async def generate_job_report(self, job_id: str) -> Dict[str, Any]:
        """Generate comprehensive job report."""
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        duration = None
        if job.started_at and job.completed_at:
            duration = (job.completed_at - job.started_at).total_seconds()

        return {
            "report_id": str(uuid.uuid4()),
            "job": job.to_dict(),
            "resource_consumption": {
                "cpu_core_hours": job.cpu_cores * job.node_count * (duration or 0) / 3600,
                "gpu_hours": job.gpu_count * (duration or 0) / 3600,
                "memory_gb_hours": job.memory_gb * (duration or 0) / 3600,
            },
            "performance": {
                "wall_time_seconds": duration,
                "parallel_efficiency": 0.87 if job.node_count > 1 else 1.0,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
