"""Robot Lifecycle - Manage robot lifecycle states for Sprint 14."""
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime


class LifecycleState(Enum):
    UNCONFIGURED = "unconfigured"
    INACTIVE = "inactive"
    ACTIVE = "active"
    FINALIZED = "finalized"
    ERROR = "error"


class RobotLifecycle:
    """Manages robot lifecycle states and transitions."""

    def __init__(self):
        self.lifecycle_states: Dict[str, Dict[str, Any]] = {}

    def initialize_robot(self, robot_id: str) -> bool:
        """Initialize robot lifecycle to UNCONFIGURED."""
        self.lifecycle_states[robot_id] = {
            "state": LifecycleState.UNCONFIGURED.value,
            "entered_at": datetime.utcnow().isoformat(),
            "history": [],
        }
        return True

    def transition_state(self, robot_id: str, new_state: LifecycleState) -> bool:
        """Transition robot to a new lifecycle state."""
        if robot_id not in self.lifecycle_states:
            return False
        current = self.lifecycle_states[robot_id]
        current["history"].append({
            "previous_state": current["state"],
            "new_state": new_state.value,
            "timestamp": datetime.utcnow().isoformat(),
        })
        current["state"] = new_state.value
        current["entered_at"] = datetime.utcnow().isoformat()
        return True

    def get_state(self, robot_id: str) -> Optional[str]:
        """Get current lifecycle state of robot."""
        if robot_id not in self.lifecycle_states:
            return None
        return self.lifecycle_states[robot_id]["state"]

    def get_history(self, robot_id: str) -> List[Dict[str, Any]]:
        """Get lifecycle history for robot."""
        if robot_id not in self.lifecycle_states:
            return []
        return self.lifecycle_states[robot_id]["history"]
