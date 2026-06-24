"""Mission Engine - Core mission management and execution."""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field, asdict
import json


class MissionStatus(str, Enum):
    """Mission lifecycle states."""
    PLANNING = "planning"
    READY = "ready"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"
    FAILED = "failed"


class MissionPriority(str, Enum):
    """Mission priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MissionObjective:
    """Mission objective specification."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    objective_type: str = ""  # survey, delivery, rescue, combat, etc.
    priority: MissionPriority = MissionPriority.MEDIUM
    location: Dict[str, float] = field(default_factory=dict)  # lat, lon, alt
    target_parameters: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    estimated_duration: float = 0.0  # minutes
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MissionAsset:
    """Mission asset (platform, vehicle, sensor, etc.)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    asset_id: str = ""  # Reference to actual asset
    asset_type: str = ""  # uav, aircraft, robot, sensor, etc.
    role: str = ""  # primary, support, backup
    capabilities: List[str] = field(default_factory=list)
    assigned_objectives: List[str] = field(default_factory=list)
    readiness: float = 1.0  # 0.0-1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Mission:
    """Complete mission definition."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    mission_type: str = ""  # uav, aerospace, robotics, etc.
    status: MissionStatus = MissionStatus.PLANNING
    priority: MissionPriority = MissionPriority.MEDIUM
    
    # Mission definition
    objectives: List[MissionObjective] = field(default_factory=list)
    assigned_assets: List[MissionAsset] = field(default_factory=list)
    
    # Timeline
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    
    # Constraints and requirements
    area_of_operations: Dict[str, Any] = field(default_factory=dict)  # geofence, boundaries
    weather_requirements: Dict[str, Any] = field(default_factory=dict)
    regulatory_requirements: List[str] = field(default_factory=list)
    risk_level: str = "medium"  # low, medium, high
    
    # Planning metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    last_modified: datetime = field(default_factory=datetime.utcnow)
    modified_by: str = ""
    version: int = 1
    
    # Execution data
    metadata: Dict[str, Any] = field(default_factory=dict)


class MissionEngine:
    """Core mission management engine."""
    
    def __init__(self):
        """Initialize mission engine."""
        self.missions: Dict[str, Mission] = {}
        self.mission_history: List[Mission] = []
        
    def create_mission(
        self,
        name: str,
        description: str,
        mission_type: str,
        priority: MissionPriority = MissionPriority.MEDIUM,
        created_by: str = "system"
    ) -> Mission:
        """Create new mission."""
        mission = Mission(
            name=name,
            description=description,
            mission_type=mission_type,
            priority=priority,
            created_by=created_by
        )
        self.missions[mission.id] = mission
        return mission
    
    def add_objective(
        self,
        mission_id: str,
        objective: MissionObjective
    ) -> bool:
        """Add objective to mission."""
        if mission_id not in self.missions:
            return False
        self.missions[mission_id].objectives.append(objective)
        self._update_mission_timestamp(mission_id)
        return True
    
    def add_asset(
        self,
        mission_id: str,
        asset: MissionAsset
    ) -> bool:
        """Add asset to mission."""
        if mission_id not in self.missions:
            return False
        self.missions[mission_id].assigned_assets.append(asset)
        self._update_mission_timestamp(mission_id)
        return True
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Retrieve mission by ID."""
        return self.missions.get(mission_id)
    
    def list_missions(
        self,
        status: Optional[MissionStatus] = None,
        mission_type: Optional[str] = None
    ) -> List[Mission]:
        """List missions with optional filters."""
        missions = list(self.missions.values())
        
        if status:
            missions = [m for m in missions if m.status == status]
        if mission_type:
            missions = [m for m in missions if m.mission_type == mission_type]
        
        return missions
    
    def update_mission_status(
        self,
        mission_id: str,
        status: MissionStatus,
        modified_by: str = "system"
    ) -> bool:
        """Update mission status."""
        if mission_id not in self.missions:
            return False
        
        mission = self.missions[mission_id]
        mission.status = status
        mission.modified_by = modified_by
        self._update_mission_timestamp(mission_id)
        
        if status == MissionStatus.EXECUTING and mission.actual_start is None:
            mission.actual_start = datetime.utcnow()
        elif status in [MissionStatus.COMPLETED, MissionStatus.ABORTED, MissionStatus.FAILED]:
            if mission.actual_end is None:
                mission.actual_end = datetime.utcnow()
        
        return True
    
    def archive_mission(self, mission_id: str) -> bool:
        """Archive completed mission to history."""
        if mission_id not in self.missions:
            return False
        
        mission = self.missions[mission_id]
        self.mission_history.append(mission)
        del self.missions[mission_id]
        return True
    
    def get_mission_summary(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission summary."""
        mission = self.get_mission(mission_id)
        if not mission:
            return None
        
        return {
            "id": mission.id,
            "name": mission.name,
            "type": mission.mission_type,
            "status": mission.status.value,
            "priority": mission.priority.value,
            "objectives": len(mission.objectives),
            "assets": len(mission.assigned_assets),
            "planned_start": mission.planned_start,
            "planned_end": mission.planned_end,
            "actual_start": mission.actual_start,
            "actual_end": mission.actual_end,
            "duration_minutes": mission.metadata.get("duration_minutes"),
            "success": mission.metadata.get("success"),
        }
    
    def _update_mission_timestamp(self, mission_id: str) -> None:
        """Update mission modification timestamp."""
        if mission_id in self.missions:
            self.missions[mission_id].last_modified = datetime.utcnow()
            self.missions[mission_id].version += 1
    
    def to_dict(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Convert mission to dictionary."""
        mission = self.get_mission(mission_id)
        if not mission:
            return None
        
        return {
            "id": mission.id,
            "name": mission.name,
            "description": mission.description,
            "mission_type": mission.mission_type,
            "status": mission.status.value,
            "priority": mission.priority.value,
            "objectives": [asdict(obj) for obj in mission.objectives],
            "assigned_assets": [asdict(asset) for asset in mission.assigned_assets],
            "planned_start": mission.planned_start,
            "planned_end": mission.planned_end,
            "actual_start": mission.actual_start,
            "actual_end": mission.actual_end,
            "area_of_operations": mission.area_of_operations,
            "weather_requirements": mission.weather_requirements,
            "regulatory_requirements": mission.regulatory_requirements,
            "risk_level": mission.risk_level,
            "created_at": mission.created_at,
            "created_by": mission.created_by,
            "last_modified": mission.last_modified,
            "modified_by": mission.modified_by,
            "version": mission.version,
            "metadata": mission.metadata,
        }
