"""
Compliance Platform SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, DateTime, Integer, ForeignKey
from app.core.database import Base


class Standard(Base):
    __tablename__ = "standards"
    id = Column(Text, primary_key=True)
    standard_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    code = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    requirements_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class Regulation(Base):
    __tablename__ = "regulations"
    id = Column(Text, primary_key=True)
    regulation_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    jurisdiction = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    requirements_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceRequirement(Base):
    __tablename__ = "compliance_requirements"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    requirement_id = Column(Text, nullable=False)
    standard_id = Column(Text, nullable=True)
    regulation_id = Column(Text, nullable=True)
    verification_method = Column(Text, nullable=True)
    evidence_id = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CertificationPlan(Base):
    __tablename__ = "certification_plans"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    certification_type = Column(Text, nullable=False)
    tasks_json = Column(Text, nullable=False, default="[]")
    timeline_json = Column(Text, nullable=False, default="{}")
    status = Column(Text, nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)


class SafetyAnalysis(Base):
    __tablename__ = "safety_analyses"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    analysis_type = Column(Text, nullable=False)
    hazards_json = Column(Text, nullable=False, default="[]")
    risk_register_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    risk_type = Column(Text, nullable=False)
    risks_json = Column(Text, nullable=False, default="[]")
    mitigations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditRecord(Base):
    __tablename__ = "audit_records"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    audit_type = Column(Text, nullable=False)
    auditor = Column(Text, nullable=True)
    findings_json = Column(Text, nullable=False, default="[]")
    overall_result = Column(Text, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    requirement_id = Column(Text, nullable=False)
    evidence_type = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceReport(Base):
    __tablename__ = "compliance_reports"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    report_type = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    sections_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class VerificationActivity(Base):
    __tablename__ = "verification_activities"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    requirement_id = Column(Text, nullable=False)
    activity_type = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
