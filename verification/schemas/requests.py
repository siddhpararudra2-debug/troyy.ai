from pydantic import BaseModel
from typing import List, Dict

class VerificationPlanRequest(BaseModel):
    project_id: str
    requirements: List[Dict]
    target_dal: str = "D"
    environments: List[str] = ["SIL", "HIL"]

class TestGenerationRequest(BaseModel):
    requirements: List[Dict]
    coverage_target: str = "MCDC"
    test_types: List[str] = ["UNIT", "INTEGRATION", "SYSTEM"]

class HILExecutionRequest(BaseModel):
    configuration: Dict
    test_cases: List[str]
    seed: int = 42
