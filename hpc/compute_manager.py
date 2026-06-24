"""
Sprint 12 — HPC Compute Manager
CPU and GPU cluster pool management for massively parallel simulations.
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


class NodeType(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    HIGH_MEMORY = "high_memory"
    FAT_NODE = "fat_node"


class NodeHealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


@dataclass
class ComputeNode:
    """An HPC compute node."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hostname: str = ""
    node_type: NodeType = NodeType.CPU
    cpu_cores: int = 32
    memory_gb: float = 128.0
    gpu_count: int = 0
    gpu_model: str = ""
    storage_tb: float = 1.0
    network_gbps: float = 25.0
    used_cpu_cores: int = 0
    used_memory_gb: float = 0.0
    used_gpu: int = 0
    health_status: NodeHealthStatus = NodeHealthStatus.HEALTHY
    cluster_id: str = ""
    partition: str = "compute"
    os_version: str = "RHEL 9.2"
    mpi_version: str = "OpenMPI 4.1"
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def available_cpu(self) -> int:
        return max(0, self.cpu_cores - self.used_cpu_cores)

    @property
    def available_memory_gb(self) -> float:
        return max(0.0, self.memory_gb - self.used_memory_gb)

    @property
    def available_gpu(self) -> int:
        return max(0, self.gpu_count - self.used_gpu)

    @property
    def utilization_score(self) -> float:
        cpu_util = self.used_cpu_cores / self.cpu_cores if self.cpu_cores > 0 else 0.0
        mem_util = self.used_memory_gb / self.memory_gb if self.memory_gb > 0 else 0.0
        return (cpu_util + mem_util) / 2.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hostname": self.hostname,
            "node_type": self.node_type.value,
            "cpu_cores": self.cpu_cores,
            "available_cpu": self.available_cpu,
            "memory_gb": self.memory_gb,
            "available_memory_gb": self.available_memory_gb,
            "gpu_count": self.gpu_count,
            "gpu_model": self.gpu_model,
            "available_gpu": self.available_gpu,
            "utilization_score": round(self.utilization_score, 3),
            "health_status": self.health_status.value,
            "partition": self.partition,
            "cluster_id": self.cluster_id,
            "network_gbps": self.network_gbps,
        }


class ComputeManager:
    """
    Manages CPU and GPU compute node pools for the HPC platform.
    Handles node allocation, health monitoring, and resource reporting.
    """

    def __init__(self):
        self._nodes: Dict[str, ComputeNode] = {}
        self._allocations: Dict[str, List[str]] = {}  # job_id -> node_ids

    async def provision_cpu_cluster(
        self,
        cluster_name: str,
        node_count: int,
        cpu_cores_per_node: int = 32,
        memory_gb_per_node: float = 128.0,
        storage_tb_per_node: float = 1.0,
        network_gbps: float = 25.0,
        partition: str = "compute",
    ) -> List[ComputeNode]:
        """Provision a CPU compute cluster."""
        nodes = []
        for i in range(node_count):
            node = ComputeNode(
                hostname=f"{cluster_name}-cpu-{i+1:04d}",
                node_type=NodeType.CPU,
                cpu_cores=cpu_cores_per_node,
                memory_gb=memory_gb_per_node,
                storage_tb=storage_tb_per_node,
                network_gbps=network_gbps,
                cluster_id=cluster_name,
                partition=partition,
            )
            self._nodes[node.id] = node
            nodes.append(node)
        logger.info(f"CPU cluster '{cluster_name}' provisioned: {node_count}x {cpu_cores_per_node}-core nodes")
        return nodes

    async def provision_gpu_cluster(
        self,
        cluster_name: str,
        node_count: int,
        gpu_per_node: int = 8,
        gpu_model: str = "NVIDIA A100 80GB",
        cpu_cores_per_node: int = 64,
        memory_gb_per_node: float = 512.0,
        network_gbps: float = 200.0,
    ) -> List[ComputeNode]:
        """Provision a GPU compute cluster."""
        nodes = []
        for i in range(node_count):
            node = ComputeNode(
                hostname=f"{cluster_name}-gpu-{i+1:04d}",
                node_type=NodeType.GPU,
                cpu_cores=cpu_cores_per_node,
                memory_gb=memory_gb_per_node,
                gpu_count=gpu_per_node,
                gpu_model=gpu_model,
                network_gbps=network_gbps,
                cluster_id=cluster_name,
                partition="gpu",
            )
            self._nodes[node.id] = node
            nodes.append(node)
        logger.info(f"GPU cluster '{cluster_name}' provisioned: {node_count}x {gpu_per_node}x {gpu_model}")
        return nodes

    async def allocate_nodes(
        self,
        job_id: str,
        required_nodes: int,
        required_cpu_per_node: int,
        required_memory_gb_per_node: float,
        required_gpu_per_node: int = 0,
        partition: str = "compute",
    ) -> List[ComputeNode]:
        """Allocate nodes for an HPC job."""
        available = [
            n for n in self._nodes.values()
            if n.partition == partition
            and n.health_status == NodeHealthStatus.HEALTHY
            and n.available_cpu >= required_cpu_per_node
            and n.available_memory_gb >= required_memory_gb_per_node
            and n.available_gpu >= required_gpu_per_node
        ]

        if len(available) < required_nodes:
            raise RuntimeError(
                f"Insufficient nodes: need {required_nodes}, "
                f"only {len(available)} available in partition '{partition}'"
            )

        # Sort by least utilized (best-fit)
        available.sort(key=lambda n: n.utilization_score)
        selected = available[:required_nodes]

        for node in selected:
            node.used_cpu_cores += required_cpu_per_node
            node.used_memory_gb += required_memory_gb_per_node
            node.used_gpu += required_gpu_per_node

        self._allocations[job_id] = [n.id for n in selected]
        logger.info(f"Job {job_id}: {required_nodes} nodes allocated from '{partition}'")
        return selected

    async def release_nodes(self, job_id: str) -> Dict[str, Any]:
        """Release nodes allocated to a job."""
        node_ids = self._allocations.pop(job_id, [])
        for node_id in node_ids:
            node = self._nodes.get(node_id)
            if node:
                node.used_cpu_cores = max(0, node.used_cpu_cores - (node.cpu_cores // 2))
                node.used_memory_gb = max(0.0, node.used_memory_gb - (node.memory_gb / 2))
        return {"job_id": job_id, "released_nodes": len(node_ids)}

    async def set_node_maintenance(self, node_id: str) -> ComputeNode:
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")
        node.health_status = NodeHealthStatus.MAINTENANCE
        return node

    async def restore_node(self, node_id: str) -> ComputeNode:
        node = self._nodes.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")
        node.health_status = NodeHealthStatus.HEALTHY
        return node

    async def get_node(self, node_id: str) -> Optional[ComputeNode]:
        return self._nodes.get(node_id)

    async def list_nodes(
        self,
        node_type: Optional[NodeType] = None,
        partition: Optional[str] = None,
        health_status: Optional[NodeHealthStatus] = None,
    ) -> List[ComputeNode]:
        nodes = list(self._nodes.values())
        if node_type:
            nodes = [n for n in nodes if n.node_type == node_type]
        if partition:
            nodes = [n for n in nodes if n.partition == partition]
        if health_status:
            nodes = [n for n in nodes if n.health_status == health_status]
        return nodes

    async def generate_resource_report(self) -> Dict[str, Any]:
        """Comprehensive resource utilization report."""
        nodes = list(self._nodes.values())
        cpu_nodes = [n for n in nodes if n.node_type == NodeType.CPU]
        gpu_nodes = [n for n in nodes if n.node_type == NodeType.GPU]

        total_cpu = sum(n.cpu_cores for n in nodes)
        used_cpu = sum(n.used_cpu_cores for n in nodes)
        total_gpu = sum(n.gpu_count for n in nodes)
        used_gpu = sum(n.used_gpu for n in nodes)
        total_mem = sum(n.memory_gb for n in nodes)
        used_mem = sum(n.used_memory_gb for n in nodes)

        return {
            "report_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cluster_summary": {
                "total_nodes": len(nodes),
                "cpu_nodes": len(cpu_nodes),
                "gpu_nodes": len(gpu_nodes),
                "healthy_nodes": sum(1 for n in nodes if n.health_status == NodeHealthStatus.HEALTHY),
                "active_allocations": len(self._allocations),
            },
            "cpu_utilization": {
                "total_cores": total_cpu,
                "used_cores": used_cpu,
                "utilization_pct": round(used_cpu / total_cpu * 100, 2) if total_cpu > 0 else 0,
            },
            "gpu_utilization": {
                "total_gpus": total_gpu,
                "used_gpus": used_gpu,
                "utilization_pct": round(used_gpu / total_gpu * 100, 2) if total_gpu > 0 else 0,
            },
            "memory_utilization": {
                "total_gb": total_mem,
                "used_gb": used_mem,
                "utilization_pct": round(used_mem / total_mem * 100, 2) if total_mem > 0 else 0,
            },
        }
