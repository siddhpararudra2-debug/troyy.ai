from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class ReviewCategory(str, Enum):
    MECHANICAL = "MECHANICAL"
    STRUCTURAL = "STRUCTURAL"
    THERMAL = "THERMAL"
    ELECTRICAL = "ELECTRICAL"
    FIRMWARE = "FIRMWARE"
    MANUFACTURING = "MANUFACTURING"
    SAFETY = "SAFETY"
    CERTIFICATION = "CERTIFICATION"

class FindingSeverity(str, Enum):
    INFO = "INFO"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"
    SHOWSTOPPER = "SHOWSTOPPER"

class ApprovalDecision(str, Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONCERNS = "APPROVED_WITH_CONCERNS"
    REQUIRES_REVISION = "REQUIRES_REVISION"
    REJECTED = "REJECTED"

class ReviewFinding(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: ReviewCategory
    severity: FindingSeverity
    title: str
    description: str
    evidence: List[str] = Field(default_factory=list)
    recommendation: str
    raised_by: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ReviewReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    design_ref: str
    reviewer_role: str
    category: ReviewCategory
    findings: List[ReviewFinding] = Field(default_factory=list)
    decision: ApprovalDecision = ApprovalDecision.REQUIRES_REVISION
    justification: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CouncilDecision(BaseModel):
    project_id: str
    decision: ApprovalDecision
    summary: str
    findings_summary: Dict[str, int] = Field(default_factory=dict)
    required_actions: List[str] = Field(default_factory=list)
    approved_by: str = "Chief Engineer Agent"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
