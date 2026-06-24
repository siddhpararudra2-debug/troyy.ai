"""
Sprint 12 — Archive Manager
Cold storage tiering, automated archival workflows, and lifecycle policy management.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ArchiveTier(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    GLACIER = "glacier"


class ArchiveStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RESTORING = "restoring"
    RESTORED = "restored"


@dataclass
class ArchiveJob:
    """Tracks an archive or restore operation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    bucket_name: str = ""
    key_prefix: str = ""
    source_tier: ArchiveTier = ArchiveTier.HOT
    target_tier: ArchiveTier = ArchiveTier.COLD
    status: ArchiveStatus = ArchiveStatus.PENDING
    object_count: int = 0
    total_size_bytes: int = 0
    tenant_id: str = "default"
    reason: str = ""
    initiated_by: str = "lifecycle_policy"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bucket_name": self.bucket_name,
            "key_prefix": self.key_prefix,
            "source_tier": self.source_tier.value,
            "target_tier": self.target_tier.value,
            "status": self.status.value,
            "object_count": self.object_count,
            "total_size_gb": round(self.total_size_bytes / 1_073_741_824, 6),
            "tenant_id": self.tenant_id,
            "reason": self.reason,
            "initiated_by": self.initiated_by,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class LifecyclePolicy:
    """Defines data lifecycle transitions."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    bucket_name: str = ""
    prefix: str = ""
    hot_to_warm_days: int = 30
    warm_to_cold_days: int = 90
    cold_to_glacier_days: int = 365
    glacier_expiry_days: Optional[int] = None  # None = keep forever
    enabled: bool = True
    tenant_id: str = "default"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "bucket_name": self.bucket_name,
            "prefix": self.prefix,
            "transitions": {
                "hot_to_warm_days": self.hot_to_warm_days,
                "warm_to_cold_days": self.warm_to_cold_days,
                "cold_to_glacier_days": self.cold_to_glacier_days,
                "glacier_expiry_days": self.glacier_expiry_days,
            },
            "enabled": self.enabled,
            "tenant_id": self.tenant_id,
        }


class ArchiveManager:
    """
    Manages cold storage tiering, lifecycle policies, and archival workflows.
    """

    def __init__(self):
        self._jobs: Dict[str, ArchiveJob] = {}
        self._policies: Dict[str, LifecyclePolicy] = {}
        self._tier_registry: Dict[str, ArchiveTier] = {}  # bucket/key -> current tier

    async def create_lifecycle_policy(
        self,
        name: str,
        bucket_name: str,
        prefix: str = "",
        hot_to_warm_days: int = 30,
        warm_to_cold_days: int = 90,
        cold_to_glacier_days: int = 365,
        glacier_expiry_days: Optional[int] = None,
        tenant_id: str = "default",
    ) -> LifecyclePolicy:
        """Create a data lifecycle policy for a bucket."""
        policy = LifecyclePolicy(
            name=name,
            bucket_name=bucket_name,
            prefix=prefix,
            hot_to_warm_days=hot_to_warm_days,
            warm_to_cold_days=warm_to_cold_days,
            cold_to_glacier_days=cold_to_glacier_days,
            glacier_expiry_days=glacier_expiry_days,
            tenant_id=tenant_id,
        )
        self._policies[policy.id] = policy
        logger.info(f"Lifecycle policy '{name}' created for bucket '{bucket_name}'")
        return policy

    async def archive_objects(
        self,
        bucket_name: str,
        key_prefix: str,
        target_tier: ArchiveTier,
        object_count: int = 0,
        total_size_bytes: int = 0,
        tenant_id: str = "default",
        reason: str = "manual",
        initiated_by: str = "user",
    ) -> ArchiveJob:
        """Archive objects to a specified tier."""
        job = ArchiveJob(
            bucket_name=bucket_name,
            key_prefix=key_prefix,
            source_tier=self._tier_registry.get(f"{bucket_name}/{key_prefix}", ArchiveTier.HOT),
            target_tier=target_tier,
            status=ArchiveStatus.IN_PROGRESS,
            object_count=object_count,
            total_size_bytes=total_size_bytes,
            tenant_id=tenant_id,
            reason=reason,
            initiated_by=initiated_by,
            started_at=datetime.now(timezone.utc),
        )
        self._jobs[job.id] = job

        # Simulate archival
        await asyncio.sleep(0)
        self._tier_registry[f"{bucket_name}/{key_prefix}"] = target_tier
        job.status = ArchiveStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)

        cost_savings = self._estimate_cost_savings(total_size_bytes, job.source_tier, target_tier)
        logger.info(
            f"Archive job {job.id}: {object_count} objects moved to {target_tier.value} "
            f"(est. savings: ${cost_savings:.2f}/month)"
        )
        return job

    def _estimate_cost_savings(
        self, size_bytes: int, source: ArchiveTier, target: ArchiveTier
    ) -> float:
        """Estimate monthly cost savings from tier transition."""
        # $/GB/month estimates
        tier_costs = {
            ArchiveTier.HOT: 0.023,
            ArchiveTier.WARM: 0.0125,
            ArchiveTier.COLD: 0.004,
            ArchiveTier.GLACIER: 0.00099,
        }
        size_gb = size_bytes / 1_073_741_824
        return max(0.0, (tier_costs[source] - tier_costs[target]) * size_gb)

    async def restore_from_archive(
        self,
        bucket_name: str,
        key_prefix: str,
        expedited: bool = False,
        tenant_id: str = "default",
    ) -> ArchiveJob:
        """Restore objects from archive tier."""
        current_tier = self._tier_registry.get(f"{bucket_name}/{key_prefix}", ArchiveTier.HOT)

        job = ArchiveJob(
            bucket_name=bucket_name,
            key_prefix=key_prefix,
            source_tier=current_tier,
            target_tier=ArchiveTier.HOT,
            status=ArchiveStatus.RESTORING,
            tenant_id=tenant_id,
            reason="user_restore",
            initiated_by="user",
            started_at=datetime.now(timezone.utc),
        )
        self._jobs[job.id] = job

        # Simulate restore time based on tier
        restore_hours = 1 if expedited else (4 if current_tier == ArchiveTier.COLD else 12)
        await asyncio.sleep(0)
        self._tier_registry[f"{bucket_name}/{key_prefix}"] = ArchiveTier.HOT
        job.status = ArchiveStatus.RESTORED
        job.completed_at = datetime.now(timezone.utc)
        logger.info(f"Restore job {job.id}: objects restored from {current_tier.value}")
        return job

    async def run_lifecycle_evaluation(self) -> Dict[str, Any]:
        """Evaluate all objects against lifecycle policies and create archive jobs."""
        archived_jobs = []
        for policy in self._policies.values():
            if not policy.enabled:
                continue
            # Simulate finding objects that need tiering
            now = datetime.now(timezone.utc)
            objects_to_warm = 50
            objects_to_cold = 20
            objects_to_glacier = 5

            if objects_to_warm > 0:
                job = await self.archive_objects(
                    bucket_name=policy.bucket_name,
                    key_prefix=f"{policy.prefix}warm/",
                    target_tier=ArchiveTier.WARM,
                    object_count=objects_to_warm,
                    total_size_bytes=objects_to_warm * 1_073_741_824,
                    initiated_by="lifecycle_policy",
                )
                archived_jobs.append(job.id)

        return {
            "policies_evaluated": len(self._policies),
            "archive_jobs_created": len(archived_jobs),
            "job_ids": archived_jobs,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_job(self, job_id: str) -> Optional[ArchiveJob]:
        return self._jobs.get(job_id)

    async def list_jobs(
        self,
        status: Optional[ArchiveStatus] = None,
        tenant_id: Optional[str] = None,
    ) -> List[ArchiveJob]:
        jobs = list(self._jobs.values())
        if status:
            jobs = [j for j in jobs if j.status == status]
        if tenant_id:
            jobs = [j for j in jobs if j.tenant_id == tenant_id]
        return jobs

    async def get_archive_summary(self) -> Dict[str, Any]:
        jobs = list(self._jobs.values())
        total_archived = sum(j.total_size_bytes for j in jobs if j.status == ArchiveStatus.COMPLETED)
        return {
            "total_archive_jobs": len(jobs),
            "completed_jobs": sum(1 for j in jobs if j.status == ArchiveStatus.COMPLETED),
            "total_archived_gb": round(total_archived / 1_073_741_824, 3),
            "active_policies": sum(1 for p in self._policies.values() if p.enabled),
            "tier_distribution": {tier.value: sum(1 for t in self._tier_registry.values() if t == tier) for tier in ArchiveTier},
        }
