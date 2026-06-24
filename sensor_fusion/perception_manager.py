"""Perception Manager - Manage perception pipeline in Sprint 14."""
from typing import Dict, Any, List


class PerceptionManager:
    """Manages the perception pipeline."""

    def __init__(self):
        self.objects: List[Dict[str, Any]] = []

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update perception with new detections."""
        self.objects = detections
        return detections
