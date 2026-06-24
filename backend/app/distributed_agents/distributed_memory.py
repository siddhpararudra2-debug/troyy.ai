"""
Distributed Memory
Manages distributed shared memory for agents
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DistributedMemory:
    """Distributed key-value store for agents"""

    def __init__(self):
        self._memory: Dict[str, Dict[str, Any]] = {}

    async def put(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Store a value in distributed memory"""
        self._memory[key] = {
            "key": key,
            "value": value,
            "ttl": ttl_seconds,
            "stored_at": datetime.utcnow().isoformat(),
        }
        logger.debug(f"Stored key: {key}")
        return {"status": "stored", "key": key}

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from distributed memory"""
        entry = self._memory.get(key)
        if entry:
            return entry["value"]
        return None

    async def delete(self, key: str) -> Dict[str, Any]:
        """Delete a key from memory"""
        if key in self._memory:
            del self._memory[key]
        return {"status": "deleted", "key": key}
