"""
Engineering Decision Engine for Engineering OS.
Makes recommendations and supports design decisions.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime
import uuid


class DecisionType(str, Enum):
    """Types of engineering decisions."""
    MATERIAL_SELECTION = "material_selection"
    GEOMETRY_OPTIMIZATION = "geometry_optimization"
    MANUFACTURING_METHOD = "manufacturing_method"
    MANUFACTURING = "manufacturing"
    DESIGN_ALTERNATIVE = "design_alternative"
    PERFORMANCE_TARGET = "performance_target"
    COST_REDUCTION = "cost_reduction"
    RISK_MITIGATION = "risk_mitigation"


class DecisionStatus(str, Enum):
    """Status of a decision."""
    OPEN = "open"
    PROPOSED = "proposed"
    ANALYZED = "analyzed"
    EVALUATED = "evaluated"
    RECOMMENDED = "recommended"
    DOCUMENTED = "documented"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    CANCELLED = "cancelled"


class Constraint(str, Enum):
    """Engineering constraints."""
    WEIGHT = "weight"
    COST = "cost"
    SIZE = "size"
    STRENGTH = "strength"
    THERMAL = "thermal"
    ELECTRICAL = "electrical"
    MANUFACTURING = "manufacturing"
    SUSTAINABILITY = "sustainability"
    SAFETY = "safety"
    RELIABILITY = "reliability"


@dataclass
class DecisionCriterion:
    name: str
    weight: float


class CriteriaDict(dict):
    def __iter__(self):
        return (DecisionCriterion(k, v) for k, v in self.items()).__iter__()


@dataclass
class DesignOption:
    """A design option to evaluate."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Performance metrics (0-100 scale)
    metrics: Dict[str, float] = field(default_factory=dict)  # e.g., {"weight": 2.5, "cost": 150, "strength": 95}
    
    # Constraint compliance
    constraints_met: List[Constraint] = field(default_factory=list)
    constraint_violations: List[Tuple[Constraint, str]] = field(default_factory=list)
    
    # Risk assessment
    risk_factors: List[str] = field(default_factory=list)
    reliability_estimate: float = 0.85  # 0-1
    failure_modes: List[str] = field(default_factory=list)
    
    # Implementation
    implementation_difficulty: float = 0.5  # 0-1
    implementation_time_months: float = 0.0
    implementation_cost: float = 0.0
    
    # Metadata
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    notes: str = ""
    option_id: Optional[str] = None

    def __post_init__(self):
        if self.option_id is not None:
            self.id = self.option_id
        else:
            self.option_id = self.id


@dataclass
class TradeoffAnalysis:
    """Analysis of trade-offs between options."""
    option_a_id: str = ""
    option_a_name: str = ""
    option_b_id: str = ""
    option_b_name: str = ""
    
    # Trade-off dimensions
    weight_vs_cost: float = 0.0  # negative=weight favors A, positive=cost favors A
    performance_vs_reliability: float = 0.0
    cost_vs_manufacturing_ease: float = 0.0
    
    # Detailed comparison
    advantages_a: List[str] = field(default_factory=list)
    advantages_b: List[str] = field(default_factory=list)
    
    # Recommendation
    recommended: str = ""  # "A", "B", or "Neither"
    rationale: str = ""


@dataclass
class EngineeringDecision:
    """A documented engineering decision."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str = ""
    
    # Context
    project_id: str = ""
    design_id: str = ""
    decision_type: DecisionType = DecisionType.DESIGN_ALTERNATIVE
    
    # Metadata
    title: str = ""
    description: str = ""
    context: str = ""  # Background and motivation
    
    # Decision-making
    options_evaluated: List[DesignOption] = field(default_factory=list)
    recommended_option_id: str = ""
    tradeoff_analyses: List[TradeoffAnalysis] = field(default_factory=list)
    
    # Criteria and weighting
    criteria: Dict[str, float] = field(default_factory=dict)  # e.g., {"weight": 0.3, "cost": 0.4, "reliability": 0.3}
    
    # Constraints
    constraints: List[Constraint] = field(default_factory=list)
    
    # Evaluation results
    scores: Dict[str, float] = field(default_factory=dict)
    
    # Decision outcome
    selected_option_id: str = ""
    decision_rationale: str = ""
    risks: List[str] = field(default_factory=list)
    
    # Status and tracking
    status: DecisionStatus = DecisionStatus.OPEN
    approved_by: Optional[str] = None
    
    # Timeline
    created_at: datetime = field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None

    @property
    def options(self) -> List[DesignOption]:
        return self.options_evaluated

    @options.setter
    def options(self, value: List[DesignOption]):
        self.options_evaluated = value


class EngineeringDecisionEngine:
    """Makes engineering design recommendations."""

    def __init__(self):
        self.decision_count = 0
        self.standard_criteria = self._initialize_criteria()

    def _initialize_criteria(self) -> Dict[DecisionType, CriteriaDict]:
        """Initialize standard weighting criteria for decision types."""
        return {
            DecisionType.MATERIAL_SELECTION: CriteriaDict({
                "Strength": 0.3,
                "Weight": 0.3,
                "Cost": 0.2,
                "Reliability": 0.2
            }),
            DecisionType.GEOMETRY_OPTIMIZATION: CriteriaDict({
                "Weight": 0.4,
                "Cost": 0.2,
                "Strength": 0.2,
                "Manufacturing": 0.2
            }),
            DecisionType.MANUFACTURING: CriteriaDict({
                "Cost": 0.4,
                "Quality": 0.3,
                "Time": 0.3
            }),
            DecisionType.MANUFACTURING_METHOD: CriteriaDict({
                "Cost": 0.4,
                "Quality": 0.3,
                "Time": 0.3
            }),
            DecisionType.DESIGN_ALTERNATIVE: CriteriaDict({
                "Performance": 0.4,
                "Cost": 0.3,
                "Reliability": 0.3
            })
        }

    async def create_decision(
        self,
        decision_id: str,
        design_id: str,
        title: str,
        decision_type: DecisionType,
        description: str = "",
        context: str = ""
    ) -> EngineeringDecision:
        """Create a new engineering decision."""
        self.decision_count += 1
        
        decision = EngineeringDecision(
            decision_id=decision_id,
            design_id=design_id,
            title=title,
            description=description,
            decision_type=decision_type,
            context=context,
            criteria=self.standard_criteria.get(decision_type, CriteriaDict()),
            constraints=[Constraint.WEIGHT, Constraint.COST]
        )
        
        return decision

    async def add_option(
        self,
        decision: EngineeringDecision,
        option: DesignOption
    ) -> EngineeringDecision:
        """Add an option to evaluate."""
        decision.options_evaluated.append(option)
        return decision

    async def evaluate_options(
        self,
        decision: EngineeringDecision,
        weighting_override: Optional[Dict[str, float]] = None
    ) -> EngineeringDecision:
        """Evaluate all options using weighted criteria."""
        weighting = weighting_override or decision.criteria
        
        if not weighting:
            weighting = {metric: 1.0 / len(decision.options_evaluated[0].metrics) 
                        for metric in decision.options_evaluated[0].metrics}
        
        # Score each option
        scored_options = []
        for option in decision.options_evaluated:
            # Calculate weighted score
            score = 0.0
            for criterion, weight in weighting.items():
                if criterion in option.metrics:
                    # Normalize metric to 0-100 scale
                    metric_value = option.metrics[criterion]
                    score += (metric_value / 100.0) * weight
            
            # Apply constraint penalties
            penalty = len(option.constraint_violations) * 0.1
            score = max(0, score - penalty)
            
            # Apply reliability factor
            score *= option.reliability_estimate
            
            scored_options.append((score, option))
        
        # Sort by score
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        # Populate scores dict
        decision.scores = {opt.id: score for score, opt in scored_options}
        
        # Set recommendation
        if scored_options:
            decision.recommended_option_id = scored_options[0][1].id
            top_option = scored_options[0][1]
            decision.decision_rationale = (
                f"'{top_option.name}' scored highest ({scored_options[0][0]:.2f}). "
                f"Best balance of criteria: {', '.join(weighting.keys())}"
            )
        
        decision.status = DecisionStatus.EVALUATED
        return decision

    async def analyze_tradeoffs(
        self,
        decision: EngineeringDecision
    ) -> EngineeringDecision:
        """Analyze trade-offs between options."""
        options = decision.options_evaluated
        
        for i in range(len(options)):
            for j in range(i + 1, len(options)):
                option_a = options[i]
                option_b = options[j]
                
                # Analyze specific trade-offs
                weight_diff = option_a.metrics.get("weight", 0) - option_b.metrics.get("weight", 0)
                cost_diff = option_a.metrics.get("cost", 0) - option_b.metrics.get("cost", 0)
                perf_diff = option_a.metrics.get("performance", 0) - option_b.metrics.get("performance", 0)
                
                tradeoff = TradeoffAnalysis(
                    option_a_id=option_a.id,
                    option_a_name=option_a.name,
                    option_b_id=option_b.id,
                    option_b_name=option_b.name,
                    weight_vs_cost=weight_diff / (cost_diff + 1),  # Avoid division by zero
                    performance_vs_reliability=perf_diff * (option_a.reliability_estimate - option_b.reliability_estimate),
                    advantages_a=option_a.pros,
                    advantages_b=option_b.pros
                )
                
                # Recommend based on tradeoff
                if weight_diff < 0 and cost_diff < 0:
                    tradeoff.recommended = "A"
                    tradeoff.rationale = f"'{option_a.name}' is lighter and cheaper than '{option_b.name}'"
                elif weight_diff > 0 and cost_diff > 0:
                    tradeoff.recommended = "B"
                    tradeoff.rationale = f"'{option_b.name}' is lighter and cheaper than '{option_a.name}'"
                else:
                    tradeoff.recommended = "Neither"
                    tradeoff.rationale = "Trade-off required: no option dominates in all dimensions"
                
                decision.tradeoff_analyses.append(tradeoff)
        
        decision.status = DecisionStatus.EVALUATED
        return decision

    async def generate_recommendations(self, decision: EngineeringDecision) -> Dict[str, Any]:
        """Generate comprehensive decision recommendations."""
        recommendation = {
            "decision_id": decision.decision_id,
            "title": decision.title,
            "type": decision.decision_type.value,
            "options_count": len(decision.options_evaluated),
            "recommended_option": None,
            "rationale": decision.decision_rationale,
            "tradeoffs": []
        }
        
        # Find recommended option
        for option in decision.options_evaluated:
            if option.id == decision.recommended_option_id:
                recommendation["recommended_option"] = {
                    "name": option.name,
                    "description": option.description,
                    "pros": option.pros,
                    "cons": option.cons,
                    "risks": option.risk_factors,
                    "reliability": option.reliability_estimate
                }
                break
        
        # Add tradeoff summaries
        recommendation["tradeoffs"] = [
            {
                "option_a": a.option_a_name,
                "option_b": a.option_b_name,
                "recommended": a.recommended,
                "rationale": a.rationale
            }
            for a in decision.tradeoff_analyses
        ]
        
        return recommendation

    async def document_decision(
        self,
        decision: EngineeringDecision,
        selected_option_id: Optional[str] = None,
        rationale: Optional[str] = None,
        risks: Optional[List[str]] = None
    ) -> EngineeringDecision:
        """Document a final decision."""
        if selected_option_id:
            decision.selected_option_id = selected_option_id
        elif decision.recommended_option_id:
            decision.selected_option_id = decision.recommended_option_id
            
        decision.decided_at = datetime.utcnow()
        
        if rationale:
            decision.decision_rationale = rationale
        
        if risks:
            decision.risks = risks
        
        decision.status = DecisionStatus.DOCUMENTED
        return decision

    async def implement_decision(
        self,
        decision: EngineeringDecision,
        selected_option_id: Optional[str] = None
    ) -> EngineeringDecision:
        """Mark decision as implemented."""
        if selected_option_id:
            decision.selected_option_id = selected_option_id
        decision.implemented_at = datetime.utcnow()
        decision.status = DecisionStatus.IMPLEMENTED
        return decision
