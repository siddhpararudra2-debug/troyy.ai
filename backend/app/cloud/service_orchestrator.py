"""
Service Orchestrator
Manages service discovery and service-to-service communication
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ServiceOrchestrator:
    """Orchestrates service discovery and health checks"""

    def __init__(self):
        self._services: Dict[str, Dict[str, Any]] = {}

    async def register_service(
        self,
        name: str,
        service_type: str,
        endpoint: str,
    ) -> Dict[str, Any]:
        """Register a service for discovery"""
        service_id = str(uuid.uuid4())
        service = {
            "id": service_id,
            "name": name,
            "type": service_type,
            "endpoint": endpoint,
            "status": "healthy",
            "registered_at": datetime.utcnow().isoformat(),
        }
        self._services[service_id] = service
        logger.info(f"Registered service {name} at {endpoint}")
        return service

    async def discover_service(self, name: str) -> Optional[Dict[str, Any]]:
        """Discover a registered service"""
        for service in self._services.values():
            if service["name"] == name and service["status"] == "healthy":
                return service
        return None
