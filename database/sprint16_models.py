"""Sprint 16 Database Models - Engineering Deep Research Platform."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class ResearchProject(Base):
    """Research Project Model."""
    __tablename__ = "sprint16_research_projects"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    domain = Column(String)
    status = Column(String, default="planning")
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_modified = Column(DateTime, default=datetime.utcnow)


class ResearchQuestion(Base):
    """Research Question Model."""
    __tablename__ = "sprint16_research_questions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("sprint16_research_projects.id"))
    question = Column(String, nullable=False)
    priority = Column(String, default="medium")
    status = Column(String, default="open")


class ResearchSource(Base):
    """Research Source Model."""
    __tablename__ = "sprint16_research_sources"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    source_type = Column(String)
    url = Column(String)
    access_date = Column(DateTime, default=datetime.utcnow)


class Paper(Base):
    """Academic Paper Model."""
    __tablename__ = "sprint16_papers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    authors = Column(JSON)
    abstract = Column(String)
    doi = Column(String, unique=True)
    publication_date = Column(DateTime)
    venue = Column(String)
    citations = Column(Integer, default=0)


class Patent(Base):
    """Patent Model."""
    __tablename__ = "sprint16_patents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    patent_number = Column(String, unique=True)
    inventors = Column(JSON)
    assignee = Column(String)
    filing_date = Column(DateTime)
    abstract = Column(String)
    status = Column(String)


class Standard(Base):
    """Standard Model."""
    __tablename__ = "sprint16_standards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    standard_number = Column(String, unique=True)
    issuing_body = Column(String)
    publication_date = Column(DateTime)
    description = Column(String)


class TradeStudy(Base):
    """Trade Study Model."""
    __tablename__ = "sprint16_trade_studies"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    alternatives = Column(JSON)
    criteria = Column(JSON)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class TechnologyTrend(Base):
    """Technology Trend Model."""
    __tablename__ = "sprint16_technology_trends"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    trend_score = Column(Float)
    growth_rate = Column(Float)
    forecast_years = Column(Integer)


class MaterialRecord(Base):
    """Material Record Model."""
    __tablename__ = "sprint16_material_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    material_type = Column(String)
    properties = Column(JSON)
    cost_per_unit = Column(Float)
    supplier = Column(String)


class ComponentRecord(Base):
    """Component Record Model."""
    __tablename__ = "sprint16_component_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    component_type = Column(String)
    manufacturer = Column(String)
    part_number = Column(String)
    specifications = Column(JSON)
    cost = Column(Float)


class ResearchFinding(Base):
    """Research Finding Model."""
    __tablename__ = "sprint16_research_findings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("sprint16_research_projects.id"))
    finding = Column(String, nullable=False)
    source_ids = Column(JSON)
    confidence = Column(Float, default=0.8)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    """Recommendation Model."""
    __tablename__ = "sprint16_recommendations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("sprint16_research_projects.id"))
    recommendation = Column(String, nullable=False)
    rationale = Column(String)
    priority = Column(String, default="medium")


class Evidence(Base):
    """Evidence Model."""
    __tablename__ = "sprint16_evidence"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    finding_id = Column(String, ForeignKey("sprint16_research_findings.id"))
    source_id = Column(String, ForeignKey("sprint16_research_sources.id"))
    content = Column(String)
    relevance_score = Column(Float, default=0.8)


class Citation(Base):
    """Citation Model."""
    __tablename__ = "sprint16_citations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    citing_id = Column(String)
    cited_id = Column(String)
    citation_type = Column(String)


class KnowledgeNode(Base):
    """Knowledge Node Model (for Engineering Knowledge Graph)."""
    __tablename__ = "sprint16_knowledge_nodes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(String, nullable=False)
    properties = Column(JSON)
    node_type = Column(String)


class KnowledgeEdge(Base):
    """Knowledge Edge Model (for Engineering Knowledge Graph)."""
    __tablename__ = "sprint16_knowledge_edges"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id = Column(String, ForeignKey("sprint16_knowledge_nodes.id"))
    target_node_id = Column(String, ForeignKey("sprint16_knowledge_nodes.id"))
    relationship_type = Column(String, nullable=False)
    properties = Column(JSON)
