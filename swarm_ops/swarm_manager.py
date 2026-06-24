"""Swarm Manager - Module 2 for Sprint 13."""
from enum import Enum
import uuid
from typing import List, Dict, Any, Optional, Tuple


class SwarmStatus(Enum):
    IDLE = "idle"
    COORDINATED = "coordinated"
    EXECUTING = "executing"
    DEGRADED = "degraded"
    ERROR = "error"


class SwarmAgent:
    def __init__(self, agent_id: str, agent_type: str):
        self.id = agent_id
        self.type = agent_type
        self.status = "idle"
        self.position = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.velocity = {"vx": 0.0, "vy": 0.0, "vz": 0.0}
        self.health = 1.0
        self.capabilities = []


class SwarmManager:
    def __init__(self):
        self.swarms: Dict[str, Any] = {}

    def create_swarm(self, name: str, swarm_type: str, agents: List[SwarmAgent]) -> Any:
        swarm_id = str(uuid.uuid4())
        swarm = {
            "id": swarm_id,
            "name": name,
            "swarm_type": swarm_type,
            "agents": agents,
            "status": SwarmStatus.IDLE,
            "formation_type": None,
            "formation_spacing": 5.0,
            "leader_id": agents[0].id if agents else None,
            "cohesion": 1.0,
            "connectivity": 1.0,
            "efficiency": 1.0,
        }
        self.swarms[swarm_id] = swarm
        return swarm

    def form_swarm(self, swarm_id: str, formation_type: str, formation_spacing: float = 5.0) -> Tuple[bool, Dict[str, Any]]:
        if swarm_id not in self.swarms:
            return False, {"error": "Swarm not found"}
        
        swarm = self.swarms[swarm_id]
        swarm["formation_type"] = formation_type
        swarm["formation_spacing"] = formation_spacing
        swarm["status"] = SwarmStatus.COORDINATED
        return True, swarm

    def get_swarm(self, swarm_id: str) -> Optional[Any]:
        return self.swarms.get(swarm_id)

    def list_swarms(self) -> List[Any]:
        return list(self.swarms.values())
