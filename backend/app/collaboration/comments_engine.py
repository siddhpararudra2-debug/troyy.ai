"""
Comments Engine for Collaboration Module
Handles comments and mentions.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CommentsEngine:
    """
    Manages comments on resources.
    """

    def __init__(self):
        self._comments: Dict[str, List[Dict[str, Any]]] = {}  # key: resource_id

    async def add_comment(
        self,
        resource_id: str,
        user_id: str,
        text: str,
        mentions: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Add a comment to a resource.
        """
        comment = {
            "id": str(uuid.uuid4()),
            "resource_id": resource_id,
            "user_id": user_id,
            "text": text,
            "mentions": mentions or [],
            "created_at": datetime.utcnow().isoformat(),
        }
        if resource_id not in self._comments:
            self._comments[resource_id] = []
        self._comments[resource_id].append(comment)
        logger.info(f"Added comment on {resource_id} by {user_id}")
        return comment

    async def get_comments(self, resource_id: str) -> List[Dict[str, Any]]:
        """
        Get comments for a resource.
        """
        return self._comments.get(resource_id, [])
