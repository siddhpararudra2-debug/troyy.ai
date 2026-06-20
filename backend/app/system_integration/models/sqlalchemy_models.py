"""
System Integration & Hardware-Software Co-Design SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, Integer, DateTime, ForeignKey
from app.core.database import Base


class SystemProject(Base):
    __tablename__ = "system_projects"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Requirement(Base):
    __tablename__ = "requirements"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    description = Column(Text, nullable=False)
    status = Column(Text, default="draft")
    parent_id = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TraceabilityRecord(Base):
    __tablename__ = "traceability_records"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    requirement_id = Column(Text, nullable=False)
    target_type = Column(Text, nullable=False)
    target_id = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Subsystem(Base):
    __tablename__ = "subsystems"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    subcomponents_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class InterfaceDefinition(Base):
    __tablename__ = "interface_definitions"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    type = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    target = Column(Text, nullable=False)
    properties_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class Dependency(Base):
    __tablename__ = "dependencies"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    source = Column(Text, nullable=False)
    target = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ConfigurationBaseline(Base):
    __tablename__ = "configuration_baselines"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    name = Column(Text, nullable=False)
    version = Column(Text, nullable=False)
    artifacts_json = Column(Text, nullable=False, default="[]")
    approvals_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class ValidationResult(Base):
    __tablename__ = "system_validation_results"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    validation_results_json = Column(Text, nullable=False, default="[]")
    engineering_findings_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReviewBoardDecision(Base):
    __tablename__ = "review_board_decisions"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    critical_findings_json = Column(Text, nullable=False, default="[]")
    risks_json = Column(Text, nullable=False, default="[]")
    recommendations_json = Column(Text, nullable=False, default="[]")
    approval_status = Column(Text, default="pending")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class DigitalThreadRecord(Base):
    __tablename__ = "digital_thread_records"
    id = Column(Text, primary_key=True)
    system_project_id = Column(Text, ForeignKey("system_projects.id"))
    artifact_type = Column(Text, nullable=False)
    artifact_id = Column(Text, nullable=False)
    parent_ids_json = Column(Text, nullable=False, default="[]")
    timestamp = Column(DateTime, default=datetime.utcnow)
