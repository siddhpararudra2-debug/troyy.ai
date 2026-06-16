from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ApprovalStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    APPROVED_WITH_CONCERNS = "APPROVED_WITH_CONCERNS"
    REQUIRES_REVISION = "REQUIRES_REVISION"
    REJECTED = "REJECTED"

class ValidationRun(Base):
    __tablename__ = "validation_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    solver_run_id: Mapped[str] = mapped_column(String, index=True)
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String, default="PENDING")
    
    issues: Mapped[List["ValidationIssue"]] = relationship(back_populates="run")
    review: Mapped[Optional["EngineeringReview"]] = relationship(back_populates="run")
    approval: Mapped[Optional["ApprovalDecision"]] = relationship(back_populates="run")

class ValidationIssue(Base):
    __tablename__ = "validation_issues"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("validation_runs.id"))
    module: Mapped[str] = mapped_column(String)
    severity: Mapped[Severity] = mapped_column(Enum(Severity))
    description: Mapped[str] = mapped_column(Text)
    engineering_reasoning: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    
    run: Mapped["ValidationRun"] = relationship(back_populates="issues")

class EngineeringReview(Base):
    __tablename__ = "engineering_reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("validation_runs.id"), unique=True)
    design_flaws: Mapped[List[str]] = mapped_column(JSON)
    component_concerns: Mapped[List[str]] = mapped_column(JSON)
    weight_budget_status: Mapped[str] = mapped_column(String)
    power_budget_status: Mapped[str] = mapped_column(String)
    thermal_assumptions_status: Mapped[str] = mapped_column(String)
    
    run: Mapped["ValidationRun"] = relationship(back_populates="review")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("validation_runs.id"), unique=True)
    overall_risk_level: Mapped[Severity] = mapped_column(Enum(Severity))
    risk_matrix: Mapped[List[dict]] = mapped_column(JSON)
    
    run: Mapped["ValidationRun"] = relationship()

class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(Integer, ForeignKey("validation_runs.id"), unique=True)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus))
    engineering_reasoning: Mapped[str] = mapped_column(Text)
    risk_summary: Mapped[str] = mapped_column(Text)
    validation_summary: Mapped[str] = mapped_column(Text)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    run: Mapped["ValidationRun"] = relationship(back_populates="approval")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    action: Mapped[str] = mapped_column(String)
    details: Mapped[dict] = mapped_column(JSON)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
