# pyrefly: ignore [missing-import]
import pytest
# pyrefly: ignore [missing-import]
import numpy as np
from advanced_simulation.services.battery_simulation_service import BatterySimulationService
from advanced_simulation.services.monte_carlo_service import MonteCarloService
from advanced_simulation.schemas.requests import BatteryRequest, MonteCarloRequest

def test_battery_sag():
    svc = BatterySimulationService()
    req = BatteryRequest(capacity_mah=5000, nominal_voltage_v=12.0, internal_resistance_ohm=0.1, load_current_a=10.0)
    rep = svc.simulate_discharge(req)
    # V_term = 12.0 - (10.0 * 0.1) = 11.0V
    assert rep.final_results['terminal_voltage_v'] == pytest.approx(11.0)

def test_monte_carlo_vectorized():
    svc = MonteCarloService()
    req = MonteCarloRequest(
        base_params={"voltage": 12.0, "resistance": 10.0},
        tolerances={"voltage": 0.05, "resistance": 0.05},
        n_runs=5000
    )
    rep = svc.run_analysis(req)
    assert rep.final_results['samples'] == 5000
    assert rep.final_results['mean'] > 0
