"""
SQLAlchemy Models for Digital Twin Ecosystem
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class DigitalTwin(Base):
    __tablename__ = "digital_twins"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    twin_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="idle")
    config_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TwinSyncRecord(Base):
    __tablename__ = "twin_sync_records"

    id = Column(String, primary_key=True)
    digital_twin_id = Column(String, ForeignKey("digital_twins.id"), nullable=False)
    sensor_data_json = Column(Text, default="{}")
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=func.now())


class TwinPrediction(Base):
    __tablename__ = "twin_predictions"

    id = Column(String, primary_key=True)
    digital_twin_id = Column(String, ForeignKey("digital_twins.id"), nullable=False)
    prediction_type = Column(String, nullable=False)
    results_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=func.now())


class TwinFailurePrediction(Base):
    __tablename__ = "twin_failure_predictions"

    id = Column(String, primary_key=True)
    digital_twin_id = Column(String, ForeignKey("digital_twins.id"), nullable=False)
    failure_type = Column(String, nullable=False)
    probability = Column(Float, default=0.0)
    time_to_failure = Column(Float)
    created_at = Column(DateTime, default=func.now())


class TwinHealthReport(Base):
    __tablename__ = "twin_health_reports"

    id = Column(String, primary_key=True)
    digital_twin_id = Column(String, ForeignKey("digital_twins.id"), nullable=False)
    health_score = Column(Float, default=0.0)
    remaining_useful_life = Column(Float)
    recommendations_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=func.now())
