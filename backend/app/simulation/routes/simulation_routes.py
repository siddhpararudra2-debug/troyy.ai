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
    OptimizationRequest, OptimizationResponse,
    FEASimulationRequest, FEASimulationResponse,
    CFDSimulationRequest, CFDSimulationResponse,
    VerificationRequest, VerificationResponse
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
from app.simulation.services.fea_engine import FEAEngine
from app.simulation.services.cfd_engine import CFDEngine
from app.simulation.services.verification.requirement_validator import RequirementValidator

router = APIRouter(prefix="/simulation", tags=["Simulation"])

# Initialize new services
fea_engine = FEAEngine()
cfd_engine = CFDEngine()
requirement_validator = RequirementValidator()


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


@router.post("/fea/run", response_model=FEASimulationResponse)
def run_fea(request: FEASimulationRequest):
    if request.analysis_type == "static":
        result = fea_engine.run_static_analysis(
            request.material_properties,
            request.loads,
            request.constraints,
            request.mesh_id
        )
    elif request.analysis_type == "modal":
        result = fea_engine.run_modal_analysis(
            request.material_properties,
            request.mesh_id
        )
    elif request.analysis_type == "thermal":
        result = fea_engine.run_thermal_stress_analysis(
            request.loads,
            request.material_properties
        )
    else:
        result = fea_engine.run_static_analysis(
            request.material_properties,
            request.loads,
            request.constraints,
            request.mesh_id
        )
    return {
        **result,
        "project_id": request.project_id
    }


@router.post("/cfd/run", response_model=CFDSimulationResponse)
def run_cfd(request: CFDSimulationRequest):
    if request.analysis_type == "external":
        result = cfd_engine.run_external_aerodynamics(
            {},
            request.fluid_properties,
            request.boundary_conditions,
            request.mesh_id
        )
    elif request.analysis_type == "internal":
        result = cfd_engine.run_internal_flow(
            {},
            request.fluid_properties,
            request.boundary_conditions,
            request.mesh_id
        )
    elif request.analysis_type == "thermal":
        result = cfd_engine.run_thermal_flow_analysis(
            {},
            request.fluid_properties,
            request.boundary_conditions,
            request.mesh_id
        )
    else:
        result = cfd_engine.run_external_aerodynamics(
            {},
            request.fluid_properties,
            request.boundary_conditions,
            request.mesh_id
        )
    return {
        **result,
        "project_id": request.project_id
    }


@router.post("/verification/run", response_model=VerificationResponse)
def run_verification(request: VerificationRequest):
    return requirement_validator.verify_requirements(
        request.requirements,
        request.project_id
    )


@router.get("/{simulation_id}")
def get_simulation(simulation_id: str):
    return {"id": simulation_id, "status": "retrieved"}


@router.get("/optimization/{optimization_id}")
def get_optimization(optimization_id: str):
    return {"id": optimization_id, "status": "retrieved"}


@router.get("/verification/{verification_id}")
def get_verification(verification_id: str):
    return {"id": verification_id, "status": "retrieved"}
