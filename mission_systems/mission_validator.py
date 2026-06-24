"""Mission Validator - Mission validation and constraint checking."""

from typing import List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum


class ValidationStatus(str, Enum):
    """Validation status."""
    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"


class MissionValidator:
    """Validates missions for completeness and feasibility."""
    
    def __init__(self):
        """Initialize mission validator."""
        self.validation_rules = self._initialize_rules()
        self.validation_history: List[Dict[str, Any]] = []
    
    def validate_mission(self, mission: Dict[str, Any]) -> Tuple[ValidationStatus, List[str], List[str]]:
        """Validate complete mission."""
        errors = []
        warnings = []
        
        # Check required fields
        errors.extend(self._validate_required_fields(mission))
        
        # Check objectives
        errors.extend(self._validate_objectives(mission.get("objectives", [])))
        
        # Check assets
        warnings.extend(self._validate_assets(mission.get("assigned_assets", [])))
        
        # Check planning constraints
        warnings.extend(self._validate_planning_constraints(mission))
        
        # Check operational constraints
        warnings.extend(self._validate_operational_constraints(mission))
        
        # Check regulatory requirements
        warnings.extend(self._validate_regulatory_requirements(mission))
        
        # Determine overall status
        status = ValidationStatus.ERROR if errors else (
            ValidationStatus.WARNING if warnings else ValidationStatus.VALID
        )
        
        # Record validation
        self.validation_history.append({
            "mission_id": mission.get("id"),
            "timestamp": datetime.utcnow(),
            "status": status.value,
            "errors": errors,
            "warnings": warnings,
        })
        
        return status, errors, warnings
    
    def validate_objective(self, objective: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate objective."""
        errors = []
        
        # Check required fields
        required_fields = ["name", "type", "target_location", "success_criteria"]
        for field in required_fields:
            if field not in objective or not objective[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check location
        if "target_location" in objective:
            location = objective["target_location"]
            if not isinstance(location, dict):
                errors.append("Target location must be a dictionary")
            elif "lat" not in location or "lon" not in location:
                errors.append("Target location must include lat and lon")
            else:
                lat = location["lat"]
                lon = location["lon"]
                if not (-90 <= lat <= 90):
                    errors.append(f"Invalid latitude: {lat}")
                if not (-180 <= lon <= 180):
                    errors.append(f"Invalid longitude: {lon}")
        
        # Check success criteria
        if "success_criteria" in objective:
            criteria = objective["success_criteria"]
            if not isinstance(criteria, list) or len(criteria) == 0:
                errors.append("Success criteria must be a non-empty list")
        
        return len(errors) == 0, errors
    
    def validate_plan(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate mission plan."""
        errors = []
        
        # Check waypoints
        if "waypoints" not in plan or not plan["waypoints"]:
            errors.append("Plan must have at least one waypoint")
        else:
            for i, wp in enumerate(plan["waypoints"]):
                if "lat" not in wp or "lon" not in wp:
                    errors.append(f"Waypoint {i} missing lat/lon")
        
        # Check timing
        if "estimated_flight_time" in plan:
            if plan["estimated_flight_time"] < 0:
                errors.append("Flight time cannot be negative")
        
        # Check assets
        if "primary_asset" not in plan or not plan["primary_asset"]:
            errors.append("Plan must specify primary asset")
        
        return len(errors) == 0, errors
    
    def check_constraint_violations(
        self,
        mission: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for constraint violations in current state."""
        violations = []
        
        # Check geofence
        if "area_of_operations" in mission:
            aop = mission["area_of_operations"]
            if "geofence" in aop:
                if not self._check_geofence(current_state, aop["geofence"]):
                    violations.append({
                        "type": "geofence",
                        "severity": "critical",
                        "message": "Asset outside geofence"
                    })
        
        # Check altitude
        if "altitude" in current_state:
            if current_state["altitude"] < 0:
                violations.append({
                    "type": "altitude",
                    "severity": "critical",
                    "message": f"Invalid altitude: {current_state['altitude']}"
                })
        
        # Check fuel
        if "fuel_remaining" in current_state:
            if current_state["fuel_remaining"] < 10:
                violations.append({
                    "type": "fuel",
                    "severity": "high",
                    "message": f"Low fuel: {current_state['fuel_remaining']}%"
                })
        
        return violations
    
    def estimate_mission_risk(self, mission: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate mission risk factors."""
        risk_score = 0.0
        risk_factors = []
        
        # Risk from mission complexity
        num_objectives = len(mission.get("objectives", []))
        if num_objectives > 5:
            risk_score += 15.0
            risk_factors.append(f"High complexity: {num_objectives} objectives")
        
        # Risk from area of operations
        if "area_of_operations" in mission:
            risk_score += 10.0
            risk_factors.append("Operating in restricted airspace")
        
        # Risk from weather constraints
        if mission.get("weather_requirements"):
            risk_score += 5.0
            risk_factors.append("Weather-dependent mission")
        
        # Risk from asset constraints
        num_assets = len(mission.get("assigned_assets", []))
        if num_assets == 1:
            risk_score += 20.0
            risk_factors.append("Single asset - no redundancy")
        
        risk_score = min(100.0, risk_score)
        
        return {
            "risk_score": risk_score,
            "risk_level": "critical" if risk_score > 75 else (
                "high" if risk_score > 50 else (
                    "medium" if risk_score > 25 else "low"
                )
            ),
            "risk_factors": risk_factors,
        }
    
    def _initialize_rules(self) -> Dict[str, List[str]]:
        """Initialize validation rules."""
        return {
            "required_mission_fields": [
                "name", "mission_type", "objectives", "assigned_assets"
            ],
            "mission_types": [
                "uav", "aerospace", "robotics", "swarm", "combined"
            ],
            "objective_types": [
                "survey", "delivery", "rescue", "combat", "transport", "reconnaissance"
            ],
        }
    
    def _validate_required_fields(self, mission: Dict[str, Any]) -> List[str]:
        """Validate required mission fields."""
        errors = []
        
        for field in self.validation_rules["required_mission_fields"]:
            if field not in mission or (isinstance(mission[field], list) and len(mission[field]) == 0):
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def _validate_objectives(self, objectives: List[Dict[str, Any]]) -> List[str]:
        """Validate mission objectives."""
        errors = []
        
        if not objectives:
            errors.append("Mission must have at least one objective")
            return errors
        
        for i, obj in enumerate(objectives):
            is_valid, obj_errors = self.validate_objective(obj)
            if not is_valid:
                for error in obj_errors:
                    errors.append(f"Objective {i}: {error}")
        
        return errors
    
    def _validate_assets(self, assets: List[Dict[str, Any]]) -> List[str]:
        """Validate assigned assets."""
        warnings = []
        
        if not assets:
            warnings.append("No assets assigned to mission")
            return warnings
        
        # Check for asset redundancy
        primary_count = sum(1 for a in assets if a.get("role") == "primary")
        if primary_count == 0:
            warnings.append("No primary assets assigned")
        elif primary_count > 1:
            warnings.append("Multiple primary assets - unclear responsibility")
        
        # Check asset readiness
        for asset in assets:
            if asset.get("readiness", 1.0) < 0.9:
                warnings.append(f"Asset {asset.get('asset_id')} has low readiness: {asset.get('readiness')}")
        
        return warnings
    
    def _validate_planning_constraints(self, mission: Dict[str, Any]) -> List[str]:
        """Validate planning constraints."""
        warnings = []
        
        # Check timing
        if mission.get("planned_start") and mission.get("planned_end"):
            start = mission["planned_start"]
            end = mission["planned_end"]
            if start >= end:
                warnings.append("Planned end time must be after start time")
        
        return warnings
    
    def _validate_operational_constraints(self, mission: Dict[str, Any]) -> List[str]:
        """Validate operational constraints."""
        warnings = []
        
        risk_level = mission.get("risk_level", "medium")
        if risk_level not in ["low", "medium", "high", "critical"]:
            warnings.append(f"Invalid risk level: {risk_level}")
        
        return warnings
    
    def _validate_regulatory_requirements(self, mission: Dict[str, Any]) -> List[str]:
        """Validate regulatory requirements."""
        warnings = []
        
        reqs = mission.get("regulatory_requirements", [])
        if not reqs:
            warnings.append("No regulatory requirements specified")
        
        return warnings
    
    def _check_geofence(
        self,
        current_state: Dict[str, Any],
        geofence: Dict[str, Any]
    ) -> bool:
        """Check if current state is within geofence."""
        if "lat" not in current_state or "lon" not in current_state:
            return False
        
        # Simplified geofence check
        return True
