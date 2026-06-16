"""
Troy — Validation SQLAlchemy ORM Models
ORM definitions for persisting validation history, design reviews, risk logs, and audit reports.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ValidationRunORM(Base):
    """Represents a single run of the validation suite."""

    __tablename__ = "validation_runs"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    solver_run_id = Column(String, ForeignKey("solver_runs.id", ondelete="SET NULL"), nullable=True)
    domain = Column(String, nullable=False)
    total_errors = Column(Integer, nullable=False, default=0)
    total_warnings = Column(Integer, nullable=False, default=0)
    is_approved = Column(Boolean, nullable=False, default=True)
    execution_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    issues = relationship(
        "ValidationIssueORM", back_populates="run", cascade="all, delete-orphan"
    )
    review = relationship(
        "EngineeringReviewORM", back_populates="run", uselist=False, cascade="all, delete-orphan"
    )
    risk_assessment = relationship(
        "RiskAssessmentORM", back_populates="run", uselist=False, cascade="all, delete-orphan"
    )
    approval_decision = relationship(
        "ApprovalDecisionORM", back_populates="run", uselist=False, cascade="all, delete-orphan"
    )
    audit_reports = relationship(
        "AuditReportORM", back_populates="run", cascade="all, delete-orphan"
    )


class ValidationIssueORM(Base):
    """Represents a specific issue flagged by a modular validator."""

    __tablename__ = "validation_issues"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False
    )
    severity = Column(String, nullable=False)  # "error", "warning", "info"
    category = Column(String, nullable=False)  # "Requirements", "Assumptions", "Formulas", etc.
    message = Column(String, nullable=False)
    validator_name = Column(String, nullable=False)
    engineering_reasoning = Column(String, nullable=True)
    recommendation = Column(String, nullable=True)

    run = relationship("ValidationRunORM", back_populates="issues")


class EngineeringReviewORM(Base):
    """Represents structural, thermal, electrical checks from the design review board."""

    __tablename__ = "engineering_reviews"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False
    )
    design_decisions_check = Column(String, nullable=False)
    component_choices_check = Column(String, nullable=False)
    structural_choices_check = Column(String, nullable=False)
    electrical_choices_check = Column(String, nullable=False)
    weight_budgets_check = Column(String, nullable=False)
    power_budgets_check = Column(String, nullable=False)
    thermal_assumptions_check = Column(String, nullable=False)
    overall_assessment = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("ValidationRunORM", back_populates="review")


class RiskAssessmentORM(Base):
    """Represents the compiled risk log and overall hazard scoring."""

    __tablename__ = "risk_assessments"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False
    )
    overall_risk_level = Column(String, nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    risks_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("ValidationRunORM", back_populates="risk_assessment")


class ApprovalDecisionORM(Base):
    """Final gateway approval or rejection decision."""

    __tablename__ = "approval_decisions"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False
    )
    status = Column(String, nullable=False)  # APPROVED, APPROVED WITH CONCERNS, REQUIRES REVISION, REJECTED
    engineering_reasoning = Column(String, nullable=False)
    risk_summary = Column(String, nullable=False)
    validation_summary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("ValidationRunORM", back_populates="approval_decision")


class AuditReportORM(Base):
    """Represents generated compliance audit reports in multiple formats."""

    __tablename__ = "audit_reports"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("validation_runs.id", ondelete="CASCADE"), nullable=False
    )
    report_type = Column(String, nullable=False)  # "validation", "review", "risk", "approval", "comprehensive"
    format = Column(String, nullable=False)  # "markdown", "html", "json", "pdf"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("ValidationRunORM", back_populates="audit_reports")


class AuditLogORM(Base):
    """Global audit log for verification gatekeeping actions."""

    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
