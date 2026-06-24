"""Best Practices Manager - Knowledge Base for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class BestPracticesManager:
    """Manage best practices knowledge base."""

    def __init__(self):
        self.practices: Dict[str, Dict[str, Any]] = {}

    def add_practice(
        self,
        title: str,
        practice: str,
        category: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a best practice."""
        practice_id = str(uuid.uuid4())
        practice_record = {
            "id": practice_id,
            "title": title,
            "practice": practice,
            "category": category,
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat()
        }
        self.practices[practice_id] = practice_record
        return practice_record
