import pytest
from simulation_execution.services.simulation_orchestrator import SimulationOrchestrator
from simulation_execution.services.simulation_validator import SimulationValidator
from simulation_execution.schemas.simulation_models import (
    SimulationJob, SolverConfig, Material, BoundaryCondition
)
from simulation_execution.schemas.enums import SimulationDomain, SolverType

def test_solver_manager():
    from simulation_execution.services.solver_manager import SolverManager
    sm = SolverManager()
    solvers = sm.list_solvers()
    assert len(solvers) >= 3
    assert any(s["type"] == "CALCULIX" for s in solvers)

def test_validation():
    validator = SimulationValidator()
    job = SimulationJob(
        project_id="P1",
        domain=SimulationDomain.STRUCTURAL,
        solver_config=SolverConfig(solver_type=SolverType.CALCULIX),
        materials=[Material(name="Steel", density_kg_m3=7800, youngs_modulus_pa=200e9, 
                           poisson_ratio=0.3, yield_strength_pa=250e6)],
        boundary_conditions=[BoundaryCondition(name="fix1", bc_type="FIXED", region="node1")]
    )
    result = validator.validate(job)
    assert result["valid"]

def test_validation_failure():
    validator = SimulationValidator()
    job = SimulationJob(
        project_id="P1",
        domain=SimulationDomain.STRUCTURAL,
        solver_config=SolverConfig(solver_type=SolverType.CALCULIX, cores=0),  # Invalid
        materials=[]  # Missing material
    )
    result = validator.validate(job)
    assert not result["valid"]
    assert len(result["errors"]) > 0
