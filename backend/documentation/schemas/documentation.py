from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from documentation.models.database import ReportType, KnowledgeCategory

class CalculationReportCreate(BaseModel):
    problem_statement: str
    requirements: str
    known_variables: Dict[str, Any]
    unknown_variables: Dict[str, Any]
    assumptions: str
    formula_selection: str
    formula_explanation: str
    unit_analysis: str
    substitution_steps: str
    intermediate_calculations: Dict[str, Any]
    final_results: Dict[str, Any]
    verification_results: str
    engineering_interpretation: str
    recommendations: str

class DecisionLogCreate(BaseModel):
    project_id: str
    decision_title: str
    decision_description: str
    reasoning: str
    benefits: str
    risks: str

class ProjectHistoryResponse(BaseModel):
    id: int
    project_id: str
    timestamp: datetime
    event_type: str
    details: Dict[str, Any]
    actor: str

class KnowledgeEntryResponse(BaseModel):
    id: int
    category: KnowledgeCategory
    title: str
    content: str
    tags: List[str]
    source_project_id: Optional[str]

class ExportRequest(BaseModel):
    report_id: int
    format: str = Field(..., description="MARKDOWN, HTML, JSON, PDF, DOCX")

class ExportResponse(BaseModel):
    report_id: int
    format: str
    content: str # Base64 encoded for binary formats, raw string for text
    generated_at: datetime
