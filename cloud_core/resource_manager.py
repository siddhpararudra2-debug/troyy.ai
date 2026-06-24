"""
Sprint 12 — Resource Manager (Cloud Core)
Unified resource tracking, quota enforcement, and cost allocation.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResourceType(str, Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"


@dataclass
class ResourceQuota:
    """Tenant/team resource quota."""
    tenant_id: str = ""
    team_name: str = ""
    cpu_cores: int = 100
    memory_gb: float = 500.0
    gpu_count: int = 4
    storage_tb: float = 10.0
    max_deployments: int = 50
    max_environments: int = 20
    used_cpu: int = 0
    used_memory_gb: float = 0.0
    used_gpu: int = 0
    used_storage_tb: float = 0.0

    @property
    def cpu_utilization(self) -> float:
        return self.used_cpu / self.cpu_cores if self.cpu_cores > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "team_name": self.team_name,
            "quotas": {
                "cpu_cores": self.cpu_cores,
                "memory_gb": self.memory_gb,
                "gpu": self.gpu_count,
                "storage_tb": self.storage_tb,
            },
            "used": {
                "cpu_cores": self.used_cpu,
                "memory_gb": self.used_memory_gb,
                "gpu": self.used_gpu,
                "storage_tb": self.used_storage_tb,
            },
            "utilization": {
                "cpu": round(self.cpu_utilization, 3),
            },
        }


@dataclass
class ResourceRecord:
    """A tracked cloud resource."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType = ResourceType.COMPUTE
    name: str = ""
    tenant_id: str = "default"
    team_name: str = ""
    region: str = "us-east-1"
    cost_per_hour: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "resource_type": self.resource_type.value,
            "name": self.name,
            "tenant_id": self.tenant_id,
            "region": self.region,
            "cost_per_hour": self.cost_per_hour,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }


class ResourceManager:
    """
    Unified resource manager with quota enforcement and cost tracking.
    """

    def __init__(self):
        self._resources: Dict[str, ResourceRecord] = {}
        self._quotas: Dict[str, ResourceQuota] = {}  # tenant_id -> quota

    async def register_resource(
        self,
        name: str,
        resource_type: ResourceType,
        tenant_id: str = "default",
        team_name: str = "",
        region: str = "us-east-1",
        cost_per_hour: float = 0.0,
        tags: Optional[Dict[str, str]] = None,
    ) -> ResourceRecord:
        """Register a cloud resource."""
        record = ResourceRecord(
            name=name,
            resource_type=resource_type,
            tenant_id=tenant_id,
            team_name=team_name,
            region=region,
            cost_per_hour=cost_per_hour,
            tags=tags or {},
        )
        self._resources[record.id] = record
        return record

    async def set_quota(
        self,
        tenant_id: str,
        cpu_cores: int = 100,
        memory_gb: float = 500.0,
        gpu_count: int = 4,
        storage_tb: float = 10.0,
        team_name: str = "",
    ) -> ResourceQuota:
        """Set resource quotas for a tenant."""
        quota = ResourceQuota(
            tenant_id=tenant_id,
            team_name=team_name,
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            gpu_count=gpu_count,
            storage_tb=storage_tb,
        )
        self._quotas[tenant_id] = quota
        return quota

    def check_quota(self, tenant_id: str, resource_type: ResourceType, amount: float) -> bool:
        """Check if a resource request is within quota."""
        quota = self._quotas.get(tenant_id)
        if not quota:
            return True  # No quota set = allow
        if resource_type == ResourceType.COMPUTE:
            return quota.used_cpu + amount <= quota.cpu_cores
        if resource_type == ResourceType.GPU:
            return quota.used_gpu + amount <= quota.gpu_count
        if resource_type == ResourceType.STORAGE:
            return quota.used_storage_tb + amount <= quota.storage_tb
        return True

    async def get_cost_report(self, tenant_id: str) -> Dict[str, Any]:
        """Generate cost report for a tenant."""
        resources = [r for r in self._resources.values() if r.tenant_id == tenant_id and r.is_active]
        total_hourly = sum(r.cost_per_hour for r in resources)
        return {
            "tenant_id": tenant_id,
            "total_resources": len(resources),
            "hourly_cost_usd": round(total_hourly, 4),
            "daily_cost_usd": round(total_hourly * 24, 2),
            "monthly_cost_usd": round(total_hourly * 24 * 30, 2),
            "by_type": {
                t.value: round(sum(r.cost_per_hour for r in resources if r.resource_type == t), 4)
                for t in ResourceType
            },
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def list_resources(
        self, tenant_id: Optional[str] = None, resource_type: Optional[ResourceType] = None
    ) -> List[ResourceRecord]:
        resources = list(self._resources.values())
        if tenant_id:
            resources = [r for r in resources if r.tenant_id == tenant_id]
        if resource_type:
            resources = [r for r in resources if r.resource_type == resource_type]
        return resources

    async def get_quota(self, tenant_id: str) -> Optional[ResourceQuota]:
        return self._quotas.get(tenant_id)

    def get_platform_summary(self) -> Dict[str, Any]:
        resources = list(self._resources.values())
        total_cost = sum(r.cost_per_hour for r in resources if r.is_active)
        return {
            "total_resources": len(resources),
            "active_resources": sum(1 for r in resources if r.is_active),
            "total_hourly_cost_usd": round(total_cost, 4),
            "total_monthly_cost_usd": round(total_cost * 24 * 30, 2),
            "tenants": len(self._quotas),
        }
