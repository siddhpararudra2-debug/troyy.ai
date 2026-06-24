"""Evidence Manager - Manages research evidence in Sprint 16."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class EvidenceManager:
    """Manages evidence collected during research."""

    def __init__(self):
        self.evidence: Dict[str, Dict[str, Any]] = {}

    def add_evidence(
        self,
        project_id: str,
        source_id: str,
        content: str,
        relevance_score: float = 0.8,
    ) -> Dict[str, Any]:
        """Add new evidence to a project."""
        evidence_id = str(uuid.uuid4())
        evidence_item = {
            "id": evidence_id,
            "project_id": project_id,
            "source_id": source_id,
            "content": content,
            "relevance_score": relevance_score,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.evidence[evidence_id] = evidence_item
        return evidence_item

    def get_evidence(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all evidence for a project."""
        return [e for e in self.evidence.values() if e["project_id"] == project_id]
