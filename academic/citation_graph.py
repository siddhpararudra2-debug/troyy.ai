"""Citation Graph - Builds citation graphs in Sprint 16."""
from typing import Dict, Any, List


class CitationGraph:
    """Builds and analyzes citation graphs."""

    def __init__(self):
        self.citations: List[Dict[str, Any]] = []

    def add_citation(
        self,
        citing_id: str,
        cited_id: str,
    ) -> Dict[str, Any]:
        """Add a citation to the graph."""
        citation = {
            "citing_id": citing_id,
            "cited_id": cited_id,
        }
        self.citations.append(citation)
        return citation

    def get_citations(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get citations for a paper."""
        return [c for c in self.citations if c["citing_id"] == paper_id or c["cited_id"] == paper_id]
