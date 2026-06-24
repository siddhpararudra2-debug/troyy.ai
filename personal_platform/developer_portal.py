"""
Sprint 12 — Developer Portal
Internal developer platform with self-service infrastructure and service catalog.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServiceCatalogCategory(str, Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    MESSAGING = "messaging"
    SECURITY = "security"
    MONITORING = "monitoring"
    AI_ML = "ai_ml"


@dataclass
class CatalogItem:
    """A service catalog item available for self-service provisioning."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: ServiceCatalogCategory = ServiceCatalogCategory.COMPUTE
    version: str = "1.0.0"
    provisioning_time_minutes: int = 1
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_available: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "version": self.version,
            "provisioning_time_minutes": self.provisioning_time_minutes,
            "parameters": self.parameters,
            "tags": self.tags,
            "is_available": self.is_available,
        }


@dataclass
class ProvisioningRequest:
    """A self-service provisioning request."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    catalog_item_id: str = ""
    catalog_item_name: str = ""
    requested_by: str = "local_user"
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    provisioned_resource_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "catalog_item_name": self.catalog_item_name,
            "requested_by": self.requested_by,
            "parameters": self.parameters,
            "status": self.status,
            "provisioned_resource_id": self.provisioned_resource_id,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class DeveloperPortal:
    """
    Developer portal providing self-service docker compose resources for the single workstation.
    """

    def __init__(self):
        self._catalog: Dict[str, CatalogItem] = {}
        self._requests: Dict[str, ProvisioningRequest] = {}
        self._initialize_catalog()

    def _initialize_catalog(self) -> None:
        """Populate with default local catalog items."""
        items = [
            ("Local PostgreSQL Instance", "Provision a PostgreSQL container", ServiceCatalogCategory.DATABASE, 1),
            ("Local Redis Cache", "Provision a Redis container", ServiceCatalogCategory.DATABASE, 1),
            ("MinIO Storage Bucket", "Local object storage bucket", ServiceCatalogCategory.STORAGE, 1),
            ("NATS Subject/Stream", "Local messaging subject", ServiceCatalogCategory.MESSAGING, 1),
            ("Neo4j Database", "Local graph database for knowledge representation", ServiceCatalogCategory.DATABASE, 1),
            ("Local TLS Certificate", "Self-signed SSL/TLS certificate", ServiceCatalogCategory.SECURITY, 1),
            ("Grafana Stack", "Local monitoring dashboard", ServiceCatalogCategory.MONITORING, 1),
            ("Ollama Container", "Run open-source local LLMs", ServiceCatalogCategory.AI_ML, 1),
        ]
        for name, desc, cat, time_mins in items:
            item = CatalogItem(name=name, description=desc, category=cat, provisioning_time_minutes=time_mins)
            self._catalog[item.id] = item

    async def search_catalog(
        self,
        query: str = "",
        category: Optional[ServiceCatalogCategory] = None,
        available_only: bool = True,
    ) -> List[CatalogItem]:
        """Search the service catalog."""
        items = list(self._catalog.values())
        if available_only:
            items = [i for i in items if i.is_available]
        if category:
            items = [i for i in items if i.category == category]
        if query:
            ql = query.lower()
            items = [i for i in items if ql in i.name.lower() or ql in i.description.lower()]
        return items

    async def request_provisioning(
        self,
        catalog_item_id: str,
        requested_by: str = "local_user",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> ProvisioningRequest:
        """Submit a self-service provisioning request."""
        item = self._catalog.get(catalog_item_id)
        if not item:
            raise ValueError(f"Catalog item {catalog_item_id} not found")

        request = ProvisioningRequest(
            catalog_item_id=catalog_item_id,
            catalog_item_name=item.name,
            requested_by=requested_by,
            parameters=parameters or {},
            status="approved",
        )
        self._requests[request.id] = request

        # Auto-provision
        request.provisioned_resource_id = f"docker_{uuid.uuid4().hex[:12]}"
        request.status = "completed"
        request.completed_at = datetime.now(timezone.utc)

        logger.info(f"Provisioned '{item.name}' for {requested_by}")
        return request

    async def list_provisioning_requests(
        self, status: Optional[str] = None
    ) -> List[ProvisioningRequest]:
        requests = list(self._requests.values())
        if status:
            requests = [r for r in requests if r.status == status]
        return requests

    def get_portal_stats(self) -> Dict[str, Any]:
        return {
            "catalog_items": len(self._catalog),
            "total_requests": len(self._requests),
            "completed_requests": sum(1 for r in self._requests.values() if r.status == "completed"),
        }
