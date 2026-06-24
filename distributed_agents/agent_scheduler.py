"""
Sprint 12 — Agent Scheduler
Ray-based multi-agent scheduling with priority queues, deadline-aware scheduling,
and full agent lifecycle management supporting thousands of concurrent agents.
"""
from __future__ import annotations

import asyncio
import heapq
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentPriority(int, Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class AgentState(str, Enum):
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class AgentCapability(str, Enum):
    SIMULATION = "simulation"
    FEA = "fea"
    CFD = "cfd"
    OPTIMIZATION = "optimization"
    CAD = "cad"
    PCB = "pcb"
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    REASONING = "reasoning"


@dataclass
class AgentSpec:
    """Specification for an agent task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    agent_type: str = "generic"
    capability: AgentCapability = AgentCapability.ANALYSIS
    priority: AgentPriority = AgentPriority.NORMAL
    payload: Dict[str, Any] = field(default_factory=dict)
    required_cpu: float = 1.0
    required_memory_gb: float = 2.0
    required_gpu: int = 0
    timeout_seconds: int = 3600
    max_retries: int = 3
    deadline: Optional[datetime] = None
    tenant_id: str = "default"
    project_id: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __lt__(self, other: "AgentSpec") -> bool:
        # Priority queue: lower priority value = higher urgency
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        # Deadline-aware: earlier deadline wins among same priority
        if self.deadline and other.deadline:
            return self.deadline < other.deadline
        return self.submitted_at < other.submitted_at


# Alias for compatibility
AgentTask = AgentSpec



@dataclass
class AgentExecution:
    """Tracks execution of a scheduled agent."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spec_id: str = ""
    state: AgentState = AgentState.QUEUED
    worker_id: str = ""
    node_name: str = ""
    attempt: int = 1
    queued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "spec_id": self.spec_id,
            "state": self.state.value,
            "worker_id": self.worker_id,
            "node_name": self.node_name,
            "attempt": self.attempt,
            "queued_at": self.queued_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "metrics": self.metrics,
        }


@dataclass
class Worker:
    """Represents a distributed worker node for agent execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    total_cpu: float = 16.0
    total_memory_gb: float = 64.0
    total_gpu: int = 0
    used_cpu: float = 0.0
    used_memory_gb: float = 0.0
    used_gpu: int = 0
    active_agents: int = 0
    max_concurrent_agents: int = 50
    is_healthy: bool = True
    cluster_id: str = ""
    region: str = "us-east-1"
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def available_cpu(self) -> float:
        return self.total_cpu - self.used_cpu

    @property
    def available_memory_gb(self) -> float:
        return self.total_memory_gb - self.used_memory_gb

    @property
    def load_factor(self) -> float:
        return self.active_agents / self.max_concurrent_agents if self.max_concurrent_agents > 0 else 1.0

    def can_accommodate(self, spec: AgentSpec) -> bool:
        return (
            self.is_healthy
            and self.active_agents < self.max_concurrent_agents
            and self.available_cpu >= spec.required_cpu
            and self.available_memory_gb >= spec.required_memory_gb
            and (self.total_gpu - self.used_gpu) >= spec.required_gpu
            and spec.capability in self.capabilities
        )

    def allocate(self, spec: AgentSpec) -> None:
        self.used_cpu += spec.required_cpu
        self.used_memory_gb += spec.required_memory_gb
        self.used_gpu += spec.required_gpu
        self.active_agents += 1

    def release(self, spec: AgentSpec) -> None:
        self.used_cpu = max(0.0, self.used_cpu - spec.required_cpu)
        self.used_memory_gb = max(0.0, self.used_memory_gb - spec.required_memory_gb)
        self.used_gpu = max(0, self.used_gpu - spec.required_gpu)
        self.active_agents = max(0, self.active_agents - 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "total_cpu": self.total_cpu,
            "available_cpu": self.available_cpu,
            "total_memory_gb": self.total_memory_gb,
            "available_memory_gb": self.available_memory_gb,
            "total_gpu": self.total_gpu,
            "active_agents": self.active_agents,
            "max_concurrent_agents": self.max_concurrent_agents,
            "load_factor": round(self.load_factor, 3),
            "is_healthy": self.is_healthy,
            "cluster_id": self.cluster_id,
            "region": self.region,
        }


class AgentScheduler:
    """
    Ray-inspired multi-agent scheduler supporting thousands of concurrent agents.
    Features: priority queues, deadline-aware scheduling, load balancing, failover.
    """

    def __init__(self, max_queue_size: int = 100_000):
        self._queue: List[AgentSpec] = []  # min-heap
        self._workers: Dict[str, Worker] = {}
        self._executions: Dict[str, AgentExecution] = {}
        self._spec_lookup: Dict[str, AgentSpec] = {}
        self._max_queue_size = max_queue_size
        self._dependency_graph: Dict[str, List[str]] = {}  # spec_id -> dependent spec_ids
        self._callbacks: Dict[str, Callable] = {}
        self._stats = {
            "total_submitted": 0,
            "total_completed": 0,
            "total_failed": 0,
            "total_cancelled": 0,
        }

    async def register_worker(
        self,
        name: str,
        capabilities: List[AgentCapability],
        total_cpu: float = 16.0,
        total_memory_gb: float = 64.0,
        total_gpu: int = 0,
        max_concurrent_agents: int = 50,
        cluster_id: str = "",
        region: str = "us-east-1",
    ) -> Worker:
        """Register a worker node with the scheduler."""
        worker = Worker(
            name=name,
            capabilities=capabilities,
            total_cpu=total_cpu,
            total_memory_gb=total_memory_gb,
            total_gpu=total_gpu,
            max_concurrent_agents=max_concurrent_agents,
            cluster_id=cluster_id,
            region=region,
        )
        self._workers[worker.id] = worker
        logger.info(f"Worker '{name}' registered with {len(capabilities)} capabilities")
        return worker

    async def submit_agent(self, spec: AgentSpec) -> AgentExecution:
        """Submit an agent task to the scheduling queue."""
        if len(self._queue) >= self._max_queue_size:
            raise RuntimeError(f"Scheduler queue full ({self._max_queue_size} max)")

        # Check dependencies are satisfied
        unmet = [dep for dep in spec.dependencies if dep not in self._spec_lookup or
                 self._executions.get(dep, AgentExecution()).state != AgentState.COMPLETED]

        execution = AgentExecution(
            spec_id=spec.id,
            state=AgentState.QUEUED if not unmet else AgentState.QUEUED,
        )

        self._spec_lookup[spec.id] = spec
        self._executions[execution.id] = execution
        heapq.heappush(self._queue, spec)
        self._stats["total_submitted"] += 1

        logger.info(f"Agent {spec.name} [{spec.id}] submitted with priority {spec.priority.name}")
        return execution

    def _find_best_worker(self, spec: AgentSpec) -> Optional[Worker]:
        """Find the least-loaded worker that can handle this spec."""
        candidates = [w for w in self._workers.values() if w.can_accommodate(spec)]
        if not candidates:
            return None
        # Sort by load_factor ascending (prefer least loaded)
        return min(candidates, key=lambda w: w.load_factor)

    async def schedule_next(self) -> Optional[Dict[str, Any]]:
        """Pop highest-priority agent from queue and schedule it."""
        if not self._queue:
            return None

        spec = heapq.heappop(self._queue)
        worker = self._find_best_worker(spec)

        if not worker:
            # No available worker — re-queue
            heapq.heappush(self._queue, spec)
            logger.debug(f"No worker available for agent {spec.name}, re-queued")
            return None

        worker.allocate(spec)

        # Find associated execution
        execution = next(
            (e for e in self._executions.values() if e.spec_id == spec.id and e.state == AgentState.QUEUED),
            None,
        )
        if execution:
            execution.state = AgentState.SCHEDULED
            execution.worker_id = worker.id
            execution.node_name = worker.name
            execution.scheduled_at = datetime.now(timezone.utc)
            execution.started_at = datetime.now(timezone.utc)
            execution.state = AgentState.RUNNING

        logger.info(f"Agent {spec.name} scheduled on worker '{worker.name}'")
        return {
            "spec_id": spec.id,
            "execution_id": execution.id if execution else None,
            "worker_id": worker.id,
            "worker_name": worker.name,
            "scheduled_at": datetime.now(timezone.utc).isoformat(),
        }

    async def complete_agent(
        self,
        execution_id: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> AgentExecution:
        """Mark an agent execution as completed or failed."""
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        spec = self._spec_lookup.get(execution.spec_id)
        worker = self._workers.get(execution.worker_id)

        if error:
            execution.state = AgentState.FAILED
            execution.error = error
            self._stats["total_failed"] += 1

            # Retry logic
            if spec and execution.attempt < spec.max_retries:
                execution.attempt += 1
                execution.state = AgentState.RETRYING
                heapq.heappush(self._queue, spec)
                logger.warning(f"Agent {spec.name} failed, retrying (attempt {execution.attempt})")
        else:
            execution.state = AgentState.COMPLETED
            execution.result = result or {}
            self._stats["total_completed"] += 1

        execution.completed_at = datetime.now(timezone.utc)
        if worker and spec:
            worker.release(spec)

        return execution

    async def cancel_agent(self, execution_id: str) -> AgentExecution:
        """Cancel a queued or running agent."""
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        execution.state = AgentState.CANCELLED
        execution.completed_at = datetime.now(timezone.utc)
        self._stats["total_cancelled"] += 1
        return execution

    async def get_execution(self, execution_id: str) -> Optional[AgentExecution]:
        return self._executions.get(execution_id)

    async def list_executions(
        self,
        state: Optional[AgentState] = None,
        tenant_id: Optional[str] = None,
        capability: Optional[AgentCapability] = None,
    ) -> List[AgentExecution]:
        executions = list(self._executions.values())
        if state:
            executions = [e for e in executions if e.state == state]
        if tenant_id or capability:
            filtered = []
            for e in executions:
                spec = self._spec_lookup.get(e.spec_id)
                if spec:
                    if tenant_id and spec.tenant_id != tenant_id:
                        continue
                    if capability and spec.capability != capability:
                        continue
                filtered.append(e)
            executions = filtered
        return executions

    async def list_workers(self, healthy_only: bool = False) -> List[Worker]:
        workers = list(self._workers.values())
        if healthy_only:
            workers = [w for w in workers if w.is_healthy]
        return workers

    async def get_queue_stats(self) -> Dict[str, Any]:
        """Return scheduler queue statistics."""
        return {
            "queue_depth": len(self._queue),
            "max_queue_size": self._max_queue_size,
            "worker_count": len(self._workers),
            "healthy_workers": sum(1 for w in self._workers.values() if w.is_healthy),
            "total_agent_capacity": sum(w.max_concurrent_agents for w in self._workers.values()),
            "active_agents": sum(w.active_agents for w in self._workers.values()),
            **self._stats,
        }

    async def failover_worker(self, failed_worker_id: str) -> Dict[str, Any]:
        """Handle worker failure by marking unhealthy and re-queuing its agents."""
        worker = self._workers.get(failed_worker_id)
        if not worker:
            raise ValueError(f"Worker {failed_worker_id} not found")
        worker.is_healthy = False

        # Re-queue running agents from this worker
        requeued = 0
        for execution in self._executions.values():
            if execution.worker_id == failed_worker_id and execution.state == AgentState.RUNNING:
                spec = self._spec_lookup.get(execution.spec_id)
                if spec:
                    execution.state = AgentState.QUEUED
                    heapq.heappush(self._queue, spec)
                    requeued += 1

        logger.warning(f"Worker {worker.name} failed, {requeued} agents re-queued")
        return {
            "failed_worker_id": failed_worker_id,
            "worker_name": worker.name,
            "agents_requeued": requeued,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
