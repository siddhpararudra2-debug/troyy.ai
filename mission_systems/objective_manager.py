"""Objective Manager - Mission objective tracking and management."""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict


class ObjectiveStatus(str, Enum):
    """Objective status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ObjectiveMetric:
    """Objective performance metric."""
    name: str
    current_value: float
    target_value: float
    unit: str
    threshold_min: float = 0.0
    threshold_max: float = 100.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ObjectiveConstraint:
    """Constraint on objective."""
    constraint_type: str  # geofence, altitude, speed, time, resource
    value: Any
    operator: str  # eq, lt, gt, lte, gte, in, not_in
    severity: str  # soft, hard


class ObjectiveManager:
    """Manages mission objectives and their execution."""
    
    def __init__(self):
        """Initialize objective manager."""
        self.objectives: Dict[str, Dict[str, Any]] = {}
        self.objective_progress: Dict[str, List[ObjectiveMetric]] = {}
        self.objective_history: List[Dict[str, Any]] = []
    
    def create_objective(
        self,
        mission_id: str,
        name: str,
        description: str,
        objective_type: str,
        target_location: Dict[str, float],
        success_criteria: List[str],
        constraints: Optional[List[ObjectiveConstraint]] = None,
        estimated_duration: float = 0.0
    ) -> str:
        """Create new objective."""
        objective_id = str(uuid.uuid4())
        
        self.objectives[objective_id] = {
            "id": objective_id,
            "mission_id": mission_id,
            "name": name,
            "description": description,
            "type": objective_type,
            "status": ObjectiveStatus.PENDING.value,
            "target_location": target_location,
            "success_criteria": success_criteria,
            "constraints": [asdict(c) for c in constraints] if constraints else [],
            "estimated_duration": estimated_duration,
            "actual_start": None,
            "actual_end": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        self.objective_progress[objective_id] = []
        return objective_id
    
    def get_objective(self, objective_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve objective by ID."""
        return self.objectives.get(objective_id)
    
    def list_objectives(
        self,
        mission_id: str,
        status: Optional[ObjectiveStatus] = None
    ) -> List[Dict[str, Any]]:
        """List mission objectives."""
        objectives = [
            obj for obj in self.objectives.values()
            if obj["mission_id"] == mission_id
        ]
        
        if status:
            objectives = [
                obj for obj in objectives
                if obj["status"] == status.value
            ]
        
        return objectives
    
    def update_objective_status(
        self,
        objective_id: str,
        status: ObjectiveStatus
    ) -> bool:
        """Update objective status."""
        if objective_id not in self.objectives:
            return False
        
        obj = self.objectives[objective_id]
        obj["status"] = status.value
        obj["updated_at"] = datetime.utcnow()
        
        if status == ObjectiveStatus.IN_PROGRESS and obj["actual_start"] is None:
            obj["actual_start"] = datetime.utcnow()
        elif status in [ObjectiveStatus.COMPLETED, ObjectiveStatus.FAILED]:
            if obj["actual_end"] is None:
                obj["actual_end"] = datetime.utcnow()
        
        return True
    
    def add_metric(
        self,
        objective_id: str,
        metric: ObjectiveMetric
    ) -> bool:
        """Add metric measurement to objective."""
        if objective_id not in self.objective_progress:
            return False
        
        self.objective_progress[objective_id].append(metric)
        self._update_objective_timestamp(objective_id)
        return True
    
    def get_objective_metrics(
        self,
        objective_id: str,
        metric_name: Optional[str] = None
    ) -> List[ObjectiveMetric]:
        """Retrieve objective metrics."""
        if objective_id not in self.objective_progress:
            return []
        
        metrics = self.objective_progress[objective_id]
        
        if metric_name:
            metrics = [m for m in metrics if m.name == metric_name]
        
        return metrics
    
    def evaluate_objective_success(
        self,
        objective_id: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Evaluate if objective meets success criteria."""
        if objective_id not in self.objectives:
            return False, {}
        
        obj = self.objectives[objective_id]
        metrics = self.objective_progress.get(objective_id, [])
        
        evaluation = {
            "objective_id": objective_id,
            "status": obj["status"],
            "success_criteria": obj["success_criteria"],
            "metrics": [
                {
                    "name": m.name,
                    "current": m.current_value,
                    "target": m.target_value,
                    "met": abs(m.current_value - m.target_value) < 0.01
                }
                for m in metrics
            ],
            "evaluation_time": datetime.utcnow(),
        }
        
        success = all(
            abs(m.current_value - m.target_value) < 0.01
            for m in metrics
        )
        
        return success, evaluation
    
    def get_constraint_violations(
        self,
        objective_id: str,
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for constraint violations."""
        if objective_id not in self.objectives:
            return []
        
        obj = self.objectives[objective_id]
        violations = []
        
        for constraint in obj.get("constraints", []):
            if self._check_constraint_violation(constraint, current_state):
                violations.append({
                    "constraint_type": constraint["constraint_type"],
                    "severity": constraint["severity"],
                    "message": f"Constraint violation: {constraint['constraint_type']}"
                })
        
        return violations
    
    def archive_objective(self, objective_id: str) -> bool:
        """Archive completed objective."""
        if objective_id not in self.objectives:
            return False
        
        obj = self.objectives[objective_id]
        self.objective_history.append(obj)
        del self.objectives[objective_id]
        
        return True
    
    def _update_objective_timestamp(self, objective_id: str) -> None:
        """Update objective timestamp."""
        if objective_id in self.objectives:
            self.objectives[objective_id]["updated_at"] = datetime.utcnow()
    
    def _check_constraint_violation(
        self,
        constraint: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> bool:
        """Check if constraint is violated."""
        state_value = current_state.get(constraint["constraint_type"])
        if state_value is None:
            return False
        
        constraint_value = constraint["value"]
        operator = constraint["operator"]
        
        if operator == "eq":
            return state_value != constraint_value
        elif operator == "lt":
            return state_value >= constraint_value
        elif operator == "gt":
            return state_value <= constraint_value
        elif operator == "lte":
            return state_value > constraint_value
        elif operator == "gte":
            return state_value < constraint_value
        elif operator == "in":
            return state_value not in constraint_value
        elif operator == "not_in":
            return state_value in constraint_value
        
        return False
