"""
Logging Engine
Centralized logging
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LoggingEngine:
    """Centralized logging"""

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    async def log(
        self,
        level: str,
        message: str,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Log a message"""
        record = {
            "level": level,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._logs.append(record)
        return record
