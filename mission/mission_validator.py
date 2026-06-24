"""
Mission Validator - Validates mission plans against requirements and constraints.

Capabilities:
- Mission Validation
- Requirement Verification
- Constraint Validation
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from mission.mission_planner import Mission


class MissionValidator:
    """Validates mission plans against requirements and constraints."""

    def validate(self, mission: Mission) -> Dict[str, Any]:
        """Validate a complete mission plan."""
        issues = []

        # Check mission basics
        if not mission.name:
            issues.append({"severity": "error", "message": "Mission name is required"})
        if not mission.objectives:
            issues.append({"severity": "error", "message": "At least one mission objective is required"})

        # Check constraints
        if not mission.constraints:
            issues.append({"severity": "warning", "message": "No constraints defined for mission"})

        # Validate for mission type
        if mission.mission_type.value == "uav" and "max_altitude" not in str(mission.metadata):
            issues.append({"severity": "warning", "message": "UAV mission should define max altitude"})

        valid = not any(i["severity"] == "error" for i in issues)

        return {
            "mission_id": mission.id,
            "valid": valid,
            "issues": issues,
            "issue_count": len(issues),
            "validated_at": datetime.utcnow().isoformat(),
        }