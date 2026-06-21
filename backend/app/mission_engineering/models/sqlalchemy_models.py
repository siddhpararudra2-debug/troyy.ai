"""
SQLAlchemy Models for Mission Engineering
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class MissionProject(Base):
    __tablename__ = "mission_projects"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    mission_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    requirements_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MissionPlan(Base):
    __tablename__ = "mission_plans"

    id = Column(String, primary_key=True)
    mission_project_id = Column(String, ForeignKey("mission_projects.id"), nullable=False)
    airframe = Column(Text)
    propulsion = Column(Text)
    battery = Column(Text)
    payload = Column(Text)
    navigation = Column(Text)
    communications = Column(Text)
    control_systems = Column(Text)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class MissionSimulationResult(Base):
    __tablename__ = "mission_simulation_results"

    id = Column(String, primary_key=True)
    mission_project_id = Column(String, ForeignKey("mission_projects.id"), nullable=False)
    results_json = Column(Text, default="{}")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class MissionOptimizationResult(Base):
    __tablename__ = "mission_optimization_results"

    id = Column(String, primary_key=True)
    mission_project_id = Column(String, ForeignKey("mission_projects.id"), nullable=False)
    objectives_json = Column(Text, default="{}")
    constraints_json = Column(Text, default="{}")
    optimal_solution_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())


class MissionValidationReport(Base):
    __tablename__ = "mission_validation_reports"

    id = Column(String, primary_key=True)
    mission_project_id = Column(String, ForeignKey("mission_projects.id"), nullable=False)
    readiness_score = Column(Float, default=0.0)
    issues_json = Column(Text, default="[]")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class MissionRiskReport(Base):
    __tablename__ = "mission_risk_reports"

    id = Column(String, primary_key=True)
    mission_project_id = Column(String, ForeignKey("mission_projects.id"), nullable=False)
    risk_level = Column(String, nullable=False, default="LOW")
    risks_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())


class MissionTradeStudy(Base):
    __tablename__ = "mission_trade_studies"

    id = Column(String, primary_key=True)
    mission_project_id = Column(String, ForeignKey("mission_projects.id"), nullable=False)
    alternatives_json = Column(Text, default="[]")
    decision_matrix_json = Column(Text, default="{}")
    winner = Column(String)
    created_at = Column(DateTime, default=func.now())
