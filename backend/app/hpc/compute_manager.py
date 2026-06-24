"""
Compute Manager
Manages CPU/GPU compute resources
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ComputeManager:
    """Manages compute resource allocation"""

    def __init__(self):
        self._resources: Dict[str, Dict[str, Any]] = {}

    async def register_compute_node(
        self,
        node_id: str,
        node_type: str,
        cpu_cores: int,
        memory_gb: float,
    ) -> Dict[str, Any]:
        """Register a compute node"""
        node = {
            "id": node_id,
            "type": node_type,
            "cpu_cores": cpu_cores,
            "memory_gb": memory_gb,
            "status": "available",
            "registered_at": datetime.utcnow().isoformat(),
        }
        self._resources[node_id] = node
        logger.info(f"Registered compute node {node_id}")
        return node
