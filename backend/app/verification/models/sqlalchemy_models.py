"""
Verification Platform SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, DateTime, Integer, ForeignKey
from app.core.database import Base


class VerificationPlan(Base):
    __tablename__ = "verification_plans"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    verification_type = Column(Text, nullable=False)
    activities_json = Column(Text, nullable=False, default="[]")
    schedule_json = Column(Text, nullable=False, default="{}")
    status = Column(Text, nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)


class ValidationPlan(Base):
    __tablename__ = "validation_plans"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    validation_type = Column(Text, nullable=False)
    scenarios_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    test_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    steps_json = Column(Text, nullable=False, default="[]")
    expected_results = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestExecution(Base):
    __tablename__ = "test_executions"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    test_case_ids_json = Column(Text, nullable=False, default="[]")
    results_json = Column(Text, nullable=False, default="[]")
    status = Column(Text, nullable=False, default="in_progress")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AcceptanceCriteria(Base):
    __tablename__ = "acceptance_criteria"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    system_type = Column(Text, nullable=False)
    criteria_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class HILSession(Base):
    __tablename__ = "hil_sessions"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    hardware_id = Column(Text, nullable=False)
    simulation_model_id = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pending")
    results_json = Column(Text, nullable=False, default="{}")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SILSession(Base):
    __tablename__ = "sil_sessions"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    firmware_id = Column(Text, nullable=False)
    simulation_model_id = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="pending")
    results_json = Column(Text, nullable=False, default="{}")
    coverage_json = Column(Text, nullable=False, default="{}")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CoverageMetric(Base):
    __tablename__ = "coverage_metrics"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    coverage_type = Column(Text, nullable=False)
    metrics_json = Column(Text, nullable=False, default="{}")
    gaps_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class VerificationMatrix(Base):
    __tablename__ = "verification_matrices"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    rows_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class VerificationReport(Base):
    __tablename__ = "verification_reports"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    report_type = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    sections_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
