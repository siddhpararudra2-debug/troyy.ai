"""Sprint 13 Database Models - SQLAlchemy models for Sprint 13."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Mission(Base):
    """Mission database model."""
    __tablename__ = "sprint13_missions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    mission_type = Column(String)
    status = Column(String, default="planning")
    priority = Column(String, default="medium")
    
    # Planning data
    objectives = Column(JSON)
    assigned_assets = Column(JSON)
    area_of_operations = Column(JSON)
    weather_requirements = Column(JSON)
    
    # Timeline
    planned_start = Column(DateTime)
    planned_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    last_modified = Column(DateTime, default=datetime.utcnow)
    modified_by = Column(String)
    version = Column(Integer, default=1)


class MissionPlan(Base):
    """Mission plan model."""
    __tablename__ = "sprint13_mission_plans"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey("sprint13_missions.id"))
    plan_name = Column(String)
    version = Column(Integer, default=1)
    
    # Waypoints and route
    waypoints = Column(JSON)
    route_distance = Column(Float)
    estimated_flight_time = Column(Float)
    
    # Optimization scores
    efficiency_score = Column(Float)
    risk_score = Column(Float)
    feasibility_score = Column(Float)
    
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)


class Swarm(Base):
    """Swarm model."""
    __tablename__ = "sprint13_swarms"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    swarm_type = Column(String)
    status = Column(String, default="idle")
    
    # Swarm composition
    agents = Column(JSON)
    leader_id = Column(String)
    
    # Formation
    formation_type = Column(String)
    formation_spacing = Column(Float)
    
    # Metrics
    cohesion = Column(Float)
    connectivity = Column(Float)
    efficiency = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_update = Column(DateTime, default=datetime.utcnow)


class Objective(Base):
    """Mission objective model."""
    __tablename__ = "sprint13_objectives"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey("sprint13_missions.id"))
    name = Column(String)
    description = Column(String)
    objective_type = Column(String)
    status = Column(String, default="pending")
    
    # Location and parameters
    target_location = Column(JSON)
    success_criteria = Column(JSON)
    constraints = Column(JSON)
    
    # Timing
    estimated_duration = Column(Float)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Scenario(Base):
    """Scenario model."""
    __tablename__ = "sprint13_scenarios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    scenario_type = Column(String)
    environment_id = Column(String)
    
    initial_conditions = Column(JSON)
    events = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class OperationalMap(Base):
    """Operational map model."""
    __tablename__ = "sprint13_operational_maps"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    center = Column(JSON)
    zoom = Column(Integer)
    map_type = Column(String)
    
    layers = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class MissionExecution(Base):
    """Mission execution record model."""
    __tablename__ = "sprint13_mission_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey("sprint13_missions.id"))
    plan_id = Column(String, ForeignKey("sprint13_mission_plans.id"))
    
    execution_status = Column(String)
    progress = Column(Float)
    
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    events = Column(JSON)
    metrics = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class MissionReplay(Base):
    """Mission replay record model."""
    __tablename__ = "sprint13_mission_replays"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    original_mission_id = Column(String, ForeignKey("sprint13_missions.id"))
    
    replay_status = Column(String)
    playback_speed = Column(Float)
    current_position = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SensorTrack(Base):
    """Sensor tracking model."""
    __tablename__ = "sprint13_sensor_tracks"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    mission_id = Column(String, ForeignKey("sprint13_missions.id"))
    
    track_id = Column(String)
    classification = Column(String)
    position = Column(JSON)
    confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class OperationalTwin(Base):
    """Operational twin model."""
    __tablename__ = "sprint13_operational_twins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String)
    asset_type = Column(String)
    
    current_state = Column(JSON)
    predictions = Column(JSON)
    anomalies = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ReadinessReport(Base):
    """Readiness report model."""
    __tablename__ = "sprint13_readiness_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    asset_id = Column(String)
    readiness_score = Column(Float)
    factors = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class LogisticsRecord(Base):
    """Logistics record model."""
    __tablename__ = "sprint13_logistics_records"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    record_type = Column(String)
    asset_id = Column(String)
    data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Campaign(Base):
    """Campaign model."""
    __tablename__ = "sprint13_campaigns"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    description = Column(String)
    status = Column(String, default="planning")
    
    missions = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
