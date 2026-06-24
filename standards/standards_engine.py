"""Standards Engine - Manages engineering standards in Sprint 16."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class StandardsEngine:
    """Manages engineering standards (ISO, ASTM, ASME, etc.)."""

    def __init__(self):
        self.standards: Dict[str, Dict[str, Any]] = {}

    def add_standard(
        self,
        name: str,
        standard_number: str,
        issuing_body: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a new standard."""
        standard_id = str(uuid.uuid4())
        standard = {
            "id": standard_id,
            "name": name,
            "number": standard_number,
            "issuing_body": issuing_body,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.standards[standard_id] = standard
        return standard

    def search_standards(
        self,
        keyword: Optional[str] = None,
        issuing_body: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search standards by keyword and issuing body."""
        results = list(self.standards.values())
        if keyword:
            results = [s for s in results if keyword.lower() in s["name"].lower()]
        if issuing_body:
            results = [s for s in results if s["issuing_body"] == issuing_body]
        return results
