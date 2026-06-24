"""Interaction Manager - Manage human-robot interactions in Sprint 14."""
from typing import Dict, Any, List
from datetime import datetime


class InteractionManager:
    """Manages interactions between humans and robots."""

    def __init__(self):
        self.interactions: List[Dict[str, Any]] = []

    def log_interaction(self, interaction: Dict[str, Any]) -> None:
        """Log an interaction."""
        interaction["timestamp"] = datetime.utcnow().isoformat()
        self.interactions.append(interaction)
