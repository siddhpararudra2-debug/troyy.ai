"""
Tests for Physics Engine, Units, Validation, and Reports.
"""
import pytest
from physics.mechanics_engine import MechanicsEngine, Force, StressState
from physics.fluid_engine import FluidEngine
from physics.thermodynamics_engine import ThermodynamicsEngine
from physics.electromagnetics_engine import ElectromagneticsEngine
from units.unit_converter import UnitConverter
from units.dimensional_checker import DimensionalChecker
from units.uncertainty_engine import UncertaintyEngine, UncertainValue
from validation_engine.equation_validator import EquationValidator
from reports.report_generator import ReportGenerator


class TestMechanics:
    def test_sum_forces(self):
        mech = MechanicsEngine()
        forces = [Force(fx=10, fy=0), Force(fx=-5, fy=5)]
        result = mech.sum_forces(forces)
        assert result.result["fx"] == 5.0
        assert result.result["fy"] == 5.0

    def test_bending_stress(self):
        mech = MechanicsEngine()
        result = mech.beam_bending_stress(100, 0.05, 1e-6)
        assert result.result["bending_stress"] > 0

    def test_safety_factor(self):
        mech = MechanicsEngine()
        result = mech.safety_factor(250e6, 100e6)
        assert result.result["safety_factor"] == 2.5

    def test_column_buckling(self):
        mech = MechanicsEngine()
        result = mech.column_buckling(200e9, 1e-6, 2.0)
        assert result.result["critical_load"] > 0

    def test_von_mises(self):
        mech = MechanicsEngine()
        s = StressState(sigma_x=100e6, sigma_y=50e6)
        result = mech.von_mises_stress(s)
        assert result.result["von_mises_stress"] > 0


class TestFluid:
    def test_reynolds(self):
        fluid = FluidEngine()
        result = fluid.reynolds_number(1000, 1, 0.1, 0.001)
        assert result.result["reynolds_number"] == 100000.0

    def test_lift(self):
        fluid = FluidEngine()
        result = fluid.lift_force(1.0, 1.225, 10, 1)
        assert abs(result.result["lift"] - 61.25) < 1e-9

    def test_mach(self):
        fluid = FluidEngine()
        result = fluid.mach_number(340, 288)
        assert abs(result.result["mach"] - 1.0) < 0.1


class TestThermal:
    def test_ideal_gas(self):
        th = ThermodynamicsEngine()
        result = th.ideal_gas_law(101325, 0.0224, 1.0)
        assert result.result["temperature"] > 0


class TestElectromagnetics:
    def test_ohms_law(self):
        el = ElectromagneticsEngine()
        result = el.ohms_law(I=2, R=10)
        assert result.result["voltage"] == 20.0

    def test_rc_time(self):
        el = ElectromagneticsEngine()
        result = el.rc_time_constant(1000, 1e-6)
        assert result.result["time_constant"] == 0.001


class TestUnits:
    def test_length_conversion(self):
        result = UnitConverter.convert(1, "m", "ft")
        assert abs(result["converted_value"] - 3.28084) < 0.001

    def test_force_conversion(self):
        result = UnitConverter.convert(1, "N", "lbf")
        assert abs(result["converted_value"] - 0.224809) < 0.001

    def test_is_convertible(self):
        assert UnitConverter.is_convertible("m", "ft")
        assert not UnitConverter.is_convertible("m", "kg")

    def test_dimension_mismatch(self):
        with pytest.raises(ValueError):
            UnitConverter.convert(1, "m", "kg")


class TestDimensionalChecker:
    def test_consistent_equation(self):
        dc = DimensionalChecker()
        result = dc.check_equation(["m"], ["ft"])
        assert result["consistent"]

    def test_inconsistent_equation(self):
        dc = DimensionalChecker()
        result = dc.check_equation(["m"], ["kg"])
        assert not result["consistent"]


class TestUncertainty:
    def test_propagate_add(self):
        ue = UncertaintyEngine()
        a = UncertainValue(10, 0.1)
        b = UncertainValue(20, 0.2)
        result = ue.propagate_add(a, b)
        assert abs(result.value - 30) < 0.01
        assert abs(result.uncertainty - 0.2236) < 0.01

    def test_propagate_multiply(self):
        ue = UncertaintyEngine()
        a = UncertainValue(10, 0.5)
        b = UncertainValue(20, 1.0)
        result = ue.propagate_multiply(a, b)
        assert abs(result.value - 200) < 0.01


class TestValidator:
    def test_validate_calculation(self):
        val = EquationValidator()
        result = val.validate_calculation("stress_axial", {"F": 1000, "A": 0.01})
        assert result.valid

    def test_safety_review(self):
        val = EquationValidator()
        result = val.review_design_safety(2.0, "aerospace")
        assert result["adequate"]


class TestReportGenerator:
    @pytest.mark.asyncio
    async def test_generate_report(self):
        from calculations.calculation_engine import CalculationResult, CalculationStep
        from calculations.formula_library import get_formula
        gen = ReportGenerator()
        formula = get_formula("stress_axial")
        result = CalculationResult(
            id="test-1", formula_id="stress_axial", title="Test",
            formula=formula, steps=[
                CalculationStep(order=1, step_type="test", description="Step 1"),
            ],
            results={"σ": 100000.0}, results_formatted={"σ": "1.0000e+05 Pa"},
            latex_summary="", execution_time_ms=10.0, warnings=[], assumptions=[],
        )
        report = await gen.generate_calculation_report(result)
        assert "Engineering Calculation Report" in report
        assert "stress_axial" in report