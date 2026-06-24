"""Source Manager - Manages research sources in Sprint 16."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class SourceManager:
    """Manages research sources (papers, patents, standards, etc.)."""

    def __init__(self):
        self.sources: Dict[str, Dict[str, Any]] = {}

    def add_source(
        self,
        name: str,
        source_type: str,
        url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a research source."""
        source_id = str(uuid.uuid4())
        source = {
            "id": source_id,
            "name": name,
            "type": source_type,
            "url": url,
            "access_date": datetime.utcnow().isoformat(),
        }
        self.sources[source_id] = source
        return source

    def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a source by ID."""
        return self.sources.get(source_id)

    def list_sources(self, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all sources, optionally filtered by type."""
        sources = list(self.sources.values())
        if source_type:
            sources = [s for s in sources if s["type"] == source_type]
        return sources
