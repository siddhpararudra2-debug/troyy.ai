"""Design Patterns Manager - Knowledge Base for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class DesignPatternsManager:
    """Manage engineering design patterns library."""

    def __init__(self):
        self.patterns: Dict[str, Dict[str, Any]] = {}

    def add_pattern(
        self,
        name: str,
        pattern_type: str,
        description: Optional[str] = None,
        implementation_notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a design pattern."""
        pattern_id = str(uuid.uuid4())
        pattern = {
            "id": pattern_id,
            "name": name,
            "pattern_type": pattern_type,
            "description": description,
            "implementation_notes": implementation_notes,
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat()
        }
        self.patterns[pattern_id] = pattern
        return pattern

    def get_patterns(
        self,
        pattern_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get design patterns, optionally filtered by type."""
        patterns = list(self.patterns.values())
        if pattern_type:
            patterns = [p for p in patterns if p["pattern_type"] == pattern_type]
        return patterns
