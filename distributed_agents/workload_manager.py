"""
Sprint 12 — Workload Manager
Workload partitioning, distribution, resource reservation, and quota management
for the distributed agent execution platform.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class WorkloadType(str, Enum):
    BATCH = "batch"
    STREAMING = "streaming"
    INTERACTIVE = "interactive"
    HPC = "hpc"
    AGENT = "agent"
    INFERENCE = "inference"


class PartitionStrategy(str, Enum):
    ROUND_ROBIN = "round_robin"
    HASH = "hash"
    RANGE = "range"
    LOCALITY = "locality"
    LEAST_LOADED = "least_loaded"


@dataclass
class ResourceQuota:
    """Per-tenant resource quota."""
    tenant_id: str = "default"
    max_cpu_cores: float = 100.0
    max_memory_gb: float = 400.0
    max_gpu: int = 8
    max_concurrent_agents: int = 500
    max_storage_gb: float = 10_000.0
    used_cpu: float = 0.0
    used_memory_gb: float = 0.0
    used_gpu: int = 0
    used_agents: int = 0
    used_storage_gb: float = 0.0

    @property
    def cpu_utilization(self) -> float:
        return self.used_cpu / self.max_cpu_cores if self.max_cpu_cores > 0 else 0.0

    @property
    def quota_available(self) -> bool:
        return (
            self.used_cpu < self.max_cpu_cores
            and self.used_memory_gb < self.max_memory_gb
            and self.used_agents < self.max_concurrent_agents
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "cpu": {"max": self.max_cpu_cores, "used": self.used_cpu, "utilization": round(self.cpu_utilization, 3)},
            "memory_gb": {"max": self.max_memory_gb, "used": self.used_memory_gb},
            "gpu": {"max": self.max_gpu, "used": self.used_gpu},
            "agents": {"max": self.max_concurrent_agents, "used": self.used_agents},
            "storage_gb": {"max": self.max_storage_gb, "used": self.used_storage_gb},
            "quota_available": self.quota_available,
        }


@dataclass
class WorkloadPartition:
    """A partition of a workload assigned to a specific worker."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workload_id: str = ""
    partition_index: int = 0
    total_partitions: int = 1
    data_range_start: Optional[int] = None
    data_range_end: Optional[int] = None
    assigned_worker_id: str = ""
    assigned_region: str = ""
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "workload_id": self.workload_id,
            "partition_index": self.partition_index,
            "total_partitions": self.total_partitions,
            "data_range_start": self.data_range_start,
            "data_range_end": self.data_range_end,
            "assigned_worker_id": self.assigned_worker_id,
            "assigned_region": self.assigned_region,
            "status": self.status,
            "result": self.result,
        }


@dataclass
class Workload:
    """A distributed workload specification."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    workload_type: WorkloadType = WorkloadType.BATCH
    tenant_id: str = "default"
    total_items: int = 1
    item_cpu_cores: float = 1.0
    item_memory_gb: float = 2.0
    partition_strategy: PartitionStrategy = PartitionStrategy.LEAST_LOADED
    partitions: List[WorkloadPartition] = field(default_factory=list)
    status: str = "pending"
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    @property
    def progress(self) -> float:
        if not self.partitions:
            return 0.0
        done = sum(1 for p in self.partitions if p.status == "completed")
        return done / len(self.partitions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "workload_type": self.workload_type.value,
            "tenant_id": self.tenant_id,
            "total_items": self.total_items,
            "partition_count": len(self.partitions),
            "progress": round(self.progress, 3),
            "status": self.status,
            "partition_strategy": self.partition_strategy.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class WorkloadManager:
    """
    Manages workload partitioning, distribution, and quota enforcement
    for the Engineering OS distributed agent platform.
    """

    def __init__(self):
        self._workloads: Dict[str, Workload] = {}
        self._quotas: Dict[str, ResourceQuota] = {}
        self._worker_registry: Dict[str, Dict[str, Any]] = {}  # worker_id -> info

    async def create_quota(
        self,
        tenant_id: str,
        max_cpu_cores: float = 100.0,
        max_memory_gb: float = 400.0,
        max_gpu: int = 8,
        max_concurrent_agents: int = 500,
        max_storage_gb: float = 10_000.0,
    ) -> ResourceQuota:
        """Create or update resource quota for a tenant."""
        quota = ResourceQuota(
            tenant_id=tenant_id,
            max_cpu_cores=max_cpu_cores,
            max_memory_gb=max_memory_gb,
            max_gpu=max_gpu,
            max_concurrent_agents=max_concurrent_agents,
            max_storage_gb=max_storage_gb,
        )
        self._quotas[tenant_id] = quota
        logger.info(f"Quota created for tenant '{tenant_id}': {max_cpu_cores} CPU, {max_memory_gb}GB RAM")
        return quota

    async def get_quota(self, tenant_id: str) -> Optional[ResourceQuota]:
        return self._quotas.get(tenant_id)

    async def reserve_resources(
        self,
        tenant_id: str,
        cpu_cores: float,
        memory_gb: float,
        gpu: int = 0,
    ) -> bool:
        """Reserve resources against tenant quota. Returns True if successful."""
        quota = self._quotas.get(tenant_id)
        if not quota:
            # Auto-create default quota
            quota = ResourceQuota(tenant_id=tenant_id)
            self._quotas[tenant_id] = quota

        if (
            quota.used_cpu + cpu_cores > quota.max_cpu_cores
            or quota.used_memory_gb + memory_gb > quota.max_memory_gb
            or quota.used_gpu + gpu > quota.max_gpu
        ):
            logger.warning(f"Quota exceeded for tenant '{tenant_id}'")
            return False

        quota.used_cpu += cpu_cores
        quota.used_memory_gb += memory_gb
        quota.used_gpu += gpu
        quota.used_agents += 1
        return True

    async def release_resources(
        self,
        tenant_id: str,
        cpu_cores: float,
        memory_gb: float,
        gpu: int = 0,
    ) -> None:
        """Release previously reserved resources."""
        quota = self._quotas.get(tenant_id)
        if quota:
            quota.used_cpu = max(0.0, quota.used_cpu - cpu_cores)
            quota.used_memory_gb = max(0.0, quota.used_memory_gb - memory_gb)
            quota.used_gpu = max(0, quota.used_gpu - gpu)
            quota.used_agents = max(0, quota.used_agents - 1)

    async def create_workload(
        self,
        name: str,
        workload_type: WorkloadType,
        total_items: int,
        tenant_id: str = "default",
        item_cpu_cores: float = 1.0,
        item_memory_gb: float = 2.0,
        partition_strategy: PartitionStrategy = PartitionStrategy.LEAST_LOADED,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Workload:
        """Create a new distributed workload."""
        workload = Workload(
            name=name,
            workload_type=workload_type,
            tenant_id=tenant_id,
            total_items=total_items,
            item_cpu_cores=item_cpu_cores,
            item_memory_gb=item_memory_gb,
            partition_strategy=partition_strategy,
            payload=payload or {},
        )
        self._workloads[workload.id] = workload
        logger.info(f"Workload '{name}' created with {total_items} items for tenant '{tenant_id}'")
        return workload

    async def partition_workload(
        self,
        workload_id: str,
        num_partitions: int,
        available_worker_ids: List[str],
    ) -> List[WorkloadPartition]:
        """Partition a workload and assign to workers."""
        workload = self._workloads.get(workload_id)
        if not workload:
            raise ValueError(f"Workload {workload_id} not found")

        num_partitions = min(num_partitions, workload.total_items)
        items_per_partition = workload.total_items // num_partitions
        partitions = []

        for i in range(num_partitions):
            start = i * items_per_partition
            end = start + items_per_partition if i < num_partitions - 1 else workload.total_items
            worker_id = available_worker_ids[i % len(available_worker_ids)] if available_worker_ids else ""

            partition = WorkloadPartition(
                workload_id=workload_id,
                partition_index=i,
                total_partitions=num_partitions,
                data_range_start=start,
                data_range_end=end,
                assigned_worker_id=worker_id,
                status="assigned",
            )
            partitions.append(partition)

        workload.partitions = partitions
        workload.status = "partitioned"
        logger.info(f"Workload {workload_id} partitioned into {num_partitions} parts")
        return partitions

    async def complete_partition(
        self,
        workload_id: str,
        partition_id: str,
        result: Optional[Dict[str, Any]] = None,
    ) -> Workload:
        """Mark a partition as completed and check if workload is done."""
        workload = self._workloads.get(workload_id)
        if not workload:
            raise ValueError(f"Workload {workload_id} not found")

        partition = next((p for p in workload.partitions if p.id == partition_id), None)
        if not partition:
            raise ValueError(f"Partition {partition_id} not found in workload {workload_id}")

        partition.status = "completed"
        partition.result = result or {}

        if workload.progress >= 1.0:
            workload.status = "completed"
            workload.completed_at = datetime.now(timezone.utc)
            logger.info(f"Workload {workload_id} fully completed")
        return workload

    async def get_workload(self, workload_id: str) -> Optional[Workload]:
        return self._workloads.get(workload_id)

    async def list_workloads(
        self,
        tenant_id: Optional[str] = None,
        workload_type: Optional[WorkloadType] = None,
        status: Optional[str] = None,
    ) -> List[Workload]:
        workloads = list(self._workloads.values())
        if tenant_id:
            workloads = [w for w in workloads if w.tenant_id == tenant_id]
        if workload_type:
            workloads = [w for w in workloads if w.workload_type == workload_type]
        if status:
            workloads = [w for w in workloads if w.status == status]
        return workloads

    async def get_quota_summary(self) -> Dict[str, Any]:
        """Summary of resource usage across all tenants."""
        return {
            "tenant_count": len(self._quotas),
            "quotas": [q.to_dict() for q in self._quotas.values()],
            "total_workloads": len(self._workloads),
            "active_workloads": sum(1 for w in self._workloads.values() if w.status not in ("completed", "failed")),
        }
