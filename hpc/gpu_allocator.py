"""
Sprint 12 — GPU Allocator
GPU inventory, reservation, multi-GPU job partitioning, and MIG (Multi-Instance GPU) support.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class GPUModel(str, Enum):
    A100_80GB = "NVIDIA A100 80GB"
    A100_40GB = "NVIDIA A100 40GB"
    H100_80GB = "NVIDIA H100 80GB"
    V100_32GB = "NVIDIA V100 32GB"
    RTX4090 = "NVIDIA RTX 4090"
    L40S = "NVIDIA L40S"


class GPUState(str, Enum):
    FREE = "free"
    ALLOCATED = "allocated"
    RESERVED = "reserved"
    FAULTY = "faulty"
    MAINTENANCE = "maintenance"


@dataclass
class GPUResource:
    """Represents a single GPU device."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_index: int = 0
    model: GPUModel = GPUModel.A100_80GB
    memory_gb: float = 80.0
    state: GPUState = GPUState.FREE
    node_id: str = ""
    node_hostname: str = ""
    cluster_id: str = ""
    allocation_id: Optional[str] = None
    job_id: Optional[str] = None
    tenant_id: Optional[str] = None
    cuda_version: str = "12.3"
    driver_version: str = "545.23.08"
    utilization_gpu_pct: float = 0.0
    utilization_memory_pct: float = 0.0
    temperature_c: float = 35.0
    power_watts: float = 50.0
    max_power_watts: float = 400.0
    allocated_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_available(self) -> bool:
        return self.state == GPUState.FREE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "device_index": self.device_index,
            "model": self.model.value,
            "memory_gb": self.memory_gb,
            "state": self.state.value,
            "node_hostname": self.node_hostname,
            "cluster_id": self.cluster_id,
            "job_id": self.job_id,
            "tenant_id": self.tenant_id,
            "cuda_version": self.cuda_version,
            "utilization_gpu_pct": self.utilization_gpu_pct,
            "utilization_memory_pct": self.utilization_memory_pct,
            "temperature_c": self.temperature_c,
            "power_watts": self.power_watts,
            "allocated_at": self.allocated_at.isoformat() if self.allocated_at else None,
        }


@dataclass
class GPUAllocation:
    """Tracks a GPU resource allocation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str = ""
    tenant_id: str = "default"
    gpu_ids: List[str] = field(default_factory=list)
    gpu_count: int = 0
    model: GPUModel = GPUModel.A100_80GB
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    allocated_at: Optional[datetime] = None
    released_at: Optional[datetime] = None
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "tenant_id": self.tenant_id,
            "gpu_ids": self.gpu_ids,
            "gpu_count": self.gpu_count,
            "model": self.model.value,
            "status": self.status,
            "requested_at": self.requested_at.isoformat(),
            "allocated_at": self.allocated_at.isoformat() if self.allocated_at else None,
            "released_at": self.released_at.isoformat() if self.released_at else None,
        }


class GPUAllocator:
    """
    Manages GPU inventory, allocation, and multi-GPU job partitioning.
    Supports NVIDIA A100, H100, V100 GPU pools.
    """

    def __init__(self):
        self._gpus: Dict[str, GPUResource] = {}
        self._allocations: Dict[str, GPUAllocation] = {}

    async def register_gpu(
        self,
        node_id: str,
        node_hostname: str,
        cluster_id: str,
        device_index: int = 0,
        model: GPUModel = GPUModel.A100_80GB,
        cuda_version: str = "12.3",
        driver_version: str = "545.23.08",
    ) -> GPUResource:
        """Register a GPU device in the inventory."""
        memory_map = {
            GPUModel.A100_80GB: 80.0,
            GPUModel.A100_40GB: 40.0,
            GPUModel.H100_80GB: 80.0,
            GPUModel.V100_32GB: 32.0,
            GPUModel.RTX4090: 24.0,
            GPUModel.L40S: 48.0,
        }
        gpu = GPUResource(
            device_index=device_index,
            model=model,
            memory_gb=memory_map.get(model, 80.0),
            node_id=node_id,
            node_hostname=node_hostname,
            cluster_id=cluster_id,
            cuda_version=cuda_version,
            driver_version=driver_version,
        )
        self._gpus[gpu.id] = gpu
        logger.debug(f"GPU registered: {model.value} on {node_hostname} (device {device_index})")
        return gpu

    async def register_gpu_cluster(
        self,
        cluster_id: str,
        node_hostname_prefix: str,
        nodes: int,
        gpus_per_node: int = 8,
        model: GPUModel = GPUModel.A100_80GB,
    ) -> List[GPUResource]:
        """Bulk-register a GPU cluster."""
        all_gpus = []
        for node_i in range(nodes):
            hostname = f"{node_hostname_prefix}-{node_i+1:04d}"
            node_id = str(uuid.uuid4())
            for dev_i in range(gpus_per_node):
                gpu = await self.register_gpu(
                    node_id=node_id,
                    node_hostname=hostname,
                    cluster_id=cluster_id,
                    device_index=dev_i,
                    model=model,
                )
                all_gpus.append(gpu)
        logger.info(f"GPU cluster '{cluster_id}': {nodes} nodes x {gpus_per_node} GPUs = {len(all_gpus)} GPUs registered")
        return all_gpus

    async def allocate_gpus(
        self,
        job_id: str,
        gpu_count: int,
        tenant_id: str = "default",
        model_preference: Optional[GPUModel] = None,
        cluster_id: Optional[str] = None,
    ) -> GPUAllocation:
        """Allocate GPUs for a job. Returns allocation record."""
        available = [
            g for g in self._gpus.values()
            if g.is_available
            and (model_preference is None or g.model == model_preference)
            and (cluster_id is None or g.cluster_id == cluster_id)
        ]

        if len(available) < gpu_count:
            raise RuntimeError(
                f"Insufficient GPUs: need {gpu_count}, "
                f"only {len(available)} available"
                + (f" of model {model_preference.value}" if model_preference else "")
            )

        # Prefer co-located GPUs (same node) for multi-GPU jobs
        if gpu_count > 1:
            node_groups: Dict[str, List[GPUResource]] = {}
            for g in available:
                node_groups.setdefault(g.node_id, []).append(g)
            # Find a node with enough GPUs
            co_located = next(
                (gpus for gpus in node_groups.values() if len(gpus) >= gpu_count),
                None,
            )
            if co_located:
                selected = co_located[:gpu_count]
            else:
                selected = available[:gpu_count]
        else:
            selected = available[:gpu_count]

        allocation = GPUAllocation(
            job_id=job_id,
            tenant_id=tenant_id,
            gpu_ids=[g.id for g in selected],
            gpu_count=len(selected),
            model=selected[0].model,
            status="allocated",
            allocated_at=datetime.now(timezone.utc),
        )

        for gpu in selected:
            gpu.state = GPUState.ALLOCATED
            gpu.job_id = job_id
            gpu.tenant_id = tenant_id
            gpu.allocation_id = allocation.id
            gpu.allocated_at = allocation.allocated_at

        self._allocations[allocation.id] = allocation
        logger.info(f"Job {job_id}: {gpu_count} GPUs allocated (allocation {allocation.id})")
        return allocation

    async def release_gpus(self, allocation_id: str) -> GPUAllocation:
        """Release GPU allocation back to pool."""
        allocation = self._allocations.get(allocation_id)
        if not allocation:
            raise ValueError(f"Allocation {allocation_id} not found")

        for gpu_id in allocation.gpu_ids:
            gpu = self._gpus.get(gpu_id)
            if gpu:
                gpu.state = GPUState.FREE
                gpu.job_id = None
                gpu.tenant_id = None
                gpu.allocation_id = None
                gpu.utilization_gpu_pct = 0.0
                gpu.utilization_memory_pct = 0.0
                gpu.power_watts = 50.0

        allocation.status = "released"
        allocation.released_at = datetime.now(timezone.utc)
        logger.info(f"Allocation {allocation_id} released ({len(allocation.gpu_ids)} GPUs freed)")
        return allocation

    async def update_gpu_metrics(
        self,
        gpu_id: str,
        utilization_gpu_pct: float = 0.0,
        utilization_memory_pct: float = 0.0,
        temperature_c: float = 35.0,
        power_watts: float = 50.0,
    ) -> GPUResource:
        """Update real-time GPU telemetry."""
        gpu = self._gpus.get(gpu_id)
        if not gpu:
            raise ValueError(f"GPU {gpu_id} not found")
        gpu.utilization_gpu_pct = utilization_gpu_pct
        gpu.utilization_memory_pct = utilization_memory_pct
        gpu.temperature_c = temperature_c
        gpu.power_watts = power_watts
        return gpu

    async def get_gpu(self, gpu_id: str) -> Optional[GPUResource]:
        return self._gpus.get(gpu_id)

    async def list_gpus(
        self,
        cluster_id: Optional[str] = None,
        state: Optional[GPUState] = None,
        model: Optional[GPUModel] = None,
    ) -> List[GPUResource]:
        gpus = list(self._gpus.values())
        if cluster_id:
            gpus = [g for g in gpus if g.cluster_id == cluster_id]
        if state:
            gpus = [g for g in gpus if g.state == state]
        if model:
            gpus = [g for g in gpus if g.model == model]
        return gpus

    async def get_allocation(self, allocation_id: str) -> Optional[GPUAllocation]:
        return self._allocations.get(allocation_id)

    async def generate_gpu_report(self) -> Dict[str, Any]:
        """Generate GPU inventory and utilization report."""
        gpus = list(self._gpus.values())
        free = [g for g in gpus if g.state == GPUState.FREE]
        allocated = [g for g in gpus if g.state == GPUState.ALLOCATED]

        avg_util = sum(g.utilization_gpu_pct for g in allocated) / len(allocated) if allocated else 0.0
        avg_temp = sum(g.temperature_c for g in gpus) / len(gpus) if gpus else 0.0
        total_power = sum(g.power_watts for g in gpus)

        by_model = {}
        for g in gpus:
            by_model.setdefault(g.model.value, {"total": 0, "free": 0, "allocated": 0})
            by_model[g.model.value]["total"] += 1
            if g.state == GPUState.FREE:
                by_model[g.model.value]["free"] += 1
            elif g.state == GPUState.ALLOCATED:
                by_model[g.model.value]["allocated"] += 1

        return {
            "report_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "inventory": {
                "total_gpus": len(gpus),
                "free_gpus": len(free),
                "allocated_gpus": len(allocated),
                "allocation_rate": round(len(allocated) / len(gpus), 3) if gpus else 0.0,
            },
            "by_model": by_model,
            "performance": {
                "avg_gpu_utilization_pct": round(avg_util, 2),
                "avg_temperature_c": round(avg_temp, 2),
                "total_power_kw": round(total_power / 1000, 3),
            },
            "active_allocations": len([a for a in self._allocations.values() if a.status == "allocated"]),
        }
