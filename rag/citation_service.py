"""
Citation service for Engineering OS.
Generates and manages citations for knowledge base sources.
"""
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class CitationService:
    """
    Generates citations for knowledge sources used in AI responses.
    Supports multiple citation formats and source types.
    """

    @staticmethod
    def format_citation(
        source: str,
        title: str = "",
        author: str = "",
        year: Optional[int] = None,
        url: str = "",
        citation_format: str = "inline",
    ) -> str:
        """Format a citation based on the specified format."""
        if citation_format == "inline":
            return f"[{source}]"
        elif citation_format == "academic":
            author_part = f"{author}, " if author else ""
            year_part = f"({year}) " if year else ""
            title_part = f"\"{title},\" " if title else ""
            return f"{author_part}{year_part}{title_part}{source}"
        elif citation_format == "apa":
            author_part = f"{author}. " if author else ""
            year_part = f"({year}). " if year else ""
            title_part = f"*{title}*. " if title else ""
            return f"{author_part}{year_part}{title_part}{source}"
        else:
            return f"[{source}]"

    @staticmethod
    def generate_reference_list(results: list[dict]) -> list[str]:
        """Generate a formatted reference list from search results."""
        references = []
        for i, result in enumerate(results, 1):
            source = result.get("source", "Unknown Source")
            title = result.get("title", "")
            score = result.get("score", 0)
            ref = f"[{i}] {title} ({source}) - Similarity: {score:.2f}"
            references.append(ref)
        return references

    @staticmethod
    def annotate_response(
        response: str,
        source_mapping: dict[str, list[str]],
    ) -> str:
        """
        Annotate an AI response with source citations.
        
        Args:
            response: The AI generated response
            source_mapping: Mapping of citation keys to list of sources
            
        Returns:
            Response with citation annotations and references
        """
        annotated = response
        
        # Add references section
        if source_mapping:
            annotated += "\n\n---\n**References:**\n"
            ref_num = 1
            for citation_key, sources in source_mapping.items():
                for source in sources:
                    annotated += f"\n[{ref_num}] {source}"
                    ref_num += 1
        
        return annotated