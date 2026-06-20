from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class AircraftProject(Base):
    __tablename__ = "aircraft_projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    lift_analysis = relationship("LiftAnalysis", back_populates="project", uselist=False, cascade="all, delete-orphan")
    drag_analysis = relationship("DragAnalysis", back_populates="project", uselist=False, cascade="all, delete-orphan")
    wing_loading_analysis = relationship("WingLoadingAnalysis", back_populates="project", uselist=False, cascade="all, delete-orphan")
    stall_speed_analysis = relationship("StallSpeedAnalysis", back_populates="project", uselist=False, cascade="all, delete-orphan")
    aspect_ratio_analysis = relationship("AspectRatioAnalysis", back_populates="project", uselist=False, cascade="all, delete-orphan")
    performance_analysis = relationship("PerformanceAnalysis", back_populates="project", uselist=False, cascade="all, delete-orphan")

class LiftAnalysis(Base):
    __tablename__ = "lift_analyses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("aircraft_projects.id"))
    required_lift_n = Column(Float)
    generated_lift_n = Column(Float)
    lift_margin_percent = Column(Float)
    calculation_trace = Column(JSON)
    project = relationship("AircraftProject", back_populates="lift_analysis")

class DragAnalysis(Base):
    __tablename__ = "drag_analyses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("aircraft_projects.id"))
    parasite_drag_n = Column(Float)
    induced_drag_n = Column(Float)
    total_drag_n = Column(Float)
    calculation_trace = Column(JSON)
    project = relationship("AircraftProject", back_populates="drag_analysis")

class WingLoadingAnalysis(Base):
    __tablename__ = "wing_loading_analyses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("aircraft_projects.id"))
    wing_loading_n_m2 = Column(Float)
    classification = Column(String)
    calculation_trace = Column(JSON)
    project = relationship("AircraftProject", back_populates="wing_loading_analysis")

class StallSpeedAnalysis(Base):
    __tablename__ = "stall_speed_analyses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("aircraft_projects.id"))
    stall_speed_ms = Column(Float)
    safe_flight_speed_ms = Column(Float)
    recommended_cruise_ms = Column(Float)
    calculation_trace = Column(JSON)
    project = relationship("AircraftProject", back_populates="stall_speed_analysis")

class AspectRatioAnalysis(Base):
    __tablename__ = "aspect_ratio_analyses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("aircraft_projects.id"))
    aspect_ratio = Column(Float)
    induced_drag_factor = Column(Float)
    efficiency_impact = Column(String)
    calculation_trace = Column(JSON)
    project = relationship("AircraftProject", back_populates="aspect_ratio_analysis")

class PerformanceAnalysis(Base):
    __tablename__ = "performance_analyses"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("aircraft_projects.id"))
    cruise_speed_ms = Column(Float)
    power_required_w = Column(Float)
    mach_number = Column(Float)
    calculation_trace = Column(JSON)
    project = relationship("AircraftProject", back_populates="performance_analysis")
