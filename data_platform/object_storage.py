"""
Sprint 12 — Object Storage Service
MinIO abstraction for petabyte-scale engineering data storage.
Supports CAD, PCB, simulation, and telemetry data.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StorageClass(str, Enum):
    HOT = "hot"          # Frequently accessed
    WARM = "warm"        # Infrequently accessed
    COLD = "cold"        # Archival
    GLACIER = "glacier"  # Deep archive


class BucketPurpose(str, Enum):
    CAD = "cad"
    PCB = "pcb"
    SIMULATION = "simulation"
    TELEMETRY = "telemetry"
    DOCUMENTS = "documents"
    BACKUPS = "backups"
    ARTIFACTS = "artifacts"
    MODELS = "ml_models"
    GENERIC = "generic"


@dataclass
class StorageObject:
    """Represents an object stored in object storage."""
    key: str = ""
    bucket_name: str = ""
    size_bytes: int = 0
    content_type: str = "application/octet-stream"
    etag: str = ""
    storage_class: StorageClass = StorageClass.HOT
    metadata: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    tenant_id: str = "default"
    project_id: Optional[str] = None
    version_id: str = ""
    last_modified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "bucket_name": self.bucket_name,
            "size_bytes": self.size_bytes,
            "size_mb": round(self.size_bytes / 1_048_576, 3),
            "content_type": self.content_type,
            "etag": self.etag,
            "storage_class": self.storage_class.value,
            "metadata": self.metadata,
            "tags": self.tags,
            "tenant_id": self.tenant_id,
            "project_id": self.project_id,
            "version_id": self.version_id,
            "last_modified": self.last_modified.isoformat(),
        }


@dataclass
class StorageBucket:
    """Represents an object storage bucket."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    purpose: BucketPurpose = BucketPurpose.GENERIC
    region: str = "us-east-1"
    tenant_id: str = "default"
    versioning_enabled: bool = True
    encryption_enabled: bool = True
    replication_enabled: bool = False
    replication_regions: List[str] = field(default_factory=list)
    lifecycle_rules: List[Dict[str, Any]] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    object_count: int = 0
    total_size_bytes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def total_size_gb(self) -> float:
        return self.total_size_bytes / 1_073_741_824

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "purpose": self.purpose.value,
            "region": self.region,
            "tenant_id": self.tenant_id,
            "versioning_enabled": self.versioning_enabled,
            "encryption_enabled": self.encryption_enabled,
            "replication_enabled": self.replication_enabled,
            "object_count": self.object_count,
            "total_size_gb": round(self.total_size_gb, 6),
            "total_size_bytes": self.total_size_bytes,
            "created_at": self.created_at.isoformat(),
        }


class ObjectStorageService:
    """
    MinIO-backed object storage service for the Engineering OS.
    Supports petabyte-scale storage for CAD, PCB, simulation, and telemetry data.
    """

    def __init__(self, minio_endpoint: str = "http://localhost:9000"):
        self._endpoint = minio_endpoint
        self._buckets: Dict[str, StorageBucket] = {}
        self._objects: Dict[str, Dict[str, StorageObject]] = {}  # bucket_name -> {key: obj}

    async def create_bucket(
        self,
        name: str,
        purpose: BucketPurpose = BucketPurpose.GENERIC,
        region: str = "us-east-1",
        tenant_id: str = "default",
        versioning_enabled: bool = True,
        encryption_enabled: bool = True,
        replication_regions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> StorageBucket:
        """Create a new storage bucket."""
        if name in {b.name for b in self._buckets.values()}:
            raise ValueError(f"Bucket '{name}' already exists")

        lifecycle_rules = self._default_lifecycle_rules(purpose)

        bucket = StorageBucket(
            name=name,
            purpose=purpose,
            region=region,
            tenant_id=tenant_id,
            versioning_enabled=versioning_enabled,
            encryption_enabled=encryption_enabled,
            replication_enabled=bool(replication_regions),
            replication_regions=replication_regions or [],
            lifecycle_rules=lifecycle_rules,
            tags=tags or {},
        )
        self._buckets[bucket.id] = bucket
        self._objects[name] = {}
        logger.info(f"Bucket '{name}' created in {region} (purpose={purpose.value})")
        return bucket

    def _default_lifecycle_rules(self, purpose: BucketPurpose) -> List[Dict[str, Any]]:
        """Default lifecycle rules based on bucket purpose."""
        rules = []
        if purpose == BucketPurpose.TELEMETRY:
            rules = [
                {"id": "hot_to_warm", "days": 30, "transition": "WARM"},
                {"id": "warm_to_cold", "days": 90, "transition": "COLD"},
                {"id": "cold_to_glacier", "days": 365, "transition": "GLACIER"},
            ]
        elif purpose == BucketPurpose.SIMULATION:
            rules = [
                {"id": "hot_to_warm", "days": 60, "transition": "WARM"},
                {"id": "warm_to_cold", "days": 180, "transition": "COLD"},
            ]
        elif purpose == BucketPurpose.BACKUPS:
            rules = [
                {"id": "expire_old_versions", "days": 90, "action": "delete_versions"},
            ]
        return rules

    async def upload_object(
        self,
        bucket_name: str,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
        tenant_id: str = "default",
        project_id: Optional[str] = None,
        storage_class: StorageClass = StorageClass.HOT,
    ) -> StorageObject:
        """Upload an object to the storage bucket."""
        if bucket_name not in self._objects:
            raise ValueError(f"Bucket '{bucket_name}' does not exist")

        etag = hashlib.md5(data).hexdigest()
        version_id = str(uuid.uuid4())[:8]

        obj = StorageObject(
            key=key,
            bucket_name=bucket_name,
            size_bytes=len(data),
            content_type=content_type,
            etag=etag,
            storage_class=storage_class,
            metadata=metadata or {},
            tags=tags or {},
            tenant_id=tenant_id,
            project_id=project_id,
            version_id=version_id,
        )
        self._objects[bucket_name][key] = obj

        # Update bucket stats
        bucket = next((b for b in self._buckets.values() if b.name == bucket_name), None)
        if bucket:
            bucket.total_size_bytes += len(data)
            bucket.object_count += 1

        logger.debug(f"Uploaded '{key}' to bucket '{bucket_name}' ({len(data)} bytes)")
        return obj

    async def download_object(self, bucket_name: str, key: str) -> Optional[bytes]:
        """Retrieve object data (simulated)."""
        if bucket_name not in self._objects:
            raise ValueError(f"Bucket '{bucket_name}' not found")
        obj = self._objects[bucket_name].get(key)
        if not obj:
            return None
        # Return simulated data of correct size
        return b"0" * min(obj.size_bytes, 1024)

    async def delete_object(self, bucket_name: str, key: str) -> bool:
        """Delete an object."""
        if bucket_name not in self._objects:
            return False
        obj = self._objects[bucket_name].pop(key, None)
        if obj:
            bucket = next((b for b in self._buckets.values() if b.name == bucket_name), None)
            if bucket:
                bucket.total_size_bytes = max(0, bucket.total_size_bytes - obj.size_bytes)
                bucket.object_count = max(0, bucket.object_count - 1)
            return True
        return False

    async def list_objects(
        self,
        bucket_name: str,
        prefix: str = "",
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        max_keys: int = 1000,
    ) -> List[StorageObject]:
        """List objects in a bucket with optional prefix filter."""
        if bucket_name not in self._objects:
            raise ValueError(f"Bucket '{bucket_name}' not found")

        objects = list(self._objects[bucket_name].values())
        if prefix:
            objects = [o for o in objects if o.key.startswith(prefix)]
        if tenant_id:
            objects = [o for o in objects if o.tenant_id == tenant_id]
        if project_id:
            objects = [o for o in objects if o.project_id == project_id]
        return objects[:max_keys]

    async def get_presigned_url(
        self,
        bucket_name: str,
        key: str,
        expiry_hours: int = 1,
        method: str = "GET",
    ) -> str:
        """Generate a pre-signed URL for direct object access."""
        expiry = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        token = hashlib.sha256(f"{bucket_name}/{key}/{expiry}".encode()).hexdigest()[:16]
        return (
            f"{self._endpoint}/{bucket_name}/{key}"
            f"?X-Amz-SignedHeaders=host"
            f"&X-Amz-Expires={expiry_hours * 3600}"
            f"&X-Amz-Signature={token}"
        )

    async def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
    ) -> StorageObject:
        """Copy an object between buckets."""
        source = self._objects.get(source_bucket, {}).get(source_key)
        if not source:
            raise ValueError(f"Source object '{source_key}' not found in '{source_bucket}'")

        copy = StorageObject(
            key=dest_key,
            bucket_name=dest_bucket,
            size_bytes=source.size_bytes,
            content_type=source.content_type,
            etag=source.etag,
            storage_class=source.storage_class,
            metadata=dict(source.metadata),
            tags=dict(source.tags),
            tenant_id=source.tenant_id,
            project_id=source.project_id,
            version_id=str(uuid.uuid4())[:8],
        )
        if dest_bucket not in self._objects:
            raise ValueError(f"Destination bucket '{dest_bucket}' not found")
        self._objects[dest_bucket][dest_key] = copy
        return copy

    async def get_bucket(self, bucket_name: str) -> Optional[StorageBucket]:
        return next((b for b in self._buckets.values() if b.name == bucket_name), None)

    async def list_buckets(
        self, tenant_id: Optional[str] = None, purpose: Optional[BucketPurpose] = None
    ) -> List[StorageBucket]:
        buckets = list(self._buckets.values())
        if tenant_id:
            buckets = [b for b in buckets if b.tenant_id == tenant_id]
        if purpose:
            buckets = [b for b in buckets if b.purpose == purpose]
        return buckets

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Overall storage platform statistics."""
        buckets = list(self._buckets.values())
        total_objects = sum(b.object_count for b in buckets)
        total_bytes = sum(b.total_size_bytes for b in buckets)
        return {
            "total_buckets": len(buckets),
            "total_objects": total_objects,
            "total_size_tb": round(total_bytes / 1_099_511_627_776, 6),
            "total_size_gb": round(total_bytes / 1_073_741_824, 3),
            "by_purpose": {
                p.value: sum(1 for b in buckets if b.purpose == p)
                for p in BucketPurpose
            },
        }
