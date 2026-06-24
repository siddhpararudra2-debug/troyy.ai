"""Autonomy Manager - Manage autonomy pipeline in Sprint 14."""
from typing import Dict, Any


class AutonomyManager:
    """Manages the entire autonomy pipeline (perceive → plan → decide → act)."""

    def __init__(self):
        self.state = "idle"

    def tick(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one autonomy cycle."""
        return {"action": "idle"}
