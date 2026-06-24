"""
Sprint 12 — Data Catalog
Metadata catalog with search, tagging, dataset versioning, and lineage tracking.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DatasetStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class DatasetType(str, Enum):
    CAD_MODEL = "cad_model"
    PCB_DESIGN = "pcb_design"
    SIMULATION_RESULT = "simulation_result"
    TELEMETRY = "telemetry"
    MESH = "mesh"
    POINT_CLOUD = "point_cloud"
    TRAINING_DATA = "training_data"
    REPORT = "report"
    GENERIC = "generic"


@dataclass
class DatasetVersion:
    """A version of a dataset."""
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version_number: str = "1.0.0"
    dataset_id: str = ""
    storage_location: str = ""
    size_bytes: int = 0
    checksum: str = ""
    change_log: str = ""
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "version_number": self.version_number,
            "storage_location": self.storage_location,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "change_log": self.change_log,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class LineageNode:
    """A node in the data lineage graph."""
    dataset_id: str = ""
    dataset_name: str = ""
    operation: str = ""  # e.g., "fea_simulation", "preprocessing", "aggregation"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DatasetEntry:
    """A dataset registered in the catalog."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    dataset_type: DatasetType = DatasetType.GENERIC
    status: DatasetStatus = DatasetStatus.DRAFT
    owner: str = ""
    tenant_id: str = "default"
    project_id: Optional[str] = None
    bucket_name: str = ""
    key_prefix: str = ""
    tags: List[str] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)
    schema: Dict[str, Any] = field(default_factory=dict)
    versions: List[DatasetVersion] = field(default_factory=list)
    lineage_parents: List[str] = field(default_factory=list)  # parent dataset IDs
    lineage_children: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def current_version(self) -> Optional[DatasetVersion]:
        return self.versions[-1] if self.versions else None

    @property
    def total_size_bytes(self) -> int:
        return sum(v.size_bytes for v in self.versions)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dataset_type": self.dataset_type.value,
            "status": self.status.value,
            "owner": self.owner,
            "tenant_id": self.tenant_id,
            "project_id": self.project_id,
            "bucket_name": self.bucket_name,
            "key_prefix": self.key_prefix,
            "tags": self.tags,
            "labels": self.labels,
            "version_count": len(self.versions),
            "current_version": self.current_version.to_dict() if self.current_version else None,
            "total_size_gb": round(self.total_size_bytes / 1_073_741_824, 6),
            "lineage_parents": self.lineage_parents,
            "lineage_children": self.lineage_children,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class DataCatalogService:
    """
    Engineering data catalog with metadata management, versioning, and lineage tracking.
    """

    def __init__(self):
        self._datasets: Dict[str, DatasetEntry] = {}

    async def register_dataset(
        self,
        name: str,
        dataset_type: DatasetType,
        owner: str,
        bucket_name: str,
        key_prefix: str = "",
        description: str = "",
        tenant_id: str = "default",
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        labels: Optional[Dict[str, str]] = None,
        schema: Optional[Dict[str, Any]] = None,
        parent_dataset_ids: Optional[List[str]] = None,
    ) -> DatasetEntry:
        """Register a new dataset in the catalog."""
        dataset = DatasetEntry(
            name=name,
            description=description,
            dataset_type=dataset_type,
            owner=owner,
            tenant_id=tenant_id,
            project_id=project_id,
            bucket_name=bucket_name,
            key_prefix=key_prefix,
            tags=tags or [],
            labels=labels or {},
            schema=schema or {},
            lineage_parents=parent_dataset_ids or [],
        )

        # Update parent lineage
        if parent_dataset_ids:
            for parent_id in parent_dataset_ids:
                parent = self._datasets.get(parent_id)
                if parent:
                    parent.lineage_children.append(dataset.id)

        self._datasets[dataset.id] = dataset
        logger.info(f"Dataset '{name}' registered in catalog [{dataset.id}]")
        return dataset

    async def add_version(
        self,
        dataset_id: str,
        storage_location: str,
        size_bytes: int,
        checksum: str = "",
        change_log: str = "",
        created_by: str = "system",
        version_override: Optional[str] = None,
    ) -> DatasetVersion:
        """Add a new version to an existing dataset."""
        dataset = self._datasets.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        # Auto-increment version
        if version_override:
            version_number = version_override
        else:
            parts = dataset.current_version.version_number.split(".") if dataset.current_version else ["0", "0", "0"]
            parts[-1] = str(int(parts[-1]) + 1)
            version_number = ".".join(parts)

        version = DatasetVersion(
            dataset_id=dataset_id,
            version_number=version_number,
            storage_location=storage_location,
            size_bytes=size_bytes,
            checksum=checksum,
            change_log=change_log,
            created_by=created_by,
        )
        dataset.versions.append(version)
        dataset.updated_at = datetime.now(timezone.utc)
        logger.info(f"Version {version_number} added to dataset '{dataset.name}'")
        return version

    async def publish_dataset(self, dataset_id: str) -> DatasetEntry:
        dataset = self._datasets.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        if not dataset.versions:
            raise ValueError("Cannot publish dataset with no versions")
        dataset.status = DatasetStatus.PUBLISHED
        dataset.updated_at = datetime.now(timezone.utc)
        return dataset

    async def deprecate_dataset(self, dataset_id: str) -> DatasetEntry:
        dataset = self._datasets.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")
        dataset.status = DatasetStatus.DEPRECATED
        dataset.updated_at = datetime.now(timezone.utc)
        return dataset

    async def search_datasets(
        self,
        query: str = "",
        dataset_type: Optional[DatasetType] = None,
        tags: Optional[List[str]] = None,
        status: Optional[DatasetStatus] = None,
        tenant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        owner: Optional[str] = None,
    ) -> List[DatasetEntry]:
        """Search datasets by text, tags, type, or ownership."""
        results = list(self._datasets.values())

        if query:
            ql = query.lower()
            results = [
                d for d in results
                if ql in d.name.lower() or ql in d.description.lower()
                or any(ql in t.lower() for t in d.tags)
            ]
        if dataset_type:
            results = [d for d in results if d.dataset_type == dataset_type]
        if tags:
            results = [d for d in results if any(t in d.tags for t in tags)]
        if status:
            results = [d for d in results if d.status == status]
        if tenant_id:
            results = [d for d in results if d.tenant_id == tenant_id]
        if project_id:
            results = [d for d in results if d.project_id == project_id]
        if owner:
            results = [d for d in results if d.owner == owner]

        # Update access counts
        for d in results:
            d.access_count += 1
            d.last_accessed = datetime.now(timezone.utc)

        return results

    async def get_lineage(self, dataset_id: str, depth: int = 3) -> Dict[str, Any]:
        """Retrieve full lineage graph for a dataset."""
        dataset = self._datasets.get(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        def build_lineage(did: str, current_depth: int) -> Dict[str, Any]:
            d = self._datasets.get(did)
            if not d or current_depth <= 0:
                return {"id": did, "name": "unknown"}
            return {
                "id": d.id,
                "name": d.name,
                "type": d.dataset_type.value,
                "status": d.status.value,
                "parents": [build_lineage(pid, current_depth - 1) for pid in d.lineage_parents],
                "children": [build_lineage(cid, current_depth - 1) for cid in d.lineage_children],
            }

        return build_lineage(dataset_id, depth)

    async def get_dataset(self, dataset_id: str) -> Optional[DatasetEntry]:
        return self._datasets.get(dataset_id)

    async def get_catalog_stats(self) -> Dict[str, Any]:
        datasets = list(self._datasets.values())
        total_size = sum(d.total_size_bytes for d in datasets)
        return {
            "total_datasets": len(datasets),
            "published": sum(1 for d in datasets if d.status == DatasetStatus.PUBLISHED),
            "by_type": {t.value: sum(1 for d in datasets if d.dataset_type == t) for t in DatasetType},
            "total_versions": sum(len(d.versions) for d in datasets),
            "total_size_tb": round(total_size / 1_099_511_627_776, 6),
        }
