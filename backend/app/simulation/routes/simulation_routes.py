"""
Simulation Module Routes
"""
from fastapi import APIRouter
from app.simulation.schemas.schemas import (
    CircuitSimulationRequest, CircuitSimulationResponse,
    AnalogSimulationRequest, AnalogSimulationResponse,
    DigitalSimulationRequest, DigitalSimulationResponse,
    PowerSimulationRequest, PowerSimulationResponse,
    ThermalSimulationRequest, ThermalSimulationResponse,
    MechanicalSimulationRequest, MechanicalSimulationResponse,
    RoboticsSimulationRequest, RoboticsSimulationResponse,
    AerospaceSimulationRequest, AerospaceSimulationResponse,
    DroneSimulationRequest, DroneSimulationResponse,
    OptimizationRequest, OptimizationResponse
)
from app.simulation.services.circuit_simulation_service import CircuitSimulationService
from app.simulation.services.analog_simulation_service import AnalogSimulationService
from app.simulation.services.digital_simulation_service import DigitalSimulationService
from app.simulation.services.power_simulation_service import PowerSimulationService
from app.simulation.services.thermal_simulation_service import ThermalSimulationService
from app.simulation.services.mechanical_simulation_service import MechanicalSimulationService
from app.simulation.services.robotics_simulation_service import RoboticsSimulationService
from app.simulation.services.aerospace_simulation_service import AerospaceSimulationService
from app.simulation.services.drone_simulation_service import DroneSimulationService
from app.simulation.services.optimization_service import OptimizationService

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/circuit", response_model=CircuitSimulationResponse)
def run_circuit_simulation(request: CircuitSimulationRequest):
    return CircuitSimulationService.simulate(request)


@router.post("/analog", response_model=AnalogSimulationResponse)
def run_analog_simulation(request: AnalogSimulationRequest):
    return AnalogSimulationService.simulate(request)


@router.post("/digital", response_model=DigitalSimulationResponse)
def run_digital_simulation(request: DigitalSimulationRequest):
    return DigitalSimulationService.simulate(request)


@router.post("/power", response_model=PowerSimulationResponse)
def run_power_simulation(request: PowerSimulationRequest):
    return PowerSimulationService.simulate(request)


@router.post("/thermal", response_model=ThermalSimulationResponse)
def run_thermal_simulation(request: ThermalSimulationRequest):
    return ThermalSimulationService.simulate(request)


@router.post("/mechanical", response_model=MechanicalSimulationResponse)
def run_mechanical_simulation(request: MechanicalSimulationRequest):
    return MechanicalSimulationService.simulate(request)


@router.post("/robotics", response_model=RoboticsSimulationResponse)
def run_robotics_simulation(request: RoboticsSimulationRequest):
    return RoboticsSimulationService.simulate(request)


@router.post("/aerospace", response_model=AerospaceSimulationResponse)
def run_aerospace_simulation(request: AerospaceSimulationRequest):
    return AerospaceSimulationService.simulate(request)


@router.post("/drone", response_model=DroneSimulationResponse)
def run_drone_simulation(request: DroneSimulationRequest):
    return DroneSimulationService.simulate(request)


@router.post("/optimize", response_model=OptimizationResponse)
def run_optimization(request: OptimizationRequest):
    return OptimizationService.optimize(request)
