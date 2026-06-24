"""Robot Manager - Core robot management for Sprint 14."""
from enum import Enum
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class RobotStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class RobotType(Enum):
    MOBILE = "mobile"
    MANIPULATOR = "manipulator"
    UAV = "uav"
    UGV = "ugv"
    HUMANOID = "humanoid"
    HYBRID = "hybrid"


class RobotManager:
    """Manages robot inventory, configuration, and coordination."""

    def __init__(self):
        self.robots: Dict[str, Dict[str, Any]] = {}
        self.fleets: Dict[str, Dict[str, Any]] = {}

    def create_robot(
        self,
        name: str,
        robot_type: RobotType,
        description: Optional[str] = None,
        serial_number: Optional[str] = None,
        manufacturer: Optional[str] = None,
        model: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new robot."""
        robot_id = str(uuid.uuid4())
        robot = {
            "id": robot_id,
            "name": name,
            "robot_type": robot_type.value,
            "status": RobotStatus.IDLE.value,
            "description": description,
            "serial_number": serial_number,
            "manufacturer": manufacturer,
            "model": model,
            "capabilities": capabilities or [],
            "current_location": {},
            "health_score": 1.0,
            "battery_level": 100.0,
            "created_at": datetime.utcnow().isoformat(),
            "version": 1,
        }
        self.robots[robot_id] = robot
        return robot

    def get_robot(self, robot_id: str) -> Optional[Dict[str, Any]]:
        """Get robot by ID."""
        return self.robots.get(robot_id)

    def update_robot_status(self, robot_id: str, status: RobotStatus) -> bool:
        """Update robot status."""
        if robot_id not in self.robots:
            return False
        self.robots[robot_id]["status"] = status.value
        self.robots[robot_id]["last_modified"] = datetime.utcnow().isoformat()
        self.robots[robot_id]["version"] += 1
        return True

    def list_robots(self, status: Optional[RobotStatus] = None, robot_type: Optional[RobotType] = None) -> List[Dict[str, Any]]:
        """List all robots, optionally filtered."""
        robots = list(self.robots.values())
        if status:
            robots = [r for r in robots if r["status"] == status.value]
        if robot_type:
            robots = [r for r in robots if r["robot_type"] == robot_type.value]
        return robots

    def create_fleet(self, name: str, robot_ids: List[str], description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new fleet of robots."""
        fleet_id = str(uuid.uuid4())
        fleet = {
            "id": fleet_id,
            "name": name,
            "description": description,
            "robot_ids": robot_ids,
            "status": "idle",
            "created_at": datetime.utcnow().isoformat(),
            "version": 1,
        }
        self.fleets[fleet_id] = fleet
        return fleet

    def get_fleet(self, fleet_id: str) -> Optional[Dict[str, Any]]:
        """Get fleet by ID."""
        return self.fleets.get(fleet_id)

    def assign_mission_to_robot(self, robot_id: str, mission_id: str) -> bool:
        """Assign a mission to a robot."""
        if robot_id not in self.robots:
            return False
        if "assigned_missions" not in self.robots[robot_id]:
            self.robots[robot_id]["assigned_missions"] = []
        self.robots[robot_id]["assigned_missions"].append(mission_id)
        return True
