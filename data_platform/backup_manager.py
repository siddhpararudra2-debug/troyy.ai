"""
Sprint 12 — Backup Manager
Scheduled backups, point-in-time recovery, backup verification, and disaster recovery support.
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


class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(str, Enum):
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"
    EXPIRED = "expired"


class BackupTarget(str, Enum):
    DATABASE = "database"
    OBJECT_STORAGE = "object_storage"
    CONFIGURATION = "configuration"
    FULL_SYSTEM = "full_system"
    VECTOR_DB = "vector_db"


@dataclass
class BackupRecord:
    """Tracks a backup operation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    backup_type: BackupType = BackupType.FULL
    target: BackupTarget = BackupTarget.DATABASE
    status: BackupStatus = BackupStatus.SCHEDULED
    source_location: str = ""
    destination_bucket: str = ""
    destination_key: str = ""
    size_bytes: int = 0
    checksum: str = ""
    tenant_id: str = "default"
    retention_days: int = 30
    encrypted: bool = True
    verified: bool = False
    schedule_id: Optional[str] = None
    parent_backup_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "backup_type": self.backup_type.value,
            "target": self.target.value,
            "status": self.status.value,
            "source_location": self.source_location,
            "destination_bucket": self.destination_bucket,
            "destination_key": self.destination_key,
            "size_gb": round(self.size_bytes / 1_073_741_824, 6),
            "checksum": self.checksum,
            "tenant_id": self.tenant_id,
            "retention_days": self.retention_days,
            "encrypted": self.encrypted,
            "verified": self.verified,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "error_message": self.error_message,
        }


@dataclass
class BackupSchedule:
    """Defines a recurring backup schedule."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    target: BackupTarget = BackupTarget.DATABASE
    backup_type: BackupType = BackupType.INCREMENTAL
    cron_expression: str = "0 2 * * *"  # 2am daily
    destination_bucket: str = ""
    retention_days: int = 30
    enabled: bool = True
    tenant_id: str = "default"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "target": self.target.value,
            "backup_type": self.backup_type.value,
            "cron_expression": self.cron_expression,
            "destination_bucket": self.destination_bucket,
            "retention_days": self.retention_days,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
        }


class BackupManager:
    """
    Manages scheduled backups, point-in-time recovery, and backup verification.
    """

    def __init__(self):
        self._backups: Dict[str, BackupRecord] = {}
        self._schedules: Dict[str, BackupSchedule] = {}
        self._pitr_checkpoints: Dict[str, List[Dict[str, Any]]] = {}  # tenant -> checkpoints

    async def create_schedule(
        self,
        name: str,
        target: BackupTarget,
        destination_bucket: str,
        backup_type: BackupType = BackupType.INCREMENTAL,
        cron_expression: str = "0 2 * * *",
        retention_days: int = 30,
        tenant_id: str = "default",
    ) -> BackupSchedule:
        """Create a recurring backup schedule."""
        schedule = BackupSchedule(
            name=name,
            target=target,
            backup_type=backup_type,
            cron_expression=cron_expression,
            destination_bucket=destination_bucket,
            retention_days=retention_days,
            tenant_id=tenant_id,
            next_run=datetime.now(timezone.utc) + timedelta(hours=2),
        )
        self._schedules[schedule.id] = schedule
        logger.info(f"Backup schedule '{name}' created (cron: {cron_expression})")
        return schedule

    async def run_backup(
        self,
        name: str,
        target: BackupTarget,
        source_location: str,
        destination_bucket: str,
        backup_type: BackupType = BackupType.FULL,
        tenant_id: str = "default",
        retention_days: int = 30,
        schedule_id: Optional[str] = None,
        parent_backup_id: Optional[str] = None,
        size_bytes: Optional[int] = None,
    ) -> BackupRecord:
        """Execute a backup operation."""
        backup = BackupRecord(
            name=name,
            backup_type=backup_type,
            target=target,
            status=BackupStatus.RUNNING,
            source_location=source_location,
            destination_bucket=destination_bucket,
            destination_key=f"backups/{tenant_id}/{target.value}/{datetime.now(timezone.utc).strftime('%Y/%m/%d')}/{name}.bak",
            size_bytes=size_bytes or (10 * 1_073_741_824),  # Default 10GB
            encrypted=True,
            tenant_id=tenant_id,
            retention_days=retention_days,
            schedule_id=schedule_id,
            parent_backup_id=parent_backup_id,
            started_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=retention_days),
        )

        await asyncio.sleep(0)
        backup.status = BackupStatus.COMPLETED
        backup.completed_at = datetime.now(timezone.utc)
        backup.checksum = f"sha256:{uuid.uuid4().hex}"
        self._backups[backup.id] = backup

        # Record PITR checkpoint
        if tenant_id not in self._pitr_checkpoints:
            self._pitr_checkpoints[tenant_id] = []
        self._pitr_checkpoints[tenant_id].append({
            "backup_id": backup.id,
            "timestamp": backup.completed_at.isoformat(),
            "target": target.value,
        })

        logger.info(f"Backup '{name}' [{backup.id}] completed ({backup.size_bytes // 1_073_741_824}GB)")
        return backup

    async def verify_backup(self, backup_id: str) -> Dict[str, Any]:
        """Verify backup integrity via checksum validation."""
        backup = self._backups.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")

        # Simulate verification
        await asyncio.sleep(0)
        verification_passed = backup.checksum.startswith("sha256:")
        backup.verified = verification_passed
        if verification_passed:
            backup.status = BackupStatus.VERIFIED

        return {
            "backup_id": backup_id,
            "verified": verification_passed,
            "checksum": backup.checksum,
            "size_gb": round(backup.size_bytes / 1_073_741_824, 3),
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

    async def restore_backup(
        self,
        backup_id: str,
        target_location: str,
        tenant_id: str = "default",
    ) -> Dict[str, Any]:
        """Restore from a backup."""
        backup = self._backups.get(backup_id)
        if not backup:
            raise ValueError(f"Backup {backup_id} not found")

        restore_id = str(uuid.uuid4())
        await asyncio.sleep(0)

        return {
            "restore_id": restore_id,
            "backup_id": backup_id,
            "backup_name": backup.name,
            "target_location": target_location,
            "restored_size_gb": round(backup.size_bytes / 1_073_741_824, 3),
            "status": "completed",
            "restored_at": datetime.now(timezone.utc).isoformat(),
        }

    async def point_in_time_restore(
        self,
        tenant_id: str,
        target_timestamp: datetime,
    ) -> Dict[str, Any]:
        """Find the closest backup before target_timestamp for PITR."""
        checkpoints = self._pitr_checkpoints.get(tenant_id, [])
        eligible = [
            c for c in checkpoints
            if datetime.fromisoformat(c["timestamp"]) <= target_timestamp
        ]
        if not eligible:
            raise ValueError(f"No backup available before {target_timestamp.isoformat()}")

        best = max(eligible, key=lambda c: c["timestamp"])
        backup = self._backups.get(best["backup_id"])

        return {
            "pitr_request_timestamp": target_timestamp.isoformat(),
            "selected_backup_id": best["backup_id"],
            "selected_backup_timestamp": best["timestamp"],
            "backup_name": backup.name if backup else "unknown",
            "status": "restore_initiated",
            "estimated_recovery_time_minutes": 15,
        }

    async def expire_old_backups(self) -> Dict[str, Any]:
        """Expire and delete backups past their retention period."""
        now = datetime.now(timezone.utc)
        expired = [
            b for b in self._backups.values()
            if b.expires_at and b.expires_at < now and b.status != BackupStatus.EXPIRED
        ]
        for b in expired:
            b.status = BackupStatus.EXPIRED
        logger.info(f"Expired {len(expired)} backup(s)")
        return {"expired_count": len(expired), "checked_at": now.isoformat()}

    async def get_backup(self, backup_id: str) -> Optional[BackupRecord]:
        return self._backups.get(backup_id)

    async def list_backups(
        self,
        tenant_id: Optional[str] = None,
        target: Optional[BackupTarget] = None,
        status: Optional[BackupStatus] = None,
    ) -> List[BackupRecord]:
        backups = list(self._backups.values())
        if tenant_id:
            backups = [b for b in backups if b.tenant_id == tenant_id]
        if target:
            backups = [b for b in backups if b.target == target]
        if status:
            backups = [b for b in backups if b.status == status]
        return sorted(backups, key=lambda b: b.created_at, reverse=True)

    async def get_backup_summary(self) -> Dict[str, Any]:
        backups = list(self._backups.values())
        total_size = sum(b.size_bytes for b in backups if b.status in (BackupStatus.COMPLETED, BackupStatus.VERIFIED))
        return {
            "total_backups": len(backups),
            "completed": sum(1 for b in backups if b.status == BackupStatus.COMPLETED),
            "verified": sum(1 for b in backups if b.status == BackupStatus.VERIFIED),
            "failed": sum(1 for b in backups if b.status == BackupStatus.FAILED),
            "expired": sum(1 for b in backups if b.status == BackupStatus.EXPIRED),
            "total_backup_size_tb": round(total_size / 1_099_511_627_776, 6),
            "active_schedules": sum(1 for s in self._schedules.values() if s.enabled),
        }
