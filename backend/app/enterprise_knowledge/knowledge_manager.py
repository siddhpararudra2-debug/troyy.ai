"""
Knowledge Manager for Enterprise Knowledge Hub
Manages knowledge entries.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class KnowledgeManager:
    """
    Manages knowledge articles, best practices, and standards.
    """

    def __init__(self):
        self._articles: Dict[str, Dict[str, Any]] = {}

    async def create_article(
        self,
        title: str,
        content: str,
        tags: List[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        article = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "tags": tags or [],
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._articles[article["id"]] = article
        return article

    async def search_articles(
        self,
        query: str,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        filtered = list(self._articles.values())
        if tenant_id:
            filtered = [a for a in filtered if a["tenant_id"] == tenant_id]
        if query:
            q = query.lower()
            filtered = [
                a
                for a in filtered
                if q in a["title"].lower() or q in a["content"].lower()
            ]
        return filtered
