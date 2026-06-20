from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class SPICERequest(BaseModel):
    nodes: int
    conductance_matrix: List[List[float]]
    capacitance_matrix: List[List[float]]
    current_sources: List[float]
    source_voltage: float = 5.0
    simulation_time_s: float = 0.01
    time_step_s: float = 1e-5

class BatteryRequest(BaseModel):
    chemistry: str = "LiPo"
    capacity_mah: float = 5000.0
    nominal_voltage_v: float = 11.1
    internal_resistance_ohm: float = 0.05
    initial_soc: float = 1.0
    load_current_a: float = 20.0
    ambient_temp_c: float = 25.0

class MotorRequest(BaseModel):
    type: str = "BLDC"
    voltage_v: float = 12.0
    kv_rpm_v: float = 900.0
    resistance_ohm: float = 0.1
    no_load_current_a: float = 0.5
    load_torque_nm: float = 0.5

class ConverterRequest(BaseModel):
    topology: str = "Buck"
    v_in: float = 12.0
    v_out: float = 5.0
    i_out: float = 3.0
    switching_freq_hz: float = 500000.0
    inductance_h: float = 10e-6
    capacitance_f: float = 22e-6

class MissionRequest(BaseModel):
    vehicle_mass_kg: float = 2.0
    battery_capacity_wh: float = 50.0
    cruise_power_w: float = 150.0
    hover_power_w: float = 250.0
    mission_profile: List[Dict[str, float]] # [{"phase": "hover", "duration_s": 60}, ...]

class MonteCarloRequest(BaseModel):
    base_params: Dict[str, float]
    tolerances: Dict[str, float] # e.g., {"resistance": 0.05} means 5%
    n_runs: int = 1000
