from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from verification.schemas.enums import TestType, ExecutionEnvironment, TestStatus, VerificationMethod

class Requirement(BaseModel):
    id: str
    text: str
    domain: str
    verification_method: VerificationMethod
    acceptance_criteria: List[str] = Field(default_factory=list)

class TestCase(BaseModel):
    __test__ = False
    id: str = Field(default_factory=lambda: f"TC-{uuid.uuid4().hex[:8].upper()}")
    requirement_id: str
    title: str
    test_type: TestType
    preconditions: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    expected_results: List[str] = Field(default_factory=list)
    environment: ExecutionEnvironment = ExecutionEnvironment.SIL
    priority: int = Field(ge=1, le=5, default=3)

class VerificationMatrixEntry(BaseModel):
    requirement_id: str
    test_ids: List[str] = Field(default_factory=list)
    analysis_refs: List[str] = Field(default_factory=list)
    inspection_refs: List[str] = Field(default_factory=list)
    coverage_status: str = "NOT_VERIFIED"

class CoverageMetrics(BaseModel):
    statement_pct: float = 0.0
    branch_pct: float = 0.0
    condition_pct: float = 0.0
    mcdc_pct: float = 0.0
    target_dal: str = "D"

class TestResult(BaseModel):
    test_id: str
    status: TestStatus
    execution_time_ms: float
    environment: ExecutionEnvironment
    evidence_refs: List[str] = Field(default_factory=list)
    failure_details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HILConfiguration(BaseModel):
    plant_model: str
    controller_model: str
    io_channels: Dict[str, str] = Field(default_factory=dict)
    step_size_s: float = 0.001
    duration_s: float = 10.0
    seed: int = 42
