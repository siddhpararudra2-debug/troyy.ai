"""
Sprint 6 SQLAlchemy Models - Systems Engineering, MBSE, Mission Planning & Risk Management.
All models with UUID keys, revision history, traceability links, and version control.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Float, Integer,
    ForeignKey, JSON, Enum as SAEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database.models import Base, TimestampMixin


class Mission(Base, TimestampMixin):
    """Engineering mission definition."""
    __tablename__ = "sprint6_missions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    mission_type = Column(String(50), default="general")
    phase = Column(String(50), default="definition")
    objectives = Column(JSON, default=list)
    constraints = Column(JSON, default=list)
    performance_targets = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    version = Column(Integer, default=1)

    requirements = relationship("Requirement", back_populates="mission")
    __table_args__ = (Index("ix_sprint6_missions_type", "mission_type"),)


class Requirement(Base, TimestampMixin):
    """Engineering requirement with full traceability."""
    __tablename__ = "sprint6_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_missions.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    req_type = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="draft")
    source = Column(String(200), nullable=True)
    owner = Column(String(100), nullable=True)
    verification_method = Column(String(200), nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_requirements.id"), nullable=True)
    revision_history = Column(JSON, default=list)
    version = Column(Integer, default=1)
    risk_ids = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)

    mission = relationship("Mission", back_populates="requirements")
    children = relationship("Requirement", backref="parent",
                           remote_side=[id], foreign_keys=[parent_id])
    traceability_links = relationship("TraceLink", back_populates="source_requirement",
                                     foreign_keys="TraceLink.source_id")
    __table_args__ = (Index("ix_sprint6_req_type_status", "req_type", "status"),)


class RequirementLink(Base, TimestampMixin):
    """Traceability link between requirements."""
    __tablename__ = "sprint6_requirement_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_req_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_requirements.id"), nullable=False, index=True)
    target_req_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_requirements.id"), nullable=False, index=True)
    link_type = Column(String(50), default="traces")
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)


class SystemModel(Base, TimestampMixin):
    """System model with elements and relations."""
    __tablename__ = "sprint6_system_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1)
    metadata = Column(JSON, default=dict)


class Subsystem(Base, TimestampMixin):
    """Subsystem within the system model."""
    __tablename__ = "sprint6_subsystems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_system_models.id"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_subsystems.id"), nullable=True)
    name = Column(String(255), nullable=False)
    subsystem_type = Column(String(50))
    description = Column(Text, nullable=True)
    components = Column(JSON, default=list)
    parameters = Column(JSON, default=dict)


class Interface(Base, TimestampMixin):
    """Interface definition between system elements."""
    __tablename__ = "sprint6_interfaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    interface_type = Column(String(50))
    description = Column(Text, nullable=True)
    source_id = Column(String(100), nullable=False)
    target_id = Column(String(100), nullable=False)
    signals = Column(JSON, default=list)
    parameters = Column(JSON, default=dict)


class TradeStudy(Base, TimestampMixin):
    """Trade study and decision analysis record."""
    __tablename__ = "sprint6_trade_studies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    methodology = Column(String(50), default="weighted_sum")
    criteria = Column(JSON, default=list)
    alternatives = Column(JSON, default=list)
    results = Column(JSON, default=dict)
    recommendation = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)


class Risk(Base, TimestampMixin):
    """Risk item in the risk register."""
    __tablename__ = "sprint6_risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="technical")
    probability = Column(Float, default=0.5)
    impact = Column(Float, default=0.5)
    risk_score = Column(Float, default=0.25)
    risk_level = Column(String(20), default="medium")
    status = Column(String(20), default="identified")
    owner = Column(String(100), nullable=True)
    mitigations = Column(JSON, default=list)
    triggers = Column(JSON, default=list)


class Hazard(Base, TimestampMixin):
    """Hazard identified in the system."""
    __tablename__ = "sprint6_hazards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component = Column(String(255), nullable=False)
    failure_mode = Column(String(255), nullable=False)
    effects = Column(Text, nullable=True)
    cause = Column(Text, nullable=True)
    severity = Column(Integer, default=5)
    occurrence = Column(Integer, default=3)
    detection = Column(Integer, default=5)
    rpn = Column(Integer, default=75)
    metadata = Column(JSON, default=dict)


class Mitigation(Base, TimestampMixin):
    """Risk mitigation plan."""
    __tablename__ = "sprint6_mitigations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_risks.id"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    owner = Column(String(100), nullable=True)
    actions = Column(JSON, default=list)
    status = Column(String(20), default="planned")
    effectiveness = Column(Float, default=0.0)


class DesignReview(Base, TimestampMixin):
    """Design review record."""
    __tablename__ = "sprint6_design_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    review_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="planned")
    findings = Column(JSON, default=list)
    action_items = Column(JSON, default=list)
    reviewers = Column(JSON, default=list)
    materials = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)


class KnowledgeGraphNode(Base, TimestampMixin):
    """Node in the system knowledge graph."""
    __tablename__ = "sprint6_kg_nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    node_type = Column(String(50), nullable=False)
    domain = Column(String(50), default="general")
    description = Column(Text, nullable=True)
    properties = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)


class KnowledgeGraphEdge(Base, TimestampMixin):
    """Edge in the system knowledge graph."""
    __tablename__ = "sprint6_kg_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_kg_nodes.id"), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_kg_nodes.id"), nullable=False, index=True)
    relation = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)
    properties = Column(JSON, default=dict)


class WorkflowExecution(Base, TimestampMixin):
    """Workflow execution record."""
    __tablename__ = "sprint6_workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    tasks = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)


class TraceLink(Base, TimestampMixin):
    """Generic traceability link between any artifacts."""
    __tablename__ = "sprint6_trace_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sprint6_requirements.id"), nullable=False, index=True)
    target_id = Column(String(100), nullable=False)
    source_type = Column(String(50), default="requirement")
    target_type = Column(String(50), default="requirement")
    link_type = Column(String(50), default="traces")
    description = Column(Text, nullable=True)
    direction = Column(String(20), default="bidirectional")
    metadata = Column(JSON, default=dict)

    source_requirement = relationship("Requirement", back_populates="traceability_links",
                                     foreign_keys=[source_id])