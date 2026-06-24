"""
Document Manager for Documents Module
Manages documents.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DocumentManager:
    """
    Manages engineering documents (reports, drawings, requirements, procedures).
    """

    def __init__(self):
        self._documents: Dict[str, Dict[str, Any]] = {}

    async def upload_document(
        self,
        name: str,
        doc_type: str,
        content: str,
        project_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a new document.
        """
        doc_id = str(uuid.uuid4())
        document = {
            "id": doc_id,
            "name": name,
            "type": doc_type,
            "content": content,
            "project_id": project_id,
            "tenant_id": tenant_id,
            "version": 1,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        self._documents[doc_id] = document
        logger.info(f"Uploaded document: {name} ({doc_id})")
        return document

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document.
        """
        return self._documents.get(doc_id)

    async def list_documents(
        self,
        project_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List documents (optionally filtered).
        """
        filtered = list(self._documents.values())
        if project_id:
            filtered = [d for d in filtered if d["project_id"] == project_id]
        if tenant_id:
            filtered = [d for d in filtered if d["tenant_id"] == tenant_id]
        return filtered
