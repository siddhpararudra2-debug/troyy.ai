from sqlalchemy import Column, String, DateTime, JSON, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class DigitalTwin(Base):
    __tablename__ = "digital_twins"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String, nullable=False)
    state_data = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String, nullable=False)
    status = Column(String, nullable=False)
    execution_time_ms = Column(Float)
    results_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MonteCarloRun(Base):
    __tablename__ = "monte_carlo_runs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    n_runs = Column(Integer, nullable=False)
    yield_pct = Column(Float)
    results_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
