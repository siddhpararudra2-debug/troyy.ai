"""Robot Architecture - Define robot hardware/software architectures for Sprint 14."""
from typing import Dict, Any, List, Optional
from enum import Enum


class ComponentType(Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    PROCESSOR = "processor"
    COMMUNICATION = "communication"
    POWER = "power"


class RobotArchitecture:
    """Defines robot hardware/software architecture templates."""

    def __init__(self):
        self.architectures: Dict[str, Dict[str, Any]] = {}

    def create_architecture(
        self,
        name: str,
        robot_type: str,
        components: List[Dict[str, Any]],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new robot architecture template."""
        architecture_id = f"arch_{name.lower().replace(' ', '_')}"
        architecture = {
            "id": architecture_id,
            "name": name,
            "robot_type": robot_type,
            "description": description,
            "components": components,
        }
        self.architectures[architecture_id] = architecture
        return architecture

    def get_architecture(self, architecture_id: str) -> Optional[Dict[str, Any]]:
        """Get architecture by ID."""
        return self.architectures.get(architecture_id)

    def list_architectures(self, robot_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List architectures, optionally filtered by robot type."""
        archs = list(self.architectures.values())
        if robot_type:
            archs = [a for a in archs if a["robot_type"] == robot_type]
        return archs
