import pytest
from physics_engine.schemas.enums import PhysicsDomain, SolveStatus
from physics_engine.schemas.physics_models import (
    PhysicsProblem, PhysicalQuantity, PhysicsSolution
)
from physics_engine.services.units_engine import UnitsEngine
from physics_engine.services.dimensional_analysis_service import DimensionalAnalysisService
from physics_engine.services.symbolic_solver_service import SymbolicSolverService
from physics_engine.services.uncertainty_engine import UncertaintyEngine
from physics_engine.services.physics_validation_service import PhysicsValidationService

@pytest.fixture
def units_engine():
    return UnitsEngine()

@pytest.fixture
def dimensional_service(units_engine):
    return DimensionalAnalysisService(units_engine)

@pytest.fixture
def solver_service():
    return SymbolicSolverService()

@pytest.fixture
def uncertainty_engine():
    return UncertaintyEngine(n_monte_carlo=100, seed=42)

@pytest.fixture
def validation_service(units_engine):
    return PhysicsValidationService(units_engine)

# ── Units Engine Tests ────────────────────────────────────────────────────────
def test_units_engine_parsing_and_si(units_engine):
    q = units_engine.parse_quantity(10.0, "m/s")
    assert q.magnitude == 10.0
    assert str(q.units) == "m/s"
    
    q_si = units_engine.to_si(q)
    assert q_si.magnitude == 10.0
    
    # Test conversion
    pq = PhysicalQuantity(value=100.0, unit="cm")
    converted = units_engine.convert(pq, "m")
    assert converted.value == 1.0
    assert converted.unit == "meter"
    assert converted.si_value == 1.0

def test_units_engine_homogeneity(units_engine):
    t1 = units_engine.parse_quantity(1.0, "m")
    t2 = units_engine.parse_quantity(2.5, "m")
    t3 = units_engine.parse_quantity(5.0, "s")
    
    assert units_engine.check_dimensional_homogeneity([t1, t2]) is True
    assert units_engine.check_dimensional_homogeneity([t1, t3]) is False

def test_units_engine_get_dimension(units_engine):
    dim = units_engine.get_dimension("N")
    assert dim.get("length") == 1
    assert dim.get("mass") == 1
    assert dim.get("time") == -2

# ── Dimensional Analysis Tests ───────────────────────────────────────────────
def test_buckingham_pi_reynolds(dimensional_service):
    # Reynolds number variables: rho (density), v (velocity), L (length), mu (dynamic viscosity)
    variables = {
        "rho": "kg/m^3",
        "v": "m/s",
        "L": "m",
        "mu": "Pa*s"
    }
    result = dimensional_service.analyze(variables)
    assert len(result.pi_groups) == 1
    assert "Reynolds Number" in result.pi_groups[0].name

# ── Symbolic Solver Tests ────────────────────────────────────────────────────
def test_solver_mechanics_f_ma(solver_service):
    problem = PhysicsProblem(
        domain=PhysicsDomain.MECHANICS,
        problem_statement="Determine the acceleration of a block when a force is applied to a mass.",
        givens={
            "F": PhysicalQuantity(value=10.0, unit="N"),
            "m": PhysicalQuantity(value=2.0, unit="kg")
        },
        unknowns=["a"]
    )
    solution = solver_service.solve(problem)
    assert solution.status == SolveStatus.EXACT
    assert "a" in solution.numerical_result
    assert solution.numerical_result["a"].value == 5.0

def test_solver_mechanics_projectile(solver_service):
    problem = PhysicsProblem(
        domain=PhysicsDomain.MECHANICS,
        problem_statement="Calculate the projectile range with velocity v0 and gravity g at theta.",
        givens={
            "v0": PhysicalQuantity(value=10.0, unit="m/s"),
            "theta": PhysicalQuantity(value=0.785398, unit="rad"), # 45 degrees in rad
            "g": PhysicalQuantity(value=9.81, unit="m/s^2")
        },
        unknowns=["R"]
    )
    solution = solver_service.solve(problem)
    assert solution.status == SolveStatus.EXACT
    assert "R" in solution.numerical_result
    assert pytest.approx(solution.numerical_result["R"].value, 0.01) == 10.19

def test_solver_thermodynamics_gas_law(solver_service):
    problem = PhysicsProblem(
        domain=PhysicsDomain.THERMODYNAMICS,
        problem_statement="Find temperature using the ideal gas law.",
        givens={
            "P": PhysicalQuantity(value=101325.0, unit="Pa"),
            "V": PhysicalQuantity(value=0.0224, unit="m^3"),
            "n": PhysicalQuantity(value=1.0, unit="mol")
        },
        unknowns=["T"]
    )
    solution = solver_service.solve(problem)
    assert solution.status == SolveStatus.EXACT
    assert "T" in solution.numerical_result
    # T = PV / (nR) = 101325 * 0.0224 / (1 * 8.314) approx 273 K
    assert pytest.approx(solution.numerical_result["T"].value, 1.0) == 273.0

# ── Uncertainty Engine Tests ─────────────────────────────────────────────────
def test_uncertainty_propagation(uncertainty_engine):
    # y = f(x1, x2) = x1 * x2
    def area(length, width):
        return length * width
        
    inputs = {
        "length": PhysicalQuantity(value=10.0, unit="m", uncertainty=0.1),
        "width": PhysicalQuantity(value=5.0, unit="m", uncertainty=0.05)
    }
    
    # Analytical: dy = sqrt((width * u_length)^2 + (length * u_width)^2) = sqrt((5*0.1)^2 + (10*0.05)^2) = sqrt(0.25 + 0.25) = sqrt(0.5) approx 0.707
    val, unc = uncertainty_engine.analytical_propagation(area, inputs)
    assert val == 50.0
    assert pytest.approx(unc, 0.01) == 0.707

    # Monte Carlo
    mc = uncertainty_engine.monte_carlo_propagation(area, inputs)
    assert pytest.approx(mc["nominal"], 0.1) == 50.0
    assert pytest.approx(mc["std"], 0.1) == 0.707

# ── Physics Validation Tests ──────────────────────────────────────────────────
def test_validation_success(validation_service):
    problem = PhysicsProblem(
        domain=PhysicsDomain.MECHANICS,
        problem_statement="Test boundary conditions",
        constraints=["v < 100"],
        givens={}
    )
    solution = PhysicsSolution(
        problem_id=problem.id,
        status=SolveStatus.EXACT,
        final_equation="v = 50",
        numerical_result={
            "v": PhysicalQuantity(value=50.0, unit="m/s")
        }
    )
    res = validation_service.validate(problem, solution)
    assert res["valid"] is True

def test_validation_failure_speed_limit(validation_service):
    problem = PhysicsProblem(
        domain=PhysicsDomain.MECHANICS,
        problem_statement="Test speed limit",
        constraints=[],
        givens={}
    )
    solution = PhysicsSolution(
        problem_id=problem.id,
        status=SolveStatus.EXACT,
        final_equation="v = 4e8",
        numerical_result={
            "v": PhysicalQuantity(value=4.0e8, unit="m/s")
        }
    )
    res = validation_service.validate(problem, solution)
    assert res["valid"] is False
    assert any(i["check"] == "order_of_magnitude" for i in res["issues"])

def test_validation_failure_constraint_violated(validation_service):
    problem = PhysicsProblem(
        domain=PhysicsDomain.MECHANICS,
        problem_statement="Test constraint limit",
        constraints=["v < 40"],
        givens={}
    )
    solution = PhysicsSolution(
        problem_id=problem.id,
        status=SolveStatus.EXACT,
        final_equation="v = 50",
        numerical_result={
            "v": PhysicalQuantity(value=50.0, unit="m/s")
        }
    )
    res = validation_service.validate(problem, solution)
    assert res["valid"] is False
    assert any(i["check"] == "boundary_conditions" for i in res["issues"])
