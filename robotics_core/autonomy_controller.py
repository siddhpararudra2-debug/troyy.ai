"""Autonomy Controller - Control autonomy stack in Sprint 14."""
from typing import Dict, Any


class AutonomyController:
    """Controls the autonomy stack."""

    def __init__(self):
        self.autonomy_enabled = False

    def enable_autonomy(self) -> None:
        """Enable full autonomy."""
        self.autonomy_enabled = True

    def disable_autonomy(self) -> None:
        """Disable autonomy (manual mode)."""
        self.autonomy_enabled = False
