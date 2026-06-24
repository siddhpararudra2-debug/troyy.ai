"""
Failure Analysis - Failure mode analysis and hazard identification.

Capabilities:
- Failure Mode Analysis
- Hazard Analysis
- FMEA Support
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime


class FailureMode:
    """A failure mode identified in the system."""

    def __init__(self, mode_id: str, component: str, failure_mode: str,
                 effects: str, cause: str, severity: int = 5,
                 occurrence: int = 3, detection: int = 5):
        self.id = mode_id
        self.component = component
        self.failure_mode = failure_mode
        self.effects = effects
        self.cause = cause
        self.severity = max(1, min(10, severity))
        self.occurrence = max(1, min(10, occurrence))
        self.detection = max(1, min(10, detection))

    @property
    def rpn(self) -> int:
        return self.severity * self.occurrence * self.detection

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "component": self.component,
            "failure_mode": self.failure_mode,
            "effects": self.effects,
            "cause": self.cause,
            "severity": self.severity,
            "occurrence": self.occurrence,
            "detection": self.detection,
            "rpn": self.rpn,
        }


class FailureAnalysis:
    """Performs failure mode and effects analysis."""

    def __init__(self):
        self._modes: Dict[str, FailureMode] = {}

    def add_failure_mode(self, component: str, failure_mode: str, effects: str,
                         cause: str, severity: int = 5, occurrence: int = 3,
                         detection: int = 5) -> FailureMode:
        mode_id = str(uuid.uuid4())
        mode = FailureMode(mode_id, component, failure_mode, effects, cause,
                          severity, occurrence, detection)
        self._modes[mode_id] = mode
        return mode

    def get_all_modes(self) -> List[FailureMode]:
        return list(self._modes.values())

    def get_high_risk_modes(self, rpn_threshold: int = 100) -> List[FailureMode]:
        return [m for m in self._modes.values() if m.rpn >= rpn_threshold]

    def generate_fmea_report(self) -> Dict[str, Any]:
        modes = self.get_all_modes()
        return {
            "total_modes": len(modes),
            "high_risk_count": len(self.get_high_risk_modes()),
            "modes": [m.to_dict() for m in sorted(modes, key=lambda m: m.rpn, reverse=True)],
            "generated_at": datetime.utcnow().isoformat(),
        }