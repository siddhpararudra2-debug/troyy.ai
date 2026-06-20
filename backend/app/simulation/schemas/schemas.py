"""
Simulation Module Schemas
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# ------------------- Base Requests -------------------
class BaseSimulationRequest(BaseModel):
    project_id: str
    simulation_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


# ------------------- Circuit Simulation -------------------
class CircuitSimulationRequest(BaseSimulationRequest):
    circuit: Dict[str, Any] = Field(default_factory=dict)
    analysis_type: str = "dc"  # dc, ac, transient, frequency


class CircuitSimulationResponse(BaseModel):
    id: str
    project_id: str
    voltages: Dict[str, Any] = Field(default_factory=dict)
    currents: Dict[str, Any] = Field(default_factory=dict)
    power: Dict[str, Any] = Field(default_factory=dict)
    waveforms: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Analog Simulation -------------------
class AnalogSimulationRequest(BaseSimulationRequest):
    circuit_type: str = "amplifier"
    specs: Dict[str, Any] = Field(default_factory=dict)


class AnalogSimulationResponse(BaseModel):
    id: str
    project_id: str
    gain: Optional[float] = None
    bandwidth: Optional[float] = None
    noise: Optional[float] = None
    response_curves: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Digital Simulation -------------------
class DigitalSimulationRequest(BaseSimulationRequest):
    system: Dict[str, Any] = Field(default_factory=dict)


class DigitalSimulationResponse(BaseModel):
    id: str
    project_id: str
    logic_states: Dict[str, Any] = Field(default_factory=dict)
    timing_analysis: Dict[str, Any] = Field(default_factory=dict)
    bus_activity: List[Any] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Power Simulation -------------------
class PowerSimulationRequest(BaseSimulationRequest):
    system: Dict[str, Any] = Field(default_factory=dict)


class PowerSimulationResponse(BaseModel):
    id: str
    project_id: str
    efficiency: Optional[float] = None
    power_losses: Dict[str, float] = Field(default_factory=dict)
    current_flow: Dict[str, Any] = Field(default_factory=dict)
    thermal_loads: Dict[str, float] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Thermal Simulation -------------------
class ThermalSimulationRequest(BaseSimulationRequest):
    thermal_system: Dict[str, Any] = Field(default_factory=dict)


class ThermalSimulationResponse(BaseModel):
    id: str
    project_id: str
    temperature_rise: Dict[str, float] = Field(default_factory=dict)
    hotspots: List[Dict[str, Any]] = Field(default_factory=list)
    cooling_requirements: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Mechanical Simulation -------------------
class MechanicalSimulationRequest(BaseSimulationRequest):
    mechanical_system: Dict[str, Any] = Field(default_factory=dict)


class MechanicalSimulationResponse(BaseModel):
    id: str
    project_id: str
    loads: Dict[str, Any] = Field(default_factory=dict)
    forces: Dict[str, Any] = Field(default_factory=dict)
    deflections: Dict[str, Any] = Field(default_factory=dict)
    stress_estimates: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Robotics Simulation -------------------
class RoboticsSimulationRequest(BaseSimulationRequest):
    robotics_system: Dict[str, Any] = Field(default_factory=dict)


class RoboticsSimulationResponse(BaseModel):
    id: str
    project_id: str
    motion_results: Dict[str, Any] = Field(default_factory=dict)
    joint_stress: Dict[str, Any] = Field(default_factory=dict)
    actuator_utilization: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Aerospace Simulation -------------------
class AerospaceSimulationRequest(BaseSimulationRequest):
    aircraft_config: Dict[str, Any] = Field(default_factory=dict)


class AerospaceSimulationResponse(BaseModel):
    id: str
    project_id: str
    lift: Optional[float] = None
    drag: Optional[float] = None
    stability: Dict[str, Any] = Field(default_factory=dict)
    performance: Dict[str, Any] = Field(default_factory=dict)
    risk_factors: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Drone Simulation -------------------
class DroneSimulationRequest(BaseSimulationRequest):
    drone_config: Dict[str, Any] = Field(default_factory=dict)
    mission_profile: Dict[str, Any] = Field(default_factory=dict)


class DroneSimulationResponse(BaseModel):
    id: str
    project_id: str
    flight_time: Optional[float] = None
    power_usage: Dict[str, float] = Field(default_factory=dict)
    payload_impact: Dict[str, Any] = Field(default_factory=dict)
    motor_loading: Dict[str, float] = Field(default_factory=dict)
    mission_results: Dict[str, Any] = Field(default_factory=dict)
    performance_reports: List[Any] = Field(default_factory=list)
    risk_reports: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Optimization -------------------
class OptimizationRequest(BaseSimulationRequest):
    optimization_target: str
    domain: str = "electrical"  # electrical, mechanical, robotics, drone, aerospace


class OptimizationResponse(BaseModel):
    id: str
    project_id: str
    alternative_designs: List[Dict[str, Any]] = Field(default_factory=list)
    improved_parameters: Dict[str, Any] = Field(default_factory=dict)
    efficiency_improvements: Dict[str, float] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    created_at: datetime


# ------------------- Result Analysis -------------------
class ResultAnalysisResponse(BaseModel):
    id: str
    project_id: str
    pass_fail: bool = True
    warnings: List[str] = Field(default_factory=list)
    critical_findings: List[str] = Field(default_factory=list)
    engineering_commentary: str = ""
    execution_time_ms: Optional[float] = None
    created_at: datetime
