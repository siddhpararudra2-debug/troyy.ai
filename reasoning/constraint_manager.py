"""
Constraint Manager for Engineering OS.
Manages design constraints and feasibility analysis.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from datetime import datetime
import uuid


class ConstraintType(str, Enum):
    """Types of engineering constraints."""
    EQUALITY = "equality"  # x = value
    INEQUALITY_MIN = "inequality_min"  # x >= value
    INEQUALITY_MAX = "inequality_max"  # x <= value
    RANGE = "range"  # min <= x <= max
    RATIO = "ratio"  # x1/x2 = ratio
    COMBINED = "combined"  # Complex relationship


class ConstraintStatus(str, Enum):
    """Status of constraint satisfaction."""
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    MARGINAL = "marginal"  # Close to boundary
    UNKNOWN = "unknown"


class Priority(str, Enum):
    """Constraint priority levels."""
    MUST_HAVE = "must_have"  # Hard constraint
    SHOULD_HAVE = "should_have"  # Soft constraint
    NICE_TO_HAVE = "nice_to_have"  # Very soft


@dataclass
class Constraint:
    """An engineering constraint."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Constraint definition
    constraint_type: ConstraintType = ConstraintType.RANGE
    variable: str = ""  # Parameter name
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    target_value: Optional[float] = None
    
    # Relationship constraints
    related_variables: List[str] = field(default_factory=list)  # For ratio/combined
    relationship_function: Optional[str] = None  # Python expression
    
    # Priority and flexibility
    priority: Priority = Priority.MUST_HAVE
    is_flexible: bool = False
    relaxation_possible: Optional[float] = None  # How much can be relaxed (%)
    
    # Justification
    justification: str = ""
    source: str = ""  # Standard, customer, engineering analysis
    
    # Status
    status: ConstraintStatus = ConstraintStatus.UNKNOWN
    violation_amount: Optional[float] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstraintViolation:
    """A constraint violation."""
    constraint: Constraint
    actual_value: float
    violation_amount: float
    severity: str  # "minor", "moderate", "severe"
    affected_designs: List[str] = field(default_factory=list)


@dataclass
class FeasibilityAnalysis:
    """Analysis of design feasibility."""
    design_id: str = ""
    design_name: str = ""
    
    # Constraint satisfaction
    all_constraints: List[Constraint] = field(default_factory=list)
    satisfied_constraints: List[Constraint] = field(default_factory=list)
    violated_constraints: List[ConstraintViolation] = field(default_factory=list)
    marginal_constraints: List[Constraint] = field(default_factory=list)
    
    # Overall feasibility
    is_feasible: bool = True
    feasibility_score: float = 1.0  # 0-1
    
    # Hard vs soft constraints
    hard_constraints_satisfied: bool = True
    soft_constraint_satisfaction: float = 1.0
    
    # Recommendations
    required_modifications: List[str] = field(default_factory=list)
    optional_improvements: List[str] = field(default_factory=list)


class ConstraintManager:
    """Manages engineering design constraints."""

    def __init__(self):
        self.constraints: Dict[str, Constraint] = {}
        self.constraint_count = 0

    async def add_constraint(
        self,
        name: str,
        description: str,
        variable: str,
        constraint_type: ConstraintType,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
        target_value: Optional[float] = None,
        priority: Priority = Priority.SHOULD_HAVE,
        justification: str = ""
    ) -> Constraint:
        """Add a new constraint."""
        self.constraint_count += 1
        
        constraint = Constraint(
            name=name,
            description=description,
            variable=variable,
            constraint_type=constraint_type,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            target_value=target_value,
            priority=priority,
            justification=justification
        )
        
        self.constraints[constraint.id] = constraint
        return constraint

    async def check_constraint(
        self,
        constraint: Constraint,
        actual_value: float
    ) -> ConstraintStatus:
        """Check if a constraint is satisfied."""
        status = ConstraintStatus.SATISFIED
        violation_amount = 0.0
        
        if constraint.constraint_type == ConstraintType.RANGE:
            if constraint.lower_bound is not None and actual_value < constraint.lower_bound:
                status = ConstraintStatus.VIOLATED
                violation_amount = constraint.lower_bound - actual_value
            elif constraint.upper_bound is not None and actual_value > constraint.upper_bound:
                status = ConstraintStatus.VIOLATED
                violation_amount = actual_value - constraint.upper_bound
            
            # Check for marginal satisfaction
            if status == ConstraintStatus.SATISFIED:
                margin_percent = 0.05  # 5% margin
                if constraint.lower_bound is not None:
                    margin = (constraint.upper_bound - constraint.lower_bound) * margin_percent if constraint.upper_bound else constraint.lower_bound * margin_percent
                    if actual_value - constraint.lower_bound < margin:
                        status = ConstraintStatus.MARGINAL
                
                if constraint.upper_bound is not None:
                    margin = (constraint.upper_bound - constraint.lower_bound) * margin_percent if constraint.lower_bound else constraint.upper_bound * margin_percent
                    if constraint.upper_bound - actual_value < margin:
                        status = ConstraintStatus.MARGINAL
        
        elif constraint.constraint_type == ConstraintType.EQUALITY:
            if constraint.target_value is not None:
                tolerance = abs(constraint.target_value) * 0.01  # 1% tolerance
                if abs(actual_value - constraint.target_value) > tolerance:
                    status = ConstraintStatus.VIOLATED
                    violation_amount = abs(actual_value - constraint.target_value)
        
        elif constraint.constraint_type == ConstraintType.INEQUALITY_MIN:
            if constraint.lower_bound is not None and actual_value < constraint.lower_bound:
                status = ConstraintStatus.VIOLATED
                violation_amount = constraint.lower_bound - actual_value
        
        elif constraint.constraint_type == ConstraintType.INEQUALITY_MAX:
            if constraint.upper_bound is not None and actual_value > constraint.upper_bound:
                status = ConstraintStatus.VIOLATED
                violation_amount = actual_value - constraint.upper_bound
        
        constraint.status = status
        constraint.violation_amount = violation_amount if status == ConstraintStatus.VIOLATED else None
        
        return status

    async def analyze_feasibility(
        self,
        design_id: str,
        design_name: str,
        parameter_values: Dict[str, float]
    ) -> FeasibilityAnalysis:
        """Analyze if a design is feasible given constraints."""
        analysis = FeasibilityAnalysis(
            design_id=design_id,
            design_name=design_name
        )
        
        # Check each constraint
        for constraint in self.constraints.values():
            if constraint.variable in parameter_values:
                actual_value = parameter_values[constraint.variable]
                status = await self.check_constraint(constraint, actual_value)
                
                if status == ConstraintStatus.SATISFIED:
                    analysis.satisfied_constraints.append(constraint)
                elif status == ConstraintStatus.VIOLATED:
                    violation = ConstraintViolation(
                        constraint=constraint,
                        actual_value=actual_value,
                        violation_amount=constraint.violation_amount or 0.0,
                        severity=self._determine_violation_severity(constraint, actual_value)
                    )
                    analysis.violated_constraints.append(violation)
                elif status == ConstraintStatus.MARGINAL:
                    analysis.marginal_constraints.append(constraint)
                
                analysis.all_constraints.append(constraint)
        
        # Calculate overall feasibility
        hard_constraint_violations = [
            v for v in analysis.violated_constraints 
            if v.constraint.priority == Priority.MUST_HAVE
        ]
        
        analysis.hard_constraints_satisfied = len(hard_constraint_violations) == 0
        
        if not analysis.hard_constraints_satisfied:
            analysis.is_feasible = False
        
        # Calculate feasibility score
        total_constraints = len(analysis.all_constraints)
        if total_constraints > 0:
            satisfied = len(analysis.satisfied_constraints)
            marginal = len(analysis.marginal_constraints) * 0.5
            analysis.feasibility_score = (satisfied + marginal) / total_constraints
        
        # Generate recommendations
        analysis = await self._generate_feasibility_recommendations(analysis, parameter_values)
        
        return analysis

    def _determine_violation_severity(self, constraint: Constraint, actual_value: float) -> str:
        """Determine severity of constraint violation."""
        if constraint.violation_amount is None:
            return "unknown"
        
        violation_percent = 0.0
        if constraint.upper_bound is not None and constraint.lower_bound is not None:
            range_size = constraint.upper_bound - constraint.lower_bound
            violation_percent = constraint.violation_amount / range_size if range_size > 0 else 0
        elif constraint.target_value is not None:
            violation_percent = constraint.violation_amount / abs(constraint.target_value) if constraint.target_value != 0 else 0
        
        if violation_percent < 0.05:
            return "minor"
        elif violation_percent < 0.20:
            return "moderate"
        else:
            return "severe"

    async def _generate_feasibility_recommendations(
        self,
        analysis: FeasibilityAnalysis,
        parameter_values: Dict[str, float]
    ) -> FeasibilityAnalysis:
        """Generate recommendations to achieve feasibility."""
        
        # Required modifications (for must-have constraints)
        for violation in analysis.violated_constraints:
            if violation.constraint.priority == Priority.MUST_HAVE:
                var = violation.constraint.variable
                current = parameter_values.get(var, 0)
                
                if violation.constraint.constraint_type == ConstraintType.INEQUALITY_MIN:
                    needed = violation.constraint.lower_bound + violation.violation_amount * 1.1
                    analysis.required_modifications.append(
                        f"Increase {var} from {current:.2f} to at least {needed:.2f}"
                    )
                elif violation.constraint.constraint_type == ConstraintType.INEQUALITY_MAX:
                    needed = violation.constraint.upper_bound - violation.violation_amount * 1.1
                    analysis.required_modifications.append(
                        f"Decrease {var} from {current:.2f} to at most {needed:.2f}"
                    )
        
        # Optional improvements (for soft constraints)
        for violation in analysis.violated_constraints:
            if violation.constraint.priority in [Priority.SHOULD_HAVE, Priority.NICE_TO_HAVE]:
                analysis.optional_improvements.append(
                    f"Consider adjusting {violation.constraint.variable} to satisfy {violation.constraint.name}"
                )
        
        return analysis

    async def relax_constraints(
        self,
        relaxation_map: Dict[str, float]
    ) -> Dict[str, Constraint]:
        """Temporarily relax constraints for feasibility analysis."""
        relaxed_constraints = {}
        
        for constraint_id, relaxation_percent in relaxation_map.items():
            if constraint_id in self.constraints:
                constraint = self.constraints[constraint_id]
                
                if constraint.is_flexible or constraint.relaxation_possible:
                    # Create relaxed version
                    relaxed = Constraint(
                        name=constraint.name,
                        description=constraint.description + " (relaxed)",
                        variable=constraint.variable,
                        constraint_type=constraint.constraint_type,
                        lower_bound=constraint.lower_bound,
                        upper_bound=constraint.upper_bound,
                        priority=constraint.priority
                    )
                    
                    # Apply relaxation
                    if constraint.lower_bound is not None:
                        relaxed.lower_bound = constraint.lower_bound * (1 - relaxation_percent / 100)
                    if constraint.upper_bound is not None:
                        relaxed.upper_bound = constraint.upper_bound * (1 + relaxation_percent / 100)
                    
                    relaxed_constraints[constraint_id] = relaxed
        
        return relaxed_constraints
