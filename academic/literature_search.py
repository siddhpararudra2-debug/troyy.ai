"""Literature Search - Searches academic literature in Sprint 16."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class LiteratureSearch:
    """Searches academic literature databases."""

    def __init__(self):
        self.papers: Dict[str, Dict[str, Any]] = {}

    def add_paper(
        self,
        title: str,
        authors: List[str],
        venue: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a paper to the database."""
        paper_id = str(uuid.uuid4())
        paper = {
            "id": paper_id,
            "title": title,
            "authors": authors,
            "venue": venue,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.papers[paper_id] = paper
        return paper

    def search(self, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search papers by keyword."""
        results = list(self.papers.values())
        if keyword:
            results = [p for p in results if keyword.lower() in p["title"].lower()]
        return results
