"""
Discussion Manager for Collaboration Module
Handles discussions about projects/designs.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class DiscussionManager:
    """
    Manages discussions and threads.
    """

    def __init__(self):
        self._discussions: Dict[str, List[Dict[str, Any]]] = {}  # key: resource_id

    async def start_discussion(
        self,
        resource_id: str,
        topic: str,
        user_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """
        Start a new discussion thread.
        """
        discussion = {
            "id": str(uuid.uuid4()),
            "resource_id": resource_id,
            "topic": topic,
            "started_by": user_id,
            "messages": [
                {
                    "user_id": user_id,
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "created_at": datetime.utcnow().isoformat(),
        }
        if resource_id not in self._discussions:
            self._discussions[resource_id] = []
        self._discussions[resource_id].append(discussion)
        return discussion
