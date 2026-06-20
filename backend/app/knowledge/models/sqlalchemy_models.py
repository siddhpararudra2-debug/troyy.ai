"""
Engineering Knowledge Graph & Memory Platform SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, DateTime, ForeignKey
from app.core.database import Base


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    id = Column(Text, primary_key=True)
    node_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    project_id = Column(Text, nullable=True)
    properties_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeRelationship(Base):
    __tablename__ = "knowledge_relationships"
    id = Column(Text, primary_key=True)
    source_node_id = Column(Text, nullable=False)
    target_node_id = Column(Text, nullable=False)
    relationship_type = Column(Text, nullable=False)
    properties_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class EngineeringMemory(Base):
    __tablename__ = "engineering_memories"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=True)
    memory_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    tags_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComponentProfile(Base):
    __tablename__ = "component_profiles"
    id = Column(Text, primary_key=True)
    component_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    part_number = Column(Text, nullable=True)
    properties_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class MaterialProfile(Base):
    __tablename__ = "material_profiles"
    id = Column(Text, primary_key=True)
    material_type = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    properties_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)


class FailureRecord(Base):
    __tablename__ = "failure_records"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=True)
    failure_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    symptoms_json = Column(Text, nullable=False, default="[]")
    mitigations_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class LessonLearned(Base):
    __tablename__ = "lessons_learned"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    impact = Column(Text, nullable=False)
    tags_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class KnowledgeEmbedding(Base):
    __tablename__ = "knowledge_embeddings"
    id = Column(Text, primary_key=True)
    node_id = Column(Text, nullable=True)
    memory_id = Column(Text, nullable=True)
    embedding_vector_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class EngineeringInsight(Base):
    __tablename__ = "engineering_insights"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=True)
    insight_type = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    source_ids_json = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    recommendation_type = Column(Text, nullable=False)
    content_json = Column(Text, nullable=False, default="[]")
    outcome = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
