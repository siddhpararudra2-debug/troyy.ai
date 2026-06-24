from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import uuid
from datetime import datetime
from physics_engine.schemas.enums import PhysicsDomain, SolveStatus

class PhysicalQuantity(BaseModel):
    """A value with units, represented internally in SI base units."""
    value: float
    unit: str  # e.g., "m", "kg/s^2", "N"
    si_value: Optional[float] = None  # Converted to SI base
    symbol: Optional[str] = None  # Variable name, e.g., "v"
    uncertainty: Optional[float] = None  # Standard deviation

class DerivationStep(BaseModel):
    """A single step in a symbolic derivation."""
    step_number: int
    description: str
    equation_before: str
    equation_after: str
    operation: str  # "substitute", "differentiate", "integrate", "simplify", "solve"
    justification: str

class PhysicsProblem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: PhysicsDomain
    problem_statement: str
    givens: Dict[str, PhysicalQuantity] = Field(default_factory=dict)
    unknowns: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)

class PhysicsSolution(BaseModel):
    problem_id: str
    status: SolveStatus
    final_equation: str
    numerical_result: Optional[Dict[str, PhysicalQuantity]] = None
    derivation_steps: List[DerivationStep] = Field(default_factory=list)
    assumptions_used: List[str] = Field(default_factory=list)
    dimensional_check: bool = True
    uncertainty: Optional[Dict[str, float]] = None
    solve_time_ms: float = 0.0

class DimensionlessGroup(BaseModel):
    name: str
    symbol: str
    formula: str
    physical_meaning: str
    variables: Dict[str, str]  # variable -> dimension

class DimensionalAnalysisResult(BaseModel):
    problem_description: str
    variables: List[Dict[str, str]]
    fundamental_dimensions: List[str]
    pi_groups: List[DimensionlessGroup]
    functional_relationship: str
