"""
Audit Engine for Audit Module
Central audit orchestration engine.
"""
import logging
from typing import Dict, Any, Optional
from app.audit.event_tracker import EventTracker
from app.audit.compliance_logger import ComplianceLogger

logger = logging.getLogger(__name__)


class AuditEngine:
    """
    Central audit engine that provides a unified interface.
    """

    def __init__(
        self,
        event_tracker: Optional[EventTracker] = None,
        compliance_logger: Optional[ComplianceLogger] = None,
    ):
        self.event_tracker = event_tracker or EventTracker()
        self.compliance_logger = compliance_logger or ComplianceLogger()

    async def get_audit_trail(
        self,
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get an audit trail for a specific resource.
        """
        events = await self.event_tracker.get_events(
            resource_id=resource_id, tenant_id=tenant_id, limit=limit
        )
        return {
            "resource_id": resource_id,
            "tenant_id": tenant_id,
            "events": events,
        }
