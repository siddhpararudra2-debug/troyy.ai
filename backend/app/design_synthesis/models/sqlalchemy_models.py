"""
SQLAlchemy Models for Design Synthesis
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class DesignSynthesisProject(Base):
    __tablename__ = "design_synthesis_projects"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    requirements_json = Column(Text, default="{}")
    status = Column(String, nullable=False, default="pending")
    current_iteration = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SynthesisIteration(Base):
    __tablename__ = "synthesis_iterations"

    id = Column(String, primary_key=True)
    design_synthesis_project_id = Column(String, ForeignKey("design_synthesis_projects.id"), nullable=False)
    iteration_number = Column(Integer, nullable=False)
    design_json = Column(Text, default="{}")
    performance_metrics_json = Column(Text, default="{}")
    issues_json = Column(Text, default="[]")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class OptimizationResult(Base):
    __tablename__ = "optimization_results"

    id = Column(String, primary_key=True)
    design_synthesis_project_id = Column(String, ForeignKey("design_synthesis_projects.id"), nullable=False)
    iteration_id = Column(String, ForeignKey("synthesis_iterations.id"), nullable=False)
    objectives_json = Column(Text, default="{}")
    constraints_json = Column(Text, default="{}")
    optimal_design_json = Column(Text, default="{}")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=func.now())
