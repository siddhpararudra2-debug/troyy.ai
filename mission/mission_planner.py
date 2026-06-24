"""
Mission Planner - Defines and plans engineering missions.

Capabilities:
- Mission Definition
- Mission Constraints
- Performance Targets
- Multi-domain Mission Support (UAV, Aerospace, Robotics)
"""

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class MissionType(str, Enum):
    """Types of missions supported."""
    UAV = "uav"
    AEROSPACE = "aerospace"
    ROBOTICS = "robotics"
    AUTONOMOUS = "autonomous"
    GENERAL = "general"


class MissionPhase(str, Enum):
    """Phases of a mission lifecycle."""
    DEFINITION = "definition"
    PLANNING = "planning"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    COMPLETE = "complete"


class MissionConstraint:
    """A constraint on the mission."""

    def __init__(self, name: str, constraint_type: str, value: Any,
                 unit: Optional[str] = None, description: Optional[str] = None):
        self.name = name
        self.type = constraint_type
        self.value = value
        self.unit = unit
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "unit": self.unit,
            "description": self.description,
        }


class PerformanceTarget:
    """A performance target for the mission."""

    def __init__(self, name: str, target_type: str, target_value: float,
                 unit: Optional[str] = None, threshold: Optional[float] = None):
        self.name = name
        self.type = target_type
        self.target_value = target_value
        self.unit = unit
        self.threshold = threshold

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "target_value": self.target_value,
            "unit": self.unit,
            "threshold": self.threshold,
        }


class Mission:
    """An engineering mission definition."""

    def __init__(
        self,
        mission_id: str,
        name: str,
        mission_type: MissionType = MissionType.GENERAL,
        description: Optional[str] = None,
    ):
        self.id = mission_id
        self.name = name
        self.mission_type = mission_type
        self.description = description
        self.phase = MissionPhase.DEFINITION
        self.objectives: List[str] = []
        self.constraints: List[MissionConstraint] = []
        self.performance_targets: List[PerformanceTarget] = []
        self.waypoints: List[Dict[str, Any]] = []
        self.requirements: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_objective(self, objective: str):
        self.objectives.append(objective)

    def add_constraint(self, constraint: MissionConstraint):
        self.constraints.append(constraint)

    def add_performance_target(self, target: PerformanceTarget):
        self.performance_targets.append(target)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "mission_type": self.mission_type.value,
            "description": self.description,
            "phase": self.phase.value,
            "objectives": self.objectives,
            "constraints": [c.to_dict() for c in self.constraints],
            "performance_targets": [t.to_dict() for t in self.performance_targets],
            "waypoints": self.waypoints,
            "requirements": self.requirements,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class MissionPlanner:
    """Plans and defines engineering missions."""

    def __init__(self):
        self._missions: Dict[str, Mission] = {}

    def create_mission(
        self,
        name: str,
        mission_type: MissionType = MissionType.GENERAL,
        description: Optional[str] = None,
    ) -> Mission:
        mission_id = str(uuid.uuid4())
        mission = Mission(mission_id, name, mission_type, description)
        self._missions[mission_id] = mission
        return mission

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self._missions.get(mission_id)

    def add_uav_mission_params(self, mission: Mission, params: Dict[str, Any]):
        """Add UAV-specific mission parameters."""
        mission.metadata["uav_params"] = params
        if "max_altitude" in params:
            mission.add_constraint(MissionConstraint("Max Altitude", "altitude", params["max_altitude"], "m"))
        if "max_range" in params:
            mission.add_constraint(MissionConstraint("Max Range", "range", params["max_range"], "km"))
        if "endurance" in params:
            mission.add_constraint(MissionConstraint("Endurance", "time", params["endurance"], "min"))
        if "payload_capacity" in params:
            mission.add_performance_target(PerformanceTarget("Payload Capacity", "mass", params["payload_capacity"], "kg"))

    def add_aerospace_mission_params(self, mission: Mission, params: Dict[str, Any]):
        """Add aerospace-specific mission parameters."""
        mission.metadata["aerospace_params"] = params
        if "orbit" in params:
            mission.add_constraint(MissionConstraint("Orbit", "orbit", params["orbit"]))
        if "delta_v" in params:
            mission.add_constraint(MissionConstraint("Delta-V", "velocity", params["delta_v"], "m/s"))
        if "launch_window" in params:
            mission.add_constraint(MissionConstraint("Launch Window", "time", params["launch_window"]))

    def add_robotics_mission_params(self, mission: Mission, params: Dict[str, Any]):
        """Add robotics-specific mission parameters."""
        mission.metadata["robotics_params"] = params
        if "workspace" in params:
            mission.add_constraint(MissionConstraint("Workspace", "volume", params["workspace"]))
        if "payload" in params:
            mission.add_performance_target(PerformanceTarget("Payload", "mass", params["payload"], "kg"))
        if "accuracy" in params:
            mission.add_performance_target(PerformanceTarget("Accuracy", "precision", params["accuracy"], "mm"))

    def get_all_missions(self) -> List[Mission]:
        return list(self._missions.values())

    def generate_mission_profile(self, mission_id: str) -> Dict[str, Any]:
        """Generate a mission profile document."""
        mission = self._missions.get(mission_id)
        if not mission:
            return {}
        return {
            "mission": mission.to_dict(),
            "profile": {
                "type": mission.mission_type.value,
                "phases": [p.value for p in MissionPhase],
                "constraint_count": len(mission.constraints),
                "target_count": len(mission.performance_targets),
                "objective_count": len(mission.objectives),
            },
            "generated_at": datetime.utcnow().isoformat(),
        }