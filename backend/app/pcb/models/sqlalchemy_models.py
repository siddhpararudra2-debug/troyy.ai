"""
PCB Intelligence Module SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class PCBProject(Base):
    __tablename__ = "pcb_projects"

    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    schematic_id = Column(Text)
    name = Column(Text, nullable=False)
    board_width_mm = Column(Float, default=100.0)
    board_height_mm = Column(Float, default=80.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PCBArchitecture(Base):
    __tablename__ = "pcb_architectures"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    subsystem_regions_json = Column(Text, nullable=False, default="[]")
    power_domains_json = Column(Text, nullable=False, default="[]")
    signal_domains_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class PCBStackup(Base):
    __tablename__ = "pcb_stackups"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    layer_count = Column(Integer, nullable=False)
    layers_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class PlacementPlan(Base):
    __tablename__ = "placement_plans"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    components_json = Column(Text, nullable=False, default="[]")
    placement_regions_json = Column(Text, nullable=False, default="[]")
    optimization_score = Column(Float)
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoutingPlan(Base):
    __tablename__ = "routing_plans"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    routing_rules_json = Column(Text, nullable=False, default="[]")
    routing_priorities_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class PowerDistribution(Base):
    __tablename__ = "power_distributions"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    power_domains_json = Column(Text, nullable=False, default="[]")
    power_planes_json = Column(Text, nullable=False, default="[]")
    regulator_placement_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class GroundStrategy(Base):
    __tablename__ = "ground_strategies"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    strategy_type = Column(Text, nullable=False)
    ground_strategy_json = Column(Text, nullable=False, default="{}")
    return_current_analysis_json = Column(Text, nullable=False, default="{}")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ThermalAnalysis(Base):
    __tablename__ = "thermal_analyses"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    power_dissipation_w = Column(Float)
    hot_spots_json = Column(Text, nullable=False, default="[]")
    thermal_density_map_json = Column(Text, nullable=False, default="{}")
    cooling_recommendations_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class EMIAnalysis(Base):
    __tablename__ = "emi_analyses"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    emi_risks_json = Column(Text, nullable=False, default="[]")
    emc_recommendations_json = Column(Text, nullable=False, default="[]")
    loop_area_analysis_json = Column(Text, nullable=False, default="{}")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class DRCResult(Base):
    __tablename__ = "drc_results"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    violations_json = Column(Text, nullable=False, default="[]")
    total_errors = Column(Integer, default=0)
    total_warnings = Column(Integer, default=0)
    is_drc_passed = Column(Integer, default=1)
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ManufacturingReview(Base):
    __tablename__ = "manufacturing_reviews"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    fabrication_constraints_json = Column(Text, nullable=False, default="[]")
    assembly_constraints_json = Column(Text, nullable=False, default="[]")
    dfm_review_json = Column(Text, nullable=False, default="[]")
    dfa_review_json = Column(Text, nullable=False, default="[]")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class PCBReviewResult(Base):
    __tablename__ = "pcb_review_results"

    id = Column(Text, primary_key=True)
    pcb_project_id = Column(Text, ForeignKey("pcb_projects.id"))
    placement_review_json = Column(Text, nullable=False, default="[]")
    routing_review_json = Column(Text, nullable=False, default="[]")
    power_review_json = Column(Text, nullable=False, default="[]")
    grounding_review_json = Column(Text, nullable=False, default="[]")
    thermal_review_json = Column(Text, nullable=False, default="[]")
    emi_review_json = Column(Text, nullable=False, default="[]")
    manufacturability_review_json = Column(Text, nullable=False, default="[]")
    approval_status = Column(Text, default="pending")
    overall_score = Column(Float)
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
