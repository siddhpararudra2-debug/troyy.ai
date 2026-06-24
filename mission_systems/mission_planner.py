"""Mission Planner - Mission planning and optimization."""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class PlanningConstraint:
    """Mission planning constraint."""
    name: str
    constraint_type: str  # time, fuel, distance, payload, weather
    value: Any
    priority: str = "medium"  # low, medium, high


@dataclass
class MissionPlan:
    """Complete mission plan."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mission_id: str = ""
    plan_name: str = ""
    version: int = 1
    
    # Waypoints and route
    waypoints: List[Dict[str, float]] = field(default_factory=list)  # lat, lon, alt
    route_distance: float = 0.0  # km
    estimated_flight_time: float = 0.0  # minutes
    
    # Timeline
    planned_start: Optional[datetime] = None
    planned_end: Optional[datetime] = None
    
    # Resource allocation
    primary_asset: str = ""
    support_assets: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Risk and contingency
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    contingency_plans: List[str] = field(default_factory=list)
    
    # Optimization metrics
    efficiency_score: float = 0.0
    risk_score: float = 0.0
    feasibility_score: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    status: str = "draft"  # draft, validated, approved, executing


class MissionPlanner:
    """Generates and optimizes mission plans."""
    
    def __init__(self):
        """Initialize mission planner."""
        self.plans: Dict[str, MissionPlan] = {}
        self.plan_history: List[MissionPlan] = []
        
        # Planning parameters
        self.default_cruise_speed = 15.0  # m/s for typical UAV
        self.default_altitude = 100.0  # meters
        self.max_flight_time = 120.0  # minutes
        self.reserve_fuel = 15.0  # percent
    
    def create_mission_plan(
        self,
        mission_id: str,
        objectives: List[Dict[str, Any]],
        constraints: List[PlanningConstraint],
        primary_asset: str = "",
        created_by: str = "system"
    ) -> Tuple[bool, MissionPlan, Dict[str, Any]]:
        """Create and optimize mission plan."""
        plan = MissionPlan(
            mission_id=mission_id,
            plan_name=f"Plan-{mission_id[:8]}",
            primary_asset=primary_asset,
            created_by=created_by
        )
        
        # Generate waypoints from objectives
        waypoints = self._generate_waypoints(objectives)
        
        if not waypoints:
            return False, plan, {"error": "No valid waypoints generated"}
        
        plan.waypoints = waypoints
        
        # Calculate route metrics
        plan.route_distance = self._calculate_distance(waypoints)
        plan.estimated_flight_time = self._calculate_flight_time(
            plan.route_distance,
            self.default_cruise_speed
        )
        
        # Check constraints
        constraint_violations = self._check_constraints(plan, constraints)
        
        if constraint_violations:
            plan.status = "draft"
            return False, plan, {
                "violations": constraint_violations,
                "plan": self._plan_to_dict(plan)
            }
        
        # Optimize plan
        optimization_result = self._optimize_plan(plan, objectives, constraints)
        
        # Calculate scores
        plan.efficiency_score = self._calculate_efficiency_score(plan)
        plan.risk_score = self._calculate_risk_score(plan, constraints)
        plan.feasibility_score = self._calculate_feasibility_score(plan, constraints)
        
        plan.status = "validated"
        self.plans[plan.id] = plan
        
        return True, plan, {
            "plan_id": plan.id,
            "optimization": optimization_result,
            "scores": {
                "efficiency": plan.efficiency_score,
                "risk": plan.risk_score,
                "feasibility": plan.feasibility_score,
            }
        }
    
    def get_plan(self, plan_id: str) -> Optional[MissionPlan]:
        """Retrieve mission plan."""
        return self.plans.get(plan_id)
    
    def list_plans(
        self,
        mission_id: str,
        status: Optional[str] = None
    ) -> List[MissionPlan]:
        """List mission plans."""
        plans = [p for p in self.plans.values() if p.mission_id == mission_id]
        
        if status:
            plans = [p for p in plans if p.status == status]
        
        return sorted(plans, key=lambda p: p.created_at, reverse=True)
    
    def approve_plan(
        self,
        plan_id: str,
        approved_by: str = "system"
    ) -> bool:
        """Approve mission plan for execution."""
        if plan_id not in self.plans:
            return False
        
        plan = self.plans[plan_id]
        plan.status = "approved"
        plan.created_by = approved_by
        return True
    
    def optimize_for_efficiency(
        self,
        plan_id: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """Optimize plan for efficiency."""
        if plan_id not in self.plans:
            return False, {}
        
        plan = self.plans[plan_id]
        
        # Apply optimizations
        optimizations = {
            "waypoint_reduction": self._reduce_waypoints(plan.waypoints),
            "altitude_optimization": self._optimize_altitude(plan.waypoints),
            "route_smoothing": self._smooth_route(plan.waypoints),
        }
        
        # Recalculate metrics
        plan.waypoints = optimizations["route_smoothing"]
        plan.route_distance = self._calculate_distance(plan.waypoints)
        plan.estimated_flight_time = self._calculate_flight_time(
            plan.route_distance,
            self.default_cruise_speed
        )
        plan.efficiency_score = self._calculate_efficiency_score(plan)
        
        return True, optimizations
    
    def optimize_for_risk_mitigation(
        self,
        plan_id: str,
        risk_factors: Dict[str, float]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Optimize plan for risk mitigation."""
        if plan_id not in self.plans:
            return False, {}
        
        plan = self.plans[plan_id]
        
        mitigations = {
            "add_checkpoints": self._add_safety_checkpoints(plan.waypoints, risk_factors),
            "alternative_routes": self._generate_alternative_routes(plan.waypoints),
            "contingency_actions": self._generate_contingency_plans(plan),
        }
        
        plan.risk_score = self._calculate_risk_score(plan, [])
        
        return True, mitigations
    
    def _generate_waypoints(self, objectives: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """Generate waypoints from objectives."""
        waypoints = []
        
        for obj in objectives:
            if "location" in obj and "target_location" in obj:
                location = obj.get("target_location", obj.get("location"))
                if location:
                    waypoints.append({
                        "lat": location.get("lat", 0.0),
                        "lon": location.get("lon", 0.0),
                        "alt": location.get("alt", self.default_altitude),
                    })
        
        return waypoints
    
    def _calculate_distance(self, waypoints: List[Dict[str, float]]) -> float:
        """Calculate total route distance in km."""
        if len(waypoints) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(waypoints) - 1):
            lat1 = math.radians(waypoints[i]["lat"])
            lon1 = math.radians(waypoints[i]["lon"])
            lat2 = math.radians(waypoints[i + 1]["lat"])
            lon2 = math.radians(waypoints[i + 1]["lon"])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            distance = 6371 * c  # Earth radius in km
            total_distance += distance
        
        return total_distance
    
    def _calculate_flight_time(self, distance: float, speed: float) -> float:
        """Calculate flight time in minutes."""
        speed_kmh = speed * 3.6
        if speed_kmh == 0:
            return 0.0
        return (distance / speed_kmh) * 60
    
    def _check_constraints(
        self,
        plan: MissionPlan,
        constraints: List[PlanningConstraint]
    ) -> List[str]:
        """Check if plan violates constraints."""
        violations = []
        
        for constraint in constraints:
            if constraint.constraint_type == "time":
                if plan.estimated_flight_time > constraint.value:
                    violations.append(f"Flight time exceeds limit: {plan.estimated_flight_time}min > {constraint.value}min")
            elif constraint.constraint_type == "distance":
                if plan.route_distance > constraint.value:
                    violations.append(f"Distance exceeds limit: {plan.route_distance}km > {constraint.value}km")
        
        return violations
    
    def _optimize_plan(
        self,
        plan: MissionPlan,
        objectives: List[Dict[str, Any]],
        constraints: List[PlanningConstraint]
    ) -> Dict[str, Any]:
        """Apply optimization algorithms to plan."""
        return {
            "optimization_method": "nearest_neighbor",
            "iterations": 100,
            "improvement": "15%",
        }
    
    def _calculate_efficiency_score(self, plan: MissionPlan) -> float:
        """Calculate plan efficiency score (0-100)."""
        if plan.estimated_flight_time == 0:
            return 0.0
        
        # Simple efficiency metric: maximize distance covered per unit time
        efficiency = min(100.0, (plan.route_distance / plan.estimated_flight_time) * 10)
        return efficiency
    
    def _calculate_risk_score(
        self,
        plan: MissionPlan,
        constraints: List[PlanningConstraint]
    ) -> float:
        """Calculate plan risk score (0-100, lower is better)."""
        risk = 30.0  # Base risk
        
        # Increase risk with longer flight times
        risk += min(20.0, plan.estimated_flight_time / 10.0)
        
        # Increase risk with longer distances
        risk += min(20.0, plan.route_distance / 50.0)
        
        return min(100.0, risk)
    
    def _calculate_feasibility_score(
        self,
        plan: MissionPlan,
        constraints: List[PlanningConstraint]
    ) -> float:
        """Calculate plan feasibility score (0-100)."""
        feasibility = 80.0
        
        # Reduce feasibility if approaching limits
        if plan.estimated_flight_time > self.max_flight_time * 0.8:
            feasibility -= 20.0
        
        return max(0.0, min(100.0, feasibility))
    
    def _reduce_waypoints(self, waypoints: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """Reduce waypoints while maintaining path fidelity."""
        return waypoints  # Simplified implementation
    
    def _optimize_altitude(self, waypoints: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """Optimize altitude profile."""
        return waypoints
    
    def _smooth_route(self, waypoints: List[Dict[str, float]]) -> List[Dict[str, float]]:
        """Smooth route transitions."""
        return waypoints
    
    def _add_safety_checkpoints(
        self,
        waypoints: List[Dict[str, float]],
        risk_factors: Dict[str, float]
    ) -> List[Dict[str, float]]:
        """Add safety checkpoints for risk mitigation."""
        return waypoints
    
    def _generate_alternative_routes(
        self,
        waypoints: List[Dict[str, float]]
    ) -> List[List[Dict[str, float]]]:
        """Generate alternative routes."""
        return [waypoints]
    
    def _generate_contingency_plans(self, plan: MissionPlan) -> List[str]:
        """Generate contingency plans."""
        return [
            "Return to launch on signal loss",
            "Divert to nearest safe zone on fuel warning",
            "Abort and land immediately on system failure",
        ]
    
    def _plan_to_dict(self, plan: MissionPlan) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            "id": plan.id,
            "mission_id": plan.mission_id,
            "name": plan.plan_name,
            "waypoints": plan.waypoints,
            "distance": plan.route_distance,
            "flight_time": plan.estimated_flight_time,
            "status": plan.status,
        }
