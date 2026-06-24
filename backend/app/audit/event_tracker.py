"""
Event Tracker for Audit Module
Tracks system events for audit.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class EventTracker:
    """
    Tracks events (design changes, simulation runs, etc.) for audit.
    """

    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    async def track_event(
        self,
        event_type: str,
        user_id: str,
        data: Dict[str, Any],
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Track an event.
        """
        event = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "user_id": user_id,
            "data": data,
            "resource_id": resource_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._events.append(event)
        logger.info(f"Tracked event: {event_type} by user {user_id}")
        return event

    async def get_events(
        self,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get audit events (optionally filtered).
        """
        filtered = self._events
        if event_type:
            filtered = [e for e in filtered if e["type"] == event_type]
        if user_id:
            filtered = [e for e in filtered if e["user_id"] == user_id]
        if resource_id:
            filtered = [e for e in filtered if e["resource_id"] == resource_id]
        if tenant_id:
            filtered = [e for e in filtered if e["tenant_id"] == tenant_id]
        return filtered[-limit:]
