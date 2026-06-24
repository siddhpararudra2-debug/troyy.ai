"""
SQLAlchemy Models for Sprint 8 & Sprint 9 Engineering OS
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, DateTime, ForeignKey, Boolean
from app.core.database import Base


class AgentTask(Base):
    __tablename__ = "agent_tasks"
    id = Column(Text, primary_key=True)
    project_id = Column(Text)
    agent_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text)
    status = Column(Text, default="pending")  # pending/running/success/failed
    input_data_json = Column(Text, default="{}")
    output_data_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(Text, primary_key=True)
    project_id = Column(Text)
    mission_id = Column(Text)
    name = Column(Text, nullable=False)
    steps_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    id = Column(Text, primary_key=True)
    workflow_id = Column(Text, ForeignKey("workflows.id"))
    status = Column(Text, default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    results_json = Column(Text, default="{}")


class DesignCandidate(Base):
    __tablename__ = "design_candidates"
    id = Column(Text, primary_key=True)
    project_id = Column(Text)
    domain = Column(Text)
    parameters_json = Column(Text, default="{}")
    iteration = Column(Float)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    id = Column(Text, primary_key=True)
    node_type = Column(Text, nullable=False)
    data_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    id = Column(Text, primary_key=True)
    source_node_id = Column(Text, ForeignKey("knowledge_nodes.id"))
    target_node_id = Column(Text, ForeignKey("knowledge_nodes.id"))
    relationship_type = Column(Text, nullable=False)
    data_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class EngineeringLesson(Base):
    __tablename__ = "engineering_lessons"
    id = Column(Text, primary_key=True)
    project_id = Column(Text)
    title = Column(Text, nullable=False)
    content = Column(Text)
    tags_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Text, primary_key=True)
    project_id = Column(Text)
    name = Column(Text, nullable=False)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)


# === Sprint 9 Models ===


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Text, primary_key=True)
    tenant_id = Column(Text, ForeignKey("tenants.id"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    org_type = Column(Text, default="startup")  # startup/enterprise/aerospace
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Team(Base):
    __tablename__ = "teams"
    id = Column(Text, primary_key=True)
    organization_id = Column(Text, ForeignKey("organizations.id"), nullable=False)
    department_id = Column(Text, ForeignKey("departments.id"))
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Department(Base):
    __tablename__ = "departments"
    id = Column(Text, primary_key=True)
    organization_id = Column(Text, ForeignKey("organizations.id"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Role(Base):
    __tablename__ = "roles"
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    permissions_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Text, primary_key=True)
    event_type = Column(Text, nullable=False)
    user_id = Column(Text)
    resource_id = Column(Text)
    tenant_id = Column(Text)
    data_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Text, primary_key=True)
    resource_id = Column(Text, nullable=False)
    review_type = Column(Text, nullable=False)  # design/architecture/manufacturing
    title = Column(Text, nullable=False)
    created_by = Column(Text)
    status = Column(Text, default="in_progress")  # in_progress/approved/rejected
    reviewers_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class Approval(Base):
    __tablename__ = "approvals"
    id = Column(Text, primary_key=True)
    resource_id = Column(Text, nullable=False)
    requested_by = Column(Text)
    approver_ids_json = Column(Text, default="[]")
    status = Column(Text, default="pending")  # pending/approved/rejected
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Text, primary_key=True)
    resource_id = Column(Text, nullable=False)
    user_id = Column(Text)
    text = Column(Text, nullable=False)
    mentions_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"
    id = Column(Text, primary_key=True)
    tenant_id = Column(Text)
    title = Column(Text, nullable=False)
    content = Column(Text)
    tags_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class Program(Base):
    __tablename__ = "programs"
    id = Column(Text, primary_key=True)
    portfolio_id = Column(Text, ForeignKey("portfolios.id"), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text)
    project_ids_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(Text, primary_key=True)
    tenant_id = Column(Text)
    name = Column(Text, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"
    id = Column(Text, primary_key=True)
    resource_id = Column(Text, nullable=False)
    project_id = Column(Text)
    role = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    domain = Column(Text, nullable=False, unique=True)
    plan = Column(Text, default="basic")  # basic/enterprise
    status = Column(Text, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Text, primary_key=True)
    user_id = Column(Text, nullable=False)
    user_data_json = Column(Text, default="{}")
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"
    id = Column(Text, primary_key=True)
    tenant_id = Column(Text)
    compliance_type = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
