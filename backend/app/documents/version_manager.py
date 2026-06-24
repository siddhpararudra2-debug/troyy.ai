"""
Version Manager for Documents Module
Manages document versioning.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class VersionManager:
    """
    Manages document versions.
    """

    def __init__(self):
        self._versions: Dict[str, List[Dict[str, Any]]] = {}  # key: doc_id, value: list of versions

    async def save_version(
        self,
        doc_id: str,
        version: int,
        content: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Save a new version of a document.
        """
        version_record = {
            "id": str(uuid.uuid4()),
            "doc_id": doc_id,
            "version": version,
            "content": content,
            "saved_by": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if doc_id not in self._versions:
            self._versions[doc_id] = []
        self._versions[doc_id].append(version_record)
        return version_record

    async def get_versions(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a document.
        """
        return self._versions.get(doc_id, [])
