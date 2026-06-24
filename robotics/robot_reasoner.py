"""Robot Reasoner - Decision-making and reasoning for robots in Sprint 14."""
from typing import Dict, Any, List, Optional
from datetime import datetime


class RobotReasoner:
    """Handles robot decision-making and reasoning."""

    def __init__(self):
        self.reasoning_logs: List[Dict[str, Any]] = []

    def reason(
        self,
        robot_id: str,
        current_state: Dict[str, Any],
        goals: List[Dict[str, Any]],
        constraints: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Perform reasoning to determine next actions."""
        reasoning_result = {
            "robot_id": robot_id,
            "timestamp": datetime.utcnow().isoformat(),
            "current_state": current_state,
            "goals": goals,
            "constraints": constraints or [],
            "decision": self._select_next_action(current_state, goals, constraints),
            "confidence": 0.85,
        }
        self.reasoning_logs.append(reasoning_result)
        return reasoning_result

    def _select_next_action(
        self,
        current_state: Dict[str, Any],
        goals: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
    ) -> str:
        """Select next action based on state, goals, constraints."""
        if current_state.get("battery_level", 100) < 20:
            return "return_to_base"
        elif goals:
            return "pursue_goal"
        else:
            return "idle"

    def get_reasoning_log(self, robot_id: str) -> List[Dict[str, Any]]:
        """Get reasoning logs for a robot."""
        return [log for log in self.reasoning_logs if log["robot_id"] == robot_id]
