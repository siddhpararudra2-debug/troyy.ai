"""
SQLAlchemy models for Engineering OS.
All entities with UUID keys, audit fields, soft deletes, and indexes.
"""
import uuid
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Float, Integer,
    ForeignKey, JSON, Enum as SAEnum, Index, UniqueConstraint,
    LargeBinary, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func


Base = declarative_base()


class MetadataDescriptor:
    def __get__(self, instance, owner):
        if instance is None:
            return Base.metadata
        return instance.metadata_

    def __set__(self, instance, value):
        instance.metadata_ = value



class TimestampMixin:
    """Mixin for timestamp and audit fields."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)


class User(Base, TimestampMixin):
    """User account."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(200), nullable=True)
    role = Column(String(50), default="engineer", nullable=False)
    preferences = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)
    
    projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    conversations = relationship("Conversation", back_populates="user")
    
    __table_args__ = (
        Index("ix_users_email_active", "email", "is_deleted"),
        Index("ix_users_username_active", "username", "is_deleted"),
    )


class Project(Base, TimestampMixin):
    """Engineering project."""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    metadata_ = Column("metadata", JSON, default=dict)
    tags = Column(JSON, default=list)
    metadata = MetadataDescriptor()

    
    owner = relationship("User", back_populates="projects", foreign_keys=[owner_id])
    conversations = relationship("Conversation", back_populates="project")
    memories = relationship("MemoryEntry", back_populates="project")
    decisions = relationship("EngineeringDecision", back_populates="project")
    calculations = relationship("Calculation", back_populates="project")
    documents = relationship("Document", back_populates="project")
    knowledge_assets = relationship("KnowledgeAsset", back_populates="project")
    agent_tasks = relationship("AgentTask", back_populates="project")
    
    __table_args__ = (
        Index("ix_projects_owner_status", "owner_id", "status"),
        Index("ix_projects_name_active", "name", "is_deleted"),
    )


class Conversation(Base, TimestampMixin):
    """Chat conversation."""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    model_used = Column(String(100), nullable=True)
    session_id = Column(String(100), nullable=True, index=True)
    metadata_ = Column("metadata", JSON, default=dict)
    metadata = MetadataDescriptor()
    
    user = relationship("User", back_populates="conversations")
    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")
    
    __table_args__ = (
        Index("ix_conversations_user_project", "user_id", "project_id"),
        Index("ix_conversations_session", "session_id"),
    )


class Message(Base, TimestampMixin):
    """Chat message within a conversation."""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=True)
    task_type = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    metadata = MetadataDescriptor()
    
    conversation = relationship("Conversation", back_populates="messages")
    
    __table_args__ = (
        Index("ix_messages_conversation_role", "conversation_id", "role"),
    )


class MemoryEntry(Base, TimestampMixin):
    """Long-term memory entry with semantic search capability."""
    __tablename__ = "memory_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    memory_type = Column(String(50), nullable=False, index=True)  # conversation, requirement, decision, calculation, report, document, context
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    embedding_id = Column(String(100), nullable=True, index=True)
    source = Column(String(100), nullable=True)
    importance = Column(Float, default=1.0, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    tags = Column(JSON, default=list)
    metadata = MetadataDescriptor()

    
    project = relationship("Project", back_populates="memories")
    
    __table_args__ = (
        Index("ix_memory_project_type", "project_id", "memory_type"),
        Index("ix_memory_type_importance", "memory_type", "importance"),
    )


class EngineeringDecision(Base, TimestampMixin):
    """Record of an engineering decision with rationale."""
    __tablename__ = "engineering_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    decision = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    alternatives = Column(JSON, default=list)
    criteria = Column(JSON, default=list)
    status = Column(String(50), default="proposed", nullable=False)  # proposed, approved, rejected, superseded
    decision_makers = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    
    project = relationship("Project", back_populates="decisions")
    
    __table_args__ = (
        Index("ix_decisions_project_status", "project_id", "status"),
    )


class Calculation(Base, TimestampMixin):
    """Engineering calculation record."""
    __tablename__ = "calculations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    calculation_type = Column(String(100), nullable=False, index=True)
    inputs = Column(JSON, nullable=False)
    outputs = Column(JSON, nullable=True)
    formula = Column(Text, nullable=True)
    result_summary = Column(Text, nullable=True)
    status = Column(String(50), default="pending", nullable=False)
    error_message = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    
    project = relationship("Project", back_populates="calculations")
    
    __table_args__ = (
        Index("ix_calculations_project_type", "project_id", "calculation_type"),
    )


class Document(Base, TimestampMixin):
    """Engineering document / knowledge source."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)
    file_size = Column(Integer, nullable=True)
    source = Column(String(200), nullable=True)
    status = Column(String(50), default="draft", nullable=False)
    tags = Column(JSON, default=list)
    metadata_ = Column("metadata", JSON, default=dict)
    metadata = MetadataDescriptor()
    
    project = relationship("Project", back_populates="documents")
    knowledge_assets = relationship("KnowledgeAsset", back_populates="document")
    
    __table_args__ = (
        Index("ix_documents_project_type", "project_id", "document_type"),
        Index("ix_documents_status", "status"),
    )


class KnowledgeAsset(Base, TimestampMixin):
    """Knowledge asset with vector embeddings for semantic search."""
    __tablename__ = "knowledge_assets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    asset_type = Column(String(100), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=True)
    embedding_id = Column(String(100), nullable=True, index=True)
    source = Column(String(200), nullable=True)
    citation = Column(Text, nullable=True)
    relevance_score = Column(Float, default=1.0)
    tags = Column(JSON, default=list)
    
    project = relationship("Project", back_populates="knowledge_assets")
    document = relationship("Document", back_populates="knowledge_assets")
    
    __table_args__ = (
        Index("ix_knowledge_project_type", "project_id", "asset_type"),
        Index("ix_knowledge_embedding", "embedding_id"),
    )


class AgentTask(Base, TimestampMixin):
    """Task assigned to an engineering agent."""
    __tablename__ = "agent_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("agent_tasks.id"), nullable=True)
    agent_type = Column(String(100), nullable=False, index=True)  # mechanical, electronics, pcb, firmware, simulation, documentation
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, nullable=True)
    status = Column(String(50), default="pending", nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False)
    dependencies = Column(JSON, default=list)
    assigned_to = Column(String(100), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    metadata = MetadataDescriptor()
    
    project = relationship("Project", back_populates="agent_tasks")
    executions = relationship("AgentExecution", back_populates="task")
    parent_task = relationship("AgentTask", remote_side=[id], backref="subtasks")
    
    __table_args__ = (
        Index("ix_agent_tasks_project_status", "project_id", "status"),
        Index("ix_agent_tasks_agent_status", "agent_type", "status"),
    )


class AgentExecution(Base, TimestampMixin):
    """Execution record for an agent task."""
    __tablename__ = "agent_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("agent_tasks.id"), nullable=False, index=True)
    execution_number = Column(Integer, nullable=False, default=1)
    status = Column(String(50), default="running", nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    model_used = Column(String(100), nullable=True)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    duration_ms = Column(Float, nullable=True)
    result_summary = Column(Text, nullable=True)
    logs = Column(JSON, default=list)
    error_message = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    metadata = MetadataDescriptor()
    
    task = relationship("AgentTask", back_populates="executions")
    
    __table_args__ = (
        Index("ix_agent_executions_task", "task_id"),
        Index("ix_agent_executions_status", "status"),
    )
