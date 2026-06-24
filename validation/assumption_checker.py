"""
Assumption Validation System for Engineering OS.
Validates design assumptions and their applicability.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


class AssumptionCategory(str, Enum):
    """Categories of engineering assumptions."""
    MATERIAL_PROPERTY = "material_property"
    ENVIRONMENTAL = "environmental"
    LOADING = "loading"
    GEOMETRY = "geometry"
    BOUNDARY_CONDITION = "boundary_condition"
    SIMPLIFICATION = "simplification"
    STANDARD = "standard"
    MANUFACTURER = "manufacturer"
    LIFE_CYCLE = "life_cycle"


class AssumptionValidity(str, Enum):
    """Validity status of assumptions."""
    VALID = "valid"
    QUESTIONABLE = "questionable"
    INVALID = "invalid"
    REQUIRES_VERIFICATION = "requires_verification"
    CONTEXT_DEPENDENT = "context_dependent"


class RiskLevel(str, Enum):
    """Risk levels for invalid assumptions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Assumption:
    """An engineering assumption."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: AssumptionCategory = AssumptionCategory.SIMPLIFICATION
    statement: str = ""
    description: str = ""
    justification: str = ""
    affected_parameters: List[str] = field(default_factory=list)
    impact_on_result: float = 0.5  # 0-1, impact magnitude
    validity: AssumptionValidity = AssumptionValidity.VALID
    risk_level: RiskLevel = RiskLevel.MEDIUM
    requirements: List[str] = field(default_factory=list)  # Conditions that make it valid
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AssumptionValidationResult:
    """Result of assumption validation."""
    assumption: Assumption
    is_applicable: bool
    confidence: float  # 0-1
    applicability_range: Dict[str, Any]  # e.g., {"temperature": [0, 100], "pressure": [1, 10]}
    violation_count: int = 0
    violations: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AssumptionSet:
    """A set of assumptions for a design."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    design_id: str = ""
    design_name: str = ""
    assumptions: List[Assumption] = field(default_factory=list)
    validations: List[AssumptionValidationResult] = field(default_factory=list)
    overall_risk: RiskLevel = RiskLevel.MEDIUM
    requires_validation: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AssumptionChecker:
    """Validates engineering assumptions."""

    def __init__(self):
        self.assumption_knowledge_base = self._initialize_kb()
        self.assumption_count = 0

    def _initialize_kb(self) -> Dict[AssumptionCategory, List[Dict]]:
        """Initialize knowledge base of common assumptions."""
        return {
            AssumptionCategory.MATERIAL_PROPERTY: [
                {
                    "name": "Isotropic Material",
                    "description": "Material properties are same in all directions",
                    "applicability": {"materials": ["mild_steel", "aluminum", "copper"]},
                    "inapplicable_for": ["composites", "wood", "laminated_materials"],
                    "range": None
                },
                {
                    "name": "Linear Elastic Behavior",
                    "description": "Stress-strain relationship is linear (Hooke's Law)",
                    "applicability": {"strain_range": [0, 0.001]},
                    "inapplicable_for": ["plastic_deformation", "large_strain"]
                },
                {
                    "name": "Room Temperature Properties",
                    "description": "Using material properties at 25°C",
                    "applicability": {"temperature": [15, 35]},
                    "inapplicable_for": ["cryogenic", "high_temperature", "thermal_cycling"]
                }
            ],
            AssumptionCategory.ENVIRONMENTAL: [
                {
                    "name": "Standard Gravity",
                    "description": "Using g = 9.81 m/s²",
                    "applicability": {"location": ["Earth_surface"]},
                    "inapplicable_for": ["space", "other_planets", "underwater"],
                    "value": 9.81
                },
                {
                    "name": "Standard Atmospheric Pressure",
                    "description": "Assuming 1 atm = 101325 Pa",
                    "applicability": {"altitude": [0, 1000]},
                    "inapplicable_for": ["high_altitude", "vacuum", "deep_sea"]
                },
                {
                    "name": "Dry Environment",
                    "description": "No moisture or corrosion effects",
                    "applicability": {"humidity": [0, 30], "environment": ["dry", "indoor"]},
                    "inapplicable_for": ["marine", "humid", "corrosive"]
                }
            ],
            AssumptionCategory.LOADING: [
                {
                    "name": "Static Loading",
                    "description": "Loads are applied slowly (quasi-static)",
                    "applicability": {"frequency": [0, 0.1]},
                    "inapplicable_for": ["dynamic", "impact", "vibration", "fatigue"]
                },
                {
                    "name": "Uniaxial Loading",
                    "description": "Single principal loading direction",
                    "applicability": None,
                    "inapplicable_for": ["multiaxial", "shear", "combined_loading"]
                },
                {
                    "name": "No Thermal Stresses",
                    "description": "Temperature is constant",
                    "applicability": {"temp_change": [0, 5]},
                    "inapplicable_for": ["thermal_cycling", "transient", "varying_temperature"]
                }
            ],
            AssumptionCategory.GEOMETRY: [
                {
                    "name": "Thin Wall Approximation",
                    "description": "Thickness << diameter",
                    "applicability": {"thickness_ratio": [0, 0.1]},
                    "inapplicable_for": ["thick_wall", "solid_sections"]
                },
                {
                    "name": "Small Deflection",
                    "description": "Deflections are small compared to dimensions",
                    "applicability": {"deflection_ratio": [0, 0.05]},
                    "inapplicable_for": ["large_displacement", "nonlinear_geometry"]
                }
            ],
            AssumptionCategory.SIMPLIFICATION: [
                {
                    "name": "Neglect Self-Weight",
                    "description": "Design loads >> self-weight",
                    "applicability": {"load_weight_ratio": [10, None]},
                    "inapplicable_for": ["tall_structures", "bridges", "ships"]
                },
                {
                    "name": "Rigid Supports",
                    "description": "Supports do not deflect",
                    "applicability": {"support_stiffness_ratio": [1e8, None]},
                    "inapplicable_for": ["soft_foundations", "flexible_supports"]
                }
            ]
        }

    async def create_assumption(
        self,
        category: AssumptionCategory,
        statement: str,
        description: str,
        justification: str,
        affected_parameters: List[str],
        impact: float = 0.5
    ) -> Assumption:
        """Create a new assumption."""
        self.assumption_count += 1
        
        assumption = Assumption(
            category=category,
            statement=statement,
            description=description,
            justification=justification,
            affected_parameters=affected_parameters,
            impact_on_result=impact
        )
        
        return assumption

    async def validate_assumption(
        self,
        assumption: Assumption,
        context: Dict[str, Any]
    ) -> AssumptionValidationResult:
        """Validate an assumption in the given context."""
        violations = []
        suggestions = []
        is_applicable = True
        confidence = 1.0
        applicability_range = {}

        # Check against knowledge base
        kb_entries = self.assumption_knowledge_base.get(assumption.category, [])
        
        for entry in kb_entries:
            if entry["name"].lower() in assumption.statement.lower():
                # Check applicability conditions
                applicability = entry.get("applicability", {})
                if applicability:
                    for param, allowed_range in applicability.items():
                        if param in context:
                            value = context[param]
                            if isinstance(allowed_range, (list, tuple)):
                                min_val, max_val = allowed_range[0], allowed_range[1] if len(allowed_range) > 1 else None
                                if value < min_val or (max_val and value > max_val):
                                    violations.append(
                                        f"Parameter '{param}' ({value}) outside applicability range {allowed_range}"
                                    )
                                    is_applicable = False
                                    confidence -= 0.2
                
                # Check inapplicable conditions
                inapplicable = entry.get("inapplicable_for", [])
                if inapplicable:
                    for forbidden_condition in inapplicable:
                        if forbidden_condition.lower() in str(context).lower():
                            violations.append(
                                f"Assumption invalid for: {forbidden_condition}"
                            )
                            is_applicable = False
                            confidence -= 0.3
                
                applicability_range = applicability or {}
        
        # Confidence cannot be negative
        confidence = max(0.0, min(1.0, confidence))

        result = AssumptionValidationResult(
            assumption=assumption,
            is_applicable=is_applicable,
            confidence=confidence,
            applicability_range=applicability_range,
            violation_count=len(violations),
            violations=violations,
            suggestions=suggestions
        )

        return result

    async def validate_assumption_set(
        self,
        assumptions: List[Assumption],
        design_id: str,
        design_name: str,
        context: Dict[str, Any]
    ) -> AssumptionSet:
        """Validate a complete set of assumptions."""
        assumption_set = AssumptionSet(
            design_id=design_id,
            design_name=design_name,
            assumptions=assumptions
        )

        for assumption in assumptions:
            result = await self.validate_assumption(assumption, context)
            assumption_set.validations.append(result)
            
            if not result.is_applicable:
                assumption_set.requires_validation.append(assumption.id)

        # Determine overall risk
        risks = [v.assumption.risk_level for v in assumption_set.validations if not v.is_applicable]
        if RiskLevel.CRITICAL in risks:
            assumption_set.overall_risk = RiskLevel.CRITICAL
        elif RiskLevel.HIGH in risks:
            assumption_set.overall_risk = RiskLevel.HIGH
        elif risks:
            assumption_set.overall_risk = RiskLevel.MEDIUM
        else:
            assumption_set.overall_risk = RiskLevel.LOW

        return assumption_set

    async def generate_assumption_report(self, assumption_set: AssumptionSet) -> Dict[str, Any]:
        """Generate a comprehensive assumption report."""
        valid_count = sum(1 for v in assumption_set.validations if v.is_applicable)
        invalid_count = len(assumption_set.validations) - valid_count
        avg_confidence = sum(v.confidence for v in assumption_set.validations) / len(assumption_set.validations) if assumption_set.validations else 0

        return {
            "design_name": assumption_set.design_name,
            "total_assumptions": len(assumption_set.assumptions),
            "valid_assumptions": valid_count,
            "invalid_assumptions": invalid_count,
            "requires_validation": len(assumption_set.requires_validation),
            "overall_risk": assumption_set.overall_risk.value,
            "average_confidence": avg_confidence,
            "assumptions": [
                {
                    "statement": a.statement,
                    "category": a.category.value,
                    "validity": a.validity.value,
                    "risk": a.risk_level.value,
                    "impact": a.impact_on_result,
                    "validation": {
                        "applicable": v.is_applicable,
                        "confidence": v.confidence,
                        "violations": v.violations
                    }
                }
                for a, v in zip(assumption_set.assumptions, assumption_set.validations)
            ],
            "recommendations": self._generate_recommendations(assumption_set)
        }

    def _generate_recommendations(self, assumption_set: AssumptionSet) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        invalid_high_impact = [
            v for v in assumption_set.validations 
            if not v.is_applicable and v.assumption.impact_on_result > 0.7
        ]
        
        if invalid_high_impact:
            recommendations.append(
                f"CRITICAL: {len(invalid_high_impact)} high-impact assumptions are questionable. "
                "Recommend redesign or validation testing."
            )
        
        requires_validation = [
            v for v in assumption_set.validations 
            if v.assumption.validity == AssumptionValidity.REQUIRES_VERIFICATION
        ]
        
        if requires_validation:
            recommendations.append(
                f"IMPORTANT: {len(requires_validation)} assumptions require verification. "
                "Plan validation tests or engineering analysis."
            )
        
        if assumption_set.overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append(
                "Design risk is elevated due to questionable assumptions. "
                "Consider design iterations or add safety margins."
            )
        
        return recommendations
