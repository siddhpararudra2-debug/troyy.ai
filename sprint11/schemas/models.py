from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class Experiment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    name: str
    hypothesis_id: Optional[str] = None
    state: str = "CREATED"
    config: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, float] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResearchProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    domain: str
    objective: str
    status: str = "ACTIVE"
    experiment_ids: List[str] = Field(default_factory=list)
    hypothesis_ids: List[str] = Field(default_factory=list)
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Hypothesis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    statement: str
    rationale: str
    testable_predictions: List[str] = Field(default_factory=list)
    status: str = "PROPOSED"
    confidence: float = 0.5
    supporting_evidence: List[str] = Field(default_factory=list)
    contradicting_evidence: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Benchmark(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    domain: str
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    scoring_rubric: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BenchmarkResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    benchmark_id: str
    agent_id: str
    scores: Dict[str, float] = Field(default_factory=dict)
    overall_score: float = 0.0
    details: List[Dict[str, Any]] = Field(default_factory=list)
    executed_at: datetime = Field(default_factory=datetime.utcnow)

class AgentCapability(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    capability_name: str
    level: str = "NOVICE"
    score: float = 0.0
    embedding: List[float] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    last_evaluated: datetime = Field(default_factory=datetime.utcnow)

class ImprovementPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    target_capability: str
    current_score: float
    target_score: float
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "PLANNED"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GeneratedTool(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    code: str
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    validated: bool = False
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ResearchResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    experiment_id: Optional[str] = None
    result_type: str  # "INSIGHT", "FINDING", "RECOMMENDATION"
    content: str
    confidence: float = 0.5
    evidence: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EngineeringInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str
    pattern: str
    recommendation: str
    confidence: float = 0.5
    supporting_data: List[Dict[str, Any]] = Field(default_factory=list)
    source_events: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GovernanceReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str
    agent_id: str
    decision: str
    policies_evaluated: List[str] = Field(default_factory=list)
    safety_level: str = "LOW"
    justification: str
    blocked_reasons: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AuditEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    action: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    governance_decision: Optional[str] = None
    reasoning_trace: List[str] = Field(default_factory=list)
