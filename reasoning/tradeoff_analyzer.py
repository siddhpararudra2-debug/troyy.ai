"""
Trade-off Analysis Engine for Engineering OS.
Analyzes design trade-offs and conflicts.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import uuid


class TradeoffDimension(str, Enum):
    """Dimensions of engineering trade-offs."""
    WEIGHT_VS_STRENGTH = "weight_vs_strength"
    COST_VS_PERFORMANCE = "cost_vs_performance"
    COST_VS_RELIABILITY = "cost_vs_reliability"
    SIZE_VS_POWER = "size_vs_power"
    WEIGHT_VS_COST = "weight_vs_cost"
    PERFORMANCE_VS_MANUFACTURABILITY = "performance_vs_manufacturability"
    PERFORMANCE_VS_RELIABILITY = "performance_vs_reliability"
    THERMAL_VS_WEIGHT = "thermal_vs_weight"
    FLEXIBILITY_VS_STIFFNESS = "flexibility_vs_stiffness"
    CYCLE_TIME_VS_QUALITY = "cycle_time_vs_quality"


@dataclass
class TradeoffPoint:
    """A point in trade-off analysis."""
    x_value: float  # Value on X-axis (e.g., weight)
    y_value: float  # Value on Y-axis (e.g., cost)
    pareto_optimal: bool = False  # Is this point on Pareto frontier?
    design_name: str = ""
    design_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TradeoffCurve:
    """A trade-off curve (Pareto frontier)."""
    dimension: TradeoffDimension = TradeoffDimension.WEIGHT_VS_COST
    x_label: str = ""
    y_label: str = ""
    points: List[TradeoffPoint] = field(default_factory=list)
    pareto_frontier: List[TradeoffPoint] = field(default_factory=list)
    sweet_spot: Optional[TradeoffPoint] = None


@dataclass
class ConstraintConflict:
    """A conflict between constraints."""
    constraint_a: str = ""
    constraint_b: str = ""
    conflict_type: str = ""  # "antagonistic", "synergistic", "independent"
    severity: float = 0.5  # 0-1
    description: str = ""
    resolution_options: List[str] = field(default_factory=list)


@dataclass
class TradeoffAnalysisResult:
    """Result of a trade-off analysis."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    design_id: str = ""
    analysis_type: str = ""
    tradeoff_curves: List[TradeoffCurve] = field(default_factory=list)
    conflicts: List[ConstraintConflict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    dominated_options: List[str] = field(default_factory=list)  # Non-optimal options
    pareto_optimal_set: List[str] = field(default_factory=list)  # Optimal options
    created_at: datetime = field(default_factory=datetime.utcnow)


class TradeoffAnalyzer:
    """Analyzes engineering design trade-offs."""

    def __init__(self):
        self.analysis_count = 0

    async def analyze_weight_vs_cost(
        self,
        designs: Dict[str, Dict[str, float]]
    ) -> TradeoffCurve:
        """
        Analyze weight vs cost trade-off.
        
        designs: {design_id: {"weight": float, "cost": float}}
        """
        points = []
        
        for design_id, metrics in designs.items():
            if "weight" in metrics and "cost" in metrics:
                point = TradeoffPoint(
                    x_value=metrics["weight"],
                    y_value=metrics["cost"],
                    design_name=design_id
                )
                points.append(point)
        
        # Find Pareto frontier (non-dominated solutions)
        pareto_frontier = self._find_pareto_frontier(points, minimize=[True, True])
        
        # Mark Pareto-optimal points
        for point in points:
            point.pareto_optimal = point in pareto_frontier
        
        curve = TradeoffCurve(
            dimension=TradeoffDimension.WEIGHT_VS_COST,
            x_label="Weight (kg)",
            y_label="Cost ($)",
            points=points,
            pareto_frontier=pareto_frontier
        )
        
        # Find sweet spot (balanced solution)
        if pareto_frontier:
            curve.sweet_spot = self._find_sweet_spot(pareto_frontier)
        
        return curve

    async def analyze_cost_vs_performance(
        self,
        designs: Dict[str, Dict[str, float]]
    ) -> TradeoffCurve:
        """Analyze cost vs performance trade-off."""
        points = []
        
        for design_id, metrics in designs.items():
            if "cost" in metrics and "performance" in metrics:
                point = TradeoffPoint(
                    x_value=metrics["cost"],
                    y_value=metrics["performance"],
                    design_name=design_id
                )
                points.append(point)
        
        # For cost/performance, we want to minimize cost and maximize performance
        pareto_frontier = self._find_pareto_frontier(points, minimize=[True, False])
        
        for point in points:
            point.pareto_optimal = point in pareto_frontier
        
        curve = TradeoffCurve(
            dimension=TradeoffDimension.COST_VS_PERFORMANCE,
            x_label="Cost ($)",
            y_label="Performance (0-100)",
            points=points,
            pareto_frontier=pareto_frontier
        )
        
        if pareto_frontier:
            curve.sweet_spot = self._find_sweet_spot(pareto_frontier)
        
        return curve

    async def analyze_cost_vs_reliability(
        self,
        designs: Dict[str, Dict[str, float]]
    ) -> TradeoffCurve:
        """Analyze cost vs reliability trade-off."""
        points = []
        
        for design_id, metrics in designs.items():
            if "cost" in metrics and "reliability" in metrics:
                point = TradeoffPoint(
                    x_value=metrics["cost"],
                    y_value=metrics["reliability"],  # 0-1 scale
                    design_name=design_id
                )
                points.append(point)
        
        # Minimize cost, maximize reliability
        pareto_frontier = self._find_pareto_frontier(points, minimize=[True, False])
        
        for point in points:
            point.pareto_optimal = point in pareto_frontier
        
        curve = TradeoffCurve(
            dimension=TradeoffDimension.COST_VS_RELIABILITY,
            x_label="Cost ($)",
            y_label="Reliability (0-1)",
            points=points,
            pareto_frontier=pareto_frontier
        )
        
        if pareto_frontier:
            curve.sweet_spot = self._find_sweet_spot(pareto_frontier)
        
        return curve

    async def detect_constraint_conflicts(
        self,
        constraints: Dict[str, Dict[str, Any]]
    ) -> List[ConstraintConflict]:
        """
        Detect conflicts between design constraints.
        
        constraints: {
            "constraint_name": {
                "value": float,
                "limit": float,
                "type": str  # "min", "max", "equal"
            }
        }
        """
        conflicts = []
        
        # Known conflict patterns
        conflict_patterns = [
            ("weight", "strength", "antagonistic", "Reducing weight often reduces strength"),
            ("cost", "reliability", "antagonistic", "Lower cost often reduces reliability"),
            ("size", "capacity", "antagonistic", "Smaller size limits capacity"),
            ("speed", "efficiency", "antagonistic", "Higher speed reduces efficiency"),
            ("flexibility", "stiffness", "antagonistic", "Cannot maximize both simultaneously"),
            ("manufacturing_time", "quality", "antagonistic", "Faster production reduces quality"),
            ("thermal_resistance", "weight", "antagonistic", "Better thermal performance adds weight"),
        ]
        
        constraint_names = list(constraints.keys())
        
        for pattern in conflict_patterns:
            constraint_a_name, constraint_b_name, conflict_type, description = pattern
            
            # Check if both constraints are present
            a_matches = [c for c in constraint_names if constraint_a_name.lower() in c.lower()]
            b_matches = [c for c in constraint_names if constraint_b_name.lower() in c.lower()]
            
            if a_matches and b_matches:
                for a in a_matches:
                    for b in b_matches:
                        conflict = ConstraintConflict(
                            constraint_a=a,
                            constraint_b=b,
                            conflict_type=conflict_type,
                            severity=0.6,
                            description=description,
                            resolution_options=[
                                f"Accept trade-off between {constraint_a_name} and {constraint_b_name}",
                                f"Increase {constraint_a_name} limit to reduce {constraint_b_name}",
                                f"Use advanced materials or methods to decouple {constraint_a_name} and {constraint_b_name}"
                            ]
                        )
                        conflicts.append(conflict)
        
        return conflicts

    def _find_pareto_frontier(
        self,
        points: List[TradeoffPoint],
        minimize: List[bool]
    ) -> List[TradeoffPoint]:
        """
        Find Pareto frontier (non-dominated solutions).
        
        minimize: [True/False for x, True/False for y]
        """
        frontier = []
        
        for candidate in points:
            dominated = False
            
            for other in points:
                if candidate == other:
                    continue
                
                # Check if 'other' dominates 'candidate'
                x_dominates = (
                    (minimize[0] and other.x_value < candidate.x_value) or
                    (not minimize[0] and other.x_value > candidate.x_value)
                )
                y_dominates = (
                    (minimize[1] and other.y_value < candidate.y_value) or
                    (not minimize[1] and other.y_value > candidate.y_value)
                )
                
                if x_dominates and y_dominates:
                    dominated = True
                    break
                elif (x_dominates and not minimize[1] and other.y_value >= candidate.y_value) or \
                     (y_dominates and not minimize[0] and other.x_value >= candidate.x_value):
                    dominated = True
                    break
            
            if not dominated:
                frontier.append(candidate)
        
        return sorted(frontier, key=lambda p: p.x_value)

    def _find_sweet_spot(self, pareto_frontier: List[TradeoffPoint]) -> TradeoffPoint:
        """Find the 'sweet spot' - balanced solution on Pareto frontier."""
        if len(pareto_frontier) == 1:
            return pareto_frontier[0]
        
        # Find point closest to median performance
        median_x = sum(p.x_value for p in pareto_frontier) / len(pareto_frontier)
        median_y = sum(p.y_value for p in pareto_frontier) / len(pareto_frontier)
        
        sweet_spot = min(
            pareto_frontier,
            key=lambda p: (p.x_value - median_x)**2 + (p.y_value - median_y)**2
        )
        
        return sweet_spot

    async def generate_tradeoff_report(
        self,
        design_id: str,
        curves: List[TradeoffCurve],
        conflicts: List[ConstraintConflict]
    ) -> Dict[str, Any]:
        """Generate trade-off analysis report."""
        return {
            "design_id": design_id,
            "tradeoff_analyses": [
                {
                    "dimension": curve.dimension.value,
                    "x_label": curve.x_label,
                    "y_label": curve.y_label,
                    "points_count": len(curve.points),
                    "pareto_optimal_count": len(curve.pareto_frontier),
                    "sweet_spot": {
                        "name": curve.sweet_spot.design_name,
                        "x": curve.sweet_spot.x_value,
                        "y": curve.sweet_spot.y_value
                    } if curve.sweet_spot else None
                }
                for curve in curves
            ],
            "conflicts": [
                {
                    "constraint_a": c.constraint_a,
                    "constraint_b": c.constraint_b,
                    "type": c.conflict_type,
                    "severity": c.severity,
                    "resolution_options": c.resolution_options
                }
                for c in conflicts
            ],
            "recommendations": self._generate_tradeoff_recommendations(curves, conflicts)
        }

    def _generate_tradeoff_recommendations(
        self,
        curves: List[TradeoffCurve],
        conflicts: List[ConstraintConflict]
    ) -> List[str]:
        """Generate recommendations from trade-off analysis."""
        recommendations = []
        
        for curve in curves:
            if curve.pareto_frontier:
                recommendations.append(
                    f"Consider Pareto-optimal solutions: {', '.join(p.design_name for p in curve.pareto_frontier[:3])}"
                )
                if curve.sweet_spot:
                    recommendations.append(
                        f"Balanced solution (sweet spot): {curve.sweet_spot.design_name}"
                    )
        
        high_severity_conflicts = [c for c in conflicts if c.severity > 0.7]
        if high_severity_conflicts:
            recommendations.append(
                f"Address high-severity conflicts: {', '.join(c.constraint_a for c in high_severity_conflicts)}"
            )
        
        return recommendations
