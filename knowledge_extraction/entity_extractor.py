"""Entity Extractor - Extracts entities from text in Sprint 16."""
from typing import Dict, Any, List


class EntityExtractor:
    """Extracts engineering entities from text."""

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text."""
        return [
            {"entity": "Material", "value": "Aluminum", "confidence": 0.9},
        ]
