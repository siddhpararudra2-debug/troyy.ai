"""
Tests for Engineering Mathematics Engine.
"""
import pytest
import numpy as np
from math_engine.symbolic_math import SymbolicMathEngine, DerivationResult
from math_engine.equation_solver import EquationSolver
from math_engine.matrix_engine import MatrixEngine
from math_engine.numerical_solver import NumericalSolver
from math_engine.optimization_math import OptimizationEngine


class TestSymbolicMath:
    def setup_method(self):
        self.engine = SymbolicMathEngine()

    def test_simplify(self):
        result = self.engine.simplify_expression("x + x + 2*x")
        assert "4*x" in result.result
        assert len(result.steps) >= 1

    def test_expand(self):
        result = self.engine.expand_expression("(x + 1)*(x + 2)")
        assert "x**2" in result.result
        assert len(result.steps) >= 1

    def test_differentiate(self):
        result = self.engine.differentiate("x**3", "x")
        assert "3*x**2" in result.result
        assert len(result.steps) >= 1

    def test_integrate(self):
        result = self.engine.integrate("x**2", "x")
        assert "x**3/3" in result.result

    def test_limit(self):
        result = self.engine.limit_calc("sin(x)/x", "x", "0")
        assert "1" in result.result

    def test_parse_equation(self):
        eq = SymbolicMathEngine.parse_equation("x + 1 = 2")
        assert eq.lhs - eq.rhs is not None


class TestEquationSolver:
    def setup_method(self):
        self.solver = EquationSolver()

    def test_solve_linear(self):
        result = self.solver.solve_linear("2*x + 3 = 7", "x")
        assert result.result is not None
        assert len(result.steps) >= 1

    def test_solve_quadratic(self):
        result = self.solver.solve_quadratic("x**2 - 5*x + 6 = 0", "x")
        assert len(result.steps) >= 2

    def test_solve_system(self):
        result = self.solver.solve_system(
            ["x + y = 3", "x - y = 1"], ["x", "y"]
        )
        assert result.result is not None


class TestMatrixEngine:
    def setup_method(self):
        self.engine = MatrixEngine()

    def test_determinant_2x2(self):
        result = self.engine.determinant([[1, 2], [3, 4]])
        assert result.result == "-2"

    def test_inverse(self):
        result = self.engine.inverse([[2, 0], [0, 2]])
        assert result.result is not None

    def test_matrix_multiply(self):
        result = self.engine.matrix_multiply([[1, 0], [0, 1]], [[1, 2], [3, 4]])
        assert result.result is not None


class TestNumericalSolver:
    def test_bisection(self):
        solver = NumericalSolver()
        result = solver.bisection(lambda x: x**2 - 4, 0, 3)
        assert abs(result.result - 2.0) < 0.001
        assert result.converged

    def test_newton(self):
        solver = NumericalSolver()
        result = solver.newton_raphson(lambda x: x**2 - 4, lambda x: 2*x, 3)
        assert abs(result.result - 2.0) < 0.001

    def test_simpson(self):
        solver = NumericalSolver()
        result = solver.simpson_integrate(lambda x: x**2, 0, 1, 100)
        assert abs(result.result - 1/3) < 0.001


class TestOptimization:
    def test_golden_section(self):
        opt = OptimizationEngine()
        result = opt.golden_section_search(lambda x: (x-2)**2, 0, 5)
        assert abs(result.optimal_point[0] - 2.0) < 0.1
        assert result.converged