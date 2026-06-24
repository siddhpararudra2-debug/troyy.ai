"""Fleet Manager - Manage fleets of robots in Sprint 14."""
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime


class FleetManager:
    """Manages fleets of robots."""

    def __init__(self):
        self.fleets: Dict[str, Dict[str, Any]] = {}

    def create_fleet(self, name: str, robot_ids: List[str]) -> Dict[str, Any]:
        """Create a new fleet."""
        fleet_id = str(uuid.uuid4())
        fleet = {
            "id": fleet_id,
            "name": name,
            "robot_ids": robot_ids,
            "status": "idle",
            "created_at": datetime.utcnow().isoformat(),
        }
        self.fleets[fleet_id] = fleet
        return fleet

    def get_fleet(self, fleet_id: str) -> Optional[Dict[str, Any]]:
        """Get fleet by ID."""
        return self.fleets.get(fleet_id)

    def add_robot_to_fleet(self, fleet_id: str, robot_id: str) -> bool:
        """Add a robot to a fleet."""
        if fleet_id not in self.fleets:
            return False
        if robot_id not in self.fleets[fleet_id]["robot_ids"]:
            self.fleets[fleet_id]["robot_ids"].append(robot_id)
        return True
