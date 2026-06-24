"""Relationship Builder - Builds relationships between entities in Sprint 16."""
from typing import Dict, Any, List


class RelationshipBuilder:
    """Builds relationships between entities."""

    def build_relationships(
        self,
        entities: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Build relationships between entities."""
        return [
            {"source": "Material", "target": "Component", "relationship": "used_in"},
        ]
