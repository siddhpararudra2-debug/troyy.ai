"""
Citation Service for generating citations for RAG results.
"""
from typing import List, Dict, Any
from uuid import UUID


class CitationService:
    """Service to generate citations and references for retrieved content."""

    @staticmethod
    def format_citation(item: Dict[str, Any]) -> str:
        """Format a single citation."""
        payload = item.get("payload", {})
        title = payload.get("title", "Untitled")
        author = payload.get("author", "Unknown Author")
        source = payload.get("file_name", payload.get("source", "Unknown Source"))
        date = payload.get("ingested_at", "Unknown Date")
        return f"[{item['id']}] {author} ({date}). {title}. {source}"

    @staticmethod
    def generate_references(items: List[Dict[str, Any]]) -> List[str]:
        """Generate formatted references from search results."""
        return [CitationService.format_citation(item) for item in items]


# Singleton instance
citation_service = CitationService()
