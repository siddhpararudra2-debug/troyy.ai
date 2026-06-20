"""
Simulation Module SQLAlchemy Models
"""
from datetime import datetime
from sqlalchemy import Column, Text, Float, DateTime, ForeignKey
from app.core.database import Base


class SimulationProject(Base):
    __tablename__ = "simulation_projects"
    id = Column(Text, primary_key=True)
    project_id = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Text, primary_key=True)
    simulation_project_id = Column(Text, ForeignKey("simulation_projects.id"))
    simulation_type = Column(Text, nullable=False)
    parameters_json = Column(Text, nullable=False, default='{}')
    status = Column(Text, default="pending")
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class CircuitSimulation(Base):
    __tablename__ = "circuit_simulations"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    voltages_json = Column(Text, nullable=False, default='{}')
    currents_json = Column(Text, nullable=False, default='{}')
    power_json = Column(Text, nullable=False, default='{}')
    waveforms_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class PowerSimulation(Base):
    __tablename__ = "power_simulations"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    efficiency = Column(Float)
    power_losses_json = Column(Text, nullable=False, default='{}')
    current_flow_json = Column(Text, nullable=False, default='{}')
    thermal_loads_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ThermalSimulation(Base):
    __tablename__ = "thermal_simulations"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    temperature_rise_json = Column(Text, nullable=False, default='{}')
    hotspots_json = Column(Text, nullable=False, default='[]')
    cooling_requirements_json = Column(Text, nullable=False, default='[]')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class MechanicalSimulation(Base):
    __tablename__ = "mechanical_simulations"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    loads_json = Column(Text, nullable=False, default='{}')
    forces_json = Column(Text, nullable=False, default='{}')
    deflections_json = Column(Text, nullable=False, default='{}')
    stress_estimates_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoboticsSimulation(Base):
    __tablename__ = "robotics_simulations"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    motion_results_json = Column(Text, nullable=False, default='{}')
    joint_stress_json = Column(Text, nullable=False, default='{}')
    actuator_utilization_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class AerospaceSimulation(Base):
    __tablename__ = "aerospace_simulations"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    lift = Column(Float)
    drag = Column(Float)
    stability_json = Column(Text, nullable=False, default='{}')
    performance_json = Column(Text, nullable=False, default='{}')
    risk_factors_json = Column(Text, nullable=False, default='[]')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class DroneSimulation(Base):
    __tablename__ = "drone_simulations"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    flight_time = Column(Float)
    power_usage_json = Column(Text, nullable=False, default='{}')
    payload_impact_json = Column(Text, nullable=False, default='{}')
    motor_loading_json = Column(Text, nullable=False, default='{}')
    mission_results_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class OptimizationResult(Base):
    __tablename__ = "optimization_results"
    id = Column(Text, primary_key=True)
    simulation_run_id = Column(Text, ForeignKey("simulation_runs.id"))
    alternative_designs_json = Column(Text, nullable=False, default='[]')
    improved_parameters_json = Column(Text, nullable=False, default='{}')
    efficiency_improvements_json = Column(Text, nullable=False, default='{}')
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
