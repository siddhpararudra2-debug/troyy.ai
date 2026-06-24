"""
Resource Manager for Portfolio Module
Manages resource allocations.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Manages resource allocations for projects/programs.
    """

    def __init__(self):
        self._allocations: List[Dict[str, Any]] = []

    async def allocate_resource(
        self,
        resource_id: str,
        project_id: str,
        role: str,
    ) -> Dict[str, Any]:
        allocation = {
            "id": str(uuid.uuid4()),
            "resource_id": resource_id,
            "project_id": project_id,
            "role": role,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._allocations.append(allocation)
        return allocation
