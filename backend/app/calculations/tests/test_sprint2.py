"""
Sprint 2 - Engineering Intelligence Core Tests
Mathematics, Physics, Units, Validation, Calculations
"""
import sympy as sp
from app.math_engine.symbolic_solver import SymbolicSolver
from app.math_engine.numerical_solver import NumericalSolver
from app.math_engine.matrix_engine import MatrixEngine
from app.math_engine.calculus_engine import CalculusEngine
from app.physics_engine.mechanics import MechanicsEngine
from app.physics_engine.fluids import FluidEngine
from app.physics_engine.thermodynamics import ThermodynamicsEngine
from app.physics_engine.electromagnetics import ElectromagneticsEngine
from app.units.dimensional_checker import DimensionalChecker, check_force_mass_velocity, check_force_mass_acceleration
from app.units.uncertainty_engine import UncertaintyEngine, UncertainQuantity
from app.validation.services.formula_validator import FormulaValidator
from app.validation.services.engineering_review import EngineeringReview, DesignOption


def test_symbolic_solver():
    """Test symbolic solving, simplification, expansion, factorization"""
    solver = SymbolicSolver()
    x, y = sp.symbols('x y')

    # Test simplify
    expr = x**2 + 2*x + 1
    simplified = solver.simplify(expr)
    assert sp.simplify(expr) == sp.simplify(simplified["simplified"])

    # Test solve
    equation = sp.Eq(x**2 - 5*x + 6, 0)
    result = solver.solve_equation(equation, x)
    assert len(result["solutions"]) == 2


def test_numerical_solver():
    """Test numerical methods: bisection, newton-raphson, simpsons, ode solvers"""
    solver = NumericalSolver()

    # Define test functions
    f = lambda x: x**2 - 2
    df = lambda x: 2*x

    # Bisection method
    bisect_result = solver.bisection(f, 1, 2, tol=1e-4)
    assert bisect_result.converged
    assert abs(bisect_result.value - 1.4142) < 0.001

    # Newton-Raphson
    nr_result = solver.newton_raphson(f, df, 1.0, tol=1e-4)
    assert nr_result.converged
    assert abs(nr_result.value - 1.4142) < 0.001

    # ODE solvers
    ode = lambda t, y: y
    euler_result = solver.euler_method(ode, 1.0, 0.0, 1.0, 0.1)
    rk4_result = solver.rk4_method(ode, 1.0, 0.0, 1.0, 0.1)
    assert len(euler_result["y"]) == len(euler_result["t"])
    assert len(rk4_result["y"]) == len(rk4_result["t"])


def test_matrix_engine():
    """Test matrix operations"""
    engine = MatrixEngine()
    m1 = sp.Matrix([[1, 2], [3, 4]])

    # Determinant
    det_result = engine.determinant(m1)
    assert det_result["determinant"] == -2

    # Inverse
    inv_result = engine.inverse(m1)
    assert "inverse" in inv_result

    # Eigenvalues
    eig_result = engine.eigenvalues(m1)
    assert "eigenvalues" in eig_result


def test_calculus_engine():
    """Test differentiation, integration, limits, series"""
    engine = CalculusEngine()
    x = sp.symbols('x')

    # Derivative
    expr = x**2
    deriv = engine.derivative(expr, x)
    assert sp.simplify(deriv["derivative"] - 2*x) == 0

    # Integral
    integral = engine.integral(expr, x)
    assert sp.simplify(integral["antiderivative"] - x**3/3) == 0

    # Limit
    limit = engine.limit(sp.sin(x)/x, x, 0)
    assert limit["result"] == 1

    # Taylor
    series = engine.taylor_series(sp.exp(x), x, 0, 4)
    assert "series" in series


def test_mechanics_engine():
    """Test mechanical calculations: force, torque, bending stress, etc."""
    engine = MechanicsEngine()

    # Force
    force_result = engine.force(10, 9.81)
    assert force_result["force"] == 98.1

    # Torque
    torque_result = engine.torque(1.0, 10.0)
    assert torque_result["torque"] == 10.0

    # Bending stress
    bending = engine.bending_stress(100.0, 0.1, 0.001)
    assert "stress" in bending


def test_fluid_engine():
    """Test fluid dynamics: reynolds number, lift, drag, bernoulli, mach"""
    engine = FluidEngine()

    # Reynolds number
    re = engine.reynolds_number(1.2, 10, 0.1, 0.000018)
    assert re["reynolds"] > 0
    assert "flow_regime" in re

    # Lift
    lift = engine.lift_force(1.2, 100, 5.0, 0.5)
    assert "lift" in lift

    # Mach
    mach = engine.mach_number(343, 343)
    assert mach["mach"] == 1.0


def test_thermodynamics_engine():
    """Test thermo: ideal gas, conduction, etc."""
    engine = ThermodynamicsEngine()

    # Ideal gas law
    p, v, n, t = None, 1.0, 1.0, 273.15
    gas_result = engine.ideal_gas_law(p=p, v=v, n=n, t=t)
    assert "pressure" in gas_result
    assert gas_result["pressure"] > 0


def test_electromagnetics_engine():
    """Test electrical: Ohm's law, power, RC, LC"""
    engine = ElectromagneticsEngine()

    # Ohm's law
    ohm_result = engine.ohms_law(v=12.0, i=None, r=100)
    assert ohm_result["current"] == 0.12

    # Power
    power_result = engine.power(v=12.0, i=0.12)
    assert power_result["power"] == 1.44


def test_dimensional_checker():
    """Test dimensional consistency checks"""
    checker = DimensionalChecker()

    # Invalid check: Force = mass * velocity
    invalid_result = check_force_mass_velocity()
    assert invalid_result.valid is False

    # Valid check: Force = mass * acceleration
    valid_result = check_force_mass_acceleration()
    assert valid_result.valid is True


def test_uncertainty_engine():
    """Test uncertainty propagation"""
    engine = UncertaintyEngine()

    # Test add/subtract
    q1 = UncertainQuantity(5.0, 0.1)
    q2 = UncertainQuantity(3.0, 0.1)
    add_result = engine.add_subtract([q1, q2], "add")
    assert add_result.value == 8.0

    # Test multiply/divide
    mul_result = engine.multiply_divide([q1, q2], "multiply")
    assert mul_result.value == 15.0

    # Test power
    power_result = engine.power(q1, 2)
    assert power_result.value == 25.0


def test_formula_validator():
    """Test validation of formula inputs"""
    validator = FormulaValidator()

    # Valid parameters
    valid = validator.validate_calculation(
        "test",
        parameters={"mass": 10, "length": 5}
    )
    assert valid.valid is True

    # Invalid (negative mass)
    invalid = validator.validate_calculation(
        "test",
        parameters={"mass": -5, "length": 5}
    )
    assert invalid.valid is False


def test_engineering_review():
    """Test design option evaluation"""
    reviewer = EngineeringReview()

    options = [
        DesignOption(
            name="Option A",
            description="Low cost, low strength",
            metrics={"cost": 1.0, "weight": 0.9},
        ),
        DesignOption(
            name="Option B",
            description="High cost, high strength",
            metrics={"cost": 0.5, "weight": 0.8},
        ),
    ]

    criteria = {"cost": 0.6, "weight": 0.4}
    recommendation = reviewer.evaluate_options(options, criteria)
    assert len(recommendation.alternatives) == 1
    assert recommendation.recommended in options
