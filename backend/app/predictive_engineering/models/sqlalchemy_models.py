"""
SQLAlchemy Models for Predictive Engineering
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class PredictiveAnalysis(Base):
    __tablename__ = "predictive_analyses"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    analysis_type = Column(String, nullable=False)
    results_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())


class AnomalyDetection(Base):
    __tablename__ = "anomaly_detections"

    id = Column(String, primary_key=True)
    predictive_analysis_id = Column(String, ForeignKey("predictive_analyses.id"), nullable=False)
    anomalies_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())


class DegradationModel(Base):
    __tablename__ = "degradation_models"

    id = Column(String, primary_key=True)
    predictive_analysis_id = Column(String, ForeignKey("predictive_analyses.id"), nullable=False)
    model_type = Column(String, nullable=False)
    model_params_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())


class ReliabilityForecast(Base):
    __tablename__ = "reliability_forecasts"

    id = Column(String, primary_key=True)
    predictive_analysis_id = Column(String, ForeignKey("predictive_analyses.id"), nullable=False)
    forecast_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())


class MaintenancePlan(Base):
    __tablename__ = "maintenance_plans"

    id = Column(String, primary_key=True)
    predictive_analysis_id = Column(String, ForeignKey("predictive_analyses.id"), nullable=False)
    tasks_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(String, primary_key=True)
    predictive_analysis_id = Column(String, ForeignKey("predictive_analyses.id"), nullable=False)
    risks_json = Column(Text, default="[]")
    mitigations_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())


class RootCauseAnalysis(Base):
    __tablename__ = "root_cause_analyses"

    id = Column(String, primary_key=True)
    predictive_analysis_id = Column(String, ForeignKey("predictive_analyses.id"), nullable=False)
    root_causes_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())
