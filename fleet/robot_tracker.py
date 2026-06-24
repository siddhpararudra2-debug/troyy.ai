"""Robot Tracker - Track robots in fleet in Sprint 14."""
from typing import Dict, Any, List


class RobotTracker:
    """Tracks robot states in a fleet."""

    def __init__(self):
        self.robot_states: Dict[str, Dict[str, Any]] = {}

    def update_robot_state(self, robot_id: str, state: Dict[str, Any]) -> None:
        """Update robot state."""
        self.robot_states[robot_id] = state

    def get_robot_state(self, robot_id: str) -> Optional[Dict[str, Any]]:
        """Get robot state."""
        return self.robot_states.get(robot_id)

    def get_all_states(self) -> List[Dict[str, Any]]:
        """Get all robot states."""
        return list(self.robot_states.values())
