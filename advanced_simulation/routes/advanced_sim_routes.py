from fastapi import APIRouter, HTTPException
import time
import asyncio
from advanced_simulation.schemas.requests import SPICERequest, BatteryRequest, MotorRequest, ConverterRequest, MissionRequest, MonteCarloRequest
from advanced_simulation.schemas.engineering_report import EngineeringReport
from advanced_simulation.services.spice_engine import SPICEEngine
from advanced_simulation.services.battery_simulation_service import BatterySimulationService
from advanced_simulation.services.motor_simulation_service import MotorSimulationService
from advanced_simulation.services.converter_simulation_service import ConverterSimulationService
from advanced_simulation.services.mission_simulation_service import MissionSimulationService
from advanced_simulation.services.digital_twin_service import DigitalTwinService
from advanced_simulation.services.monte_carlo_service import MonteCarloService
from advanced_simulation.services.sensitivity_service import SensitivityService
from advanced_simulation.services.scenario_comparison_service import ScenarioComparisonService
from advanced_simulation.services.reliability_prediction_service import ReliabilityPredictionService
from advanced_simulation.repositories.simulation_repository import SimulationRepository

router = APIRouter(prefix="/advanced-sim", tags=["Advanced Simulation & Digital Twin"])
repo = SimulationRepository()

spice = SPICEEngine()
batt = BatterySimulationService()
motor = MotorSimulationService()
conv = ConverterSimulationService()
mission = MissionSimulationService()
twin = DigitalTwinService()
mc = MonteCarloService()
sens = SensitivityService()
comp = ScenarioComparisonService()
rel = ReliabilityPredictionService()

def track_perf(func):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        ms = (time.perf_counter() - start) * 1000
        return res
    return wrapper

@router.post("/spice", response_model=EngineeringReport)
async def sim_spice(req: SPICERequest):
    return spice.simulate_transient(req)

@router.post("/battery", response_model=EngineeringReport)
async def sim_battery(req: BatteryRequest):
    return batt.simulate_discharge(req)

@router.post("/motor", response_model=EngineeringReport)
async def sim_motor(req: MotorRequest):
    return motor.simulate_performance(req)

@router.post("/converter", response_model=EngineeringReport)
async def sim_converter(req: ConverterRequest):
    return conv.simulate_buck(req)

@router.post("/mission", response_model=EngineeringReport)
async def sim_mission(req: MissionRequest):
    return mission.simulate_profile(req)

@router.post("/digital-twin", response_model=EngineeringReport)
async def update_twin(twin_id: str, state: dict):
    return twin.update_state(twin_id, state)

@router.post("/monte-carlo", response_model=EngineeringReport)
async def run_mc(req: MonteCarloRequest):
    return mc.run_analysis(req)

@router.post("/sensitivity", response_model=EngineeringReport)
async def run_sens(base_params: dict, func_name: str = "default"):
    return sens.analyze(base_params, func_name)

@router.post("/compare", response_model=EngineeringReport)
async def compare_scenarios(a: dict, b: dict):
    return comp.compare(a, b)

@router.post("/reliability", response_model=EngineeringReport)
async def predict_rel(stress_factor: float, temp_c: float):
    return rel.predict_life(stress_factor, temp_c)

@router.get("/{run_id}")
async def get_run(run_id: str):
    return repo.get_run(run_id)
