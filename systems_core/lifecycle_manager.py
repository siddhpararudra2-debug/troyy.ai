"""
Lifecycle Manager - Manages the engineering product lifecycle.

Capabilities:
- Phase Management
- Stage Gate Control
- Lifecycle Reporting
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class LifecycleManager:
    """Manages the engineering product lifecycle phases and stage gates."""

    PHASES = [
        "Mission Definition", "Requirements Engineering", "System Architecture",
        "Detailed Design", "Simulation & Analysis", "Verification & Validation",
        "Manufacturing Preparation"
    ]

    def __init__(self):
        self._phases: Dict[str, Dict[str, Any]] = {}
        self._initialize_phases()

    def _initialize_phases(self):
        for i, phase in enumerate(self.PHASES):
            self._phases[phase] = {
                "name": phase,
                "order": i + 1,
                "status": "pending",
                "gate": "closed",
                "tasks": [],
                "completed_at": None,
            }

    def open_gate(self, phase_name: str) -> bool:
        if phase_name in self._phases:
            self._phases[phase_name]["gate"] = "open"
            return True
        return False

    def close_gate(self, phase_name: str) -> bool:
        if phase_name in self._phases:
            self._phases[phase_name]["gate"] = "closed"
            self._phases[phase_name]["status"] = "completed"
            self._phases[phase_name]["completed_at"] = datetime.utcnow().isoformat()
            return True
        return False

    def get_lifecycle_report(self) -> Dict[str, Any]:
        return {
            "phases": list(self._phases.values()),
            "progress": f"{sum(1 for p in self._phases.values() if p['status'] == 'completed')}/{len(self.PHASES)}",
            "generated_at": datetime.utcnow().isoformat(),
        }