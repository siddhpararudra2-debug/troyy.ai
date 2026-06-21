"""
SQLAlchemy Models for PLM Platform
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class PLMProject(Base):
    __tablename__ = "plm_projects"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class ProjectRevision(Base):
    __tablename__ = "project_revisions"

    id = Column(String, primary_key=True)
    plm_project_id = Column(String, ForeignKey("plm_projects.id"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    description = Column(Text)
    artifacts_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())


class ConfigurationBaseline(Base):
    __tablename__ = "configuration_baselines"

    id = Column(String, primary_key=True)
    plm_project_id = Column(String, ForeignKey("plm_projects.id"), nullable=False)
    name = Column(String, nullable=False)
    artifacts_json = Column(Text, default="[]")
    approvals_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())


class ChangeRequest(Base):
    __tablename__ = "change_requests"

    id = Column(String, primary_key=True)
    plm_project_id = Column(String, ForeignKey("plm_projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False, default="submitted")
    created_at = Column(DateTime, default=func.now())


class ChangeOrder(Base):
    __tablename__ = "change_orders"

    id = Column(String, primary_key=True)
    change_request_id = Column(String, ForeignKey("change_requests.id"), nullable=False)
    actions_json = Column(Text, default="[]")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True)
    change_order_id = Column(String, ForeignKey("change_orders.id"), nullable=False)
    approver = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class ReleasePackage(Base):
    __tablename__ = "release_packages"

    id = Column(String, primary_key=True)
    plm_project_id = Column(String, ForeignKey("plm_projects.id"), nullable=False)
    version = Column(String, nullable=False)
    artifacts_json = Column(Text, default="[]")
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime, default=func.now())
