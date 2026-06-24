"""
Event Router
Routes events to appropriate handlers
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class EventRouter:
    """Routes events to handlers"""

    def __init__(self):
        self._routes: Dict[str, str] = {}

    async def register_route(self, event_type: str, handler: str):
        """Register an event route"""
        self._routes[event_type] = handler
        logger.info(f"Registered route for event {event_type}")

    async def route_event(self, event: Dict[str, Any]) -> Optional[str]:
        """Route an event to its handler"""
        return self._routes.get(event.get("type"))
