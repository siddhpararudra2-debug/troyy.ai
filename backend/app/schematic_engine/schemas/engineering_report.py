from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class CalculationStep(BaseModel):
    description: str
    formula: Optional[str] = None
    values: Dict[str, Any] = Field(default_factory=dict)

class EngineeringReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requirements: List[str]
    assumptions: List[str]
    constraints: List[str]
    formula_selection: str
    formula_explanation: str
    matrix_operations: List[CalculationStep] = Field(default_factory=list)
    coordinate_transformations: List[CalculationStep] = Field(default_factory=list)
    unit_analysis: str
    intermediate_calculations: List[CalculationStep] = Field(default_factory=list)
    final_results: Optional[Dict[str, Any]] = None
    engineering_interpretation: Optional[str] = None
    validation_results: Dict[str, Any] = Field(default_factory=dict)
    documentation_ref: Optional[str] = None

class ReportContext:
    def __init__(self, **kwargs):
        self.report = EngineeringReport(**kwargs)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
        
    def add_matrix_op(self, desc: str, formula: str, values: dict):
        self.report.matrix_operations.append(CalculationStep(description=desc, formula=formula, values=values))
        
    def add_intermediate(self, desc: str, formula: str, values: dict):
        self.report.intermediate_calculations.append(CalculationStep(description=desc, formula=formula, values=values))
        
    def finalize(self, final_results: dict, interpretation: str):
        self.report.final_results = final_results
        self.report.engineering_interpretation = interpretation
        # Mock Day 7 & 8 integrations
        self.report.validation_results = {"status": "passed", "checks": ["electrical_rules_valid", "component_compatibility_ok"]}
        self.report.documentation_ref = f"DOC-{self.report.id}"
        return self.report
