"""Patent Search - Searches patent databases in Sprint 16."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class PatentSearch:
    """Searches patent databases."""

    def __init__(self):
        self.patents: Dict[str, Dict[str, Any]] = {}

    def add_patent(
        self,
        title: str,
        patent_number: str,
        inventors: List[str],
        assignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a patent to the database."""
        patent_id = str(uuid.uuid4())
        patent = {
            "id": patent_id,
            "title": title,
            "number": patent_number,
            "inventors": inventors,
            "assignee": assignee,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.patents[patent_id] = patent
        return patent

    def search(
        self,
        keyword: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search patents by keyword and assignee."""
        results = list(self.patents.values())
        if keyword:
            results = [p for p in results if keyword.lower() in p["title"].lower()]
        if assignee:
            results = [p for p in results if p["assignee"] == assignee]
        return results
