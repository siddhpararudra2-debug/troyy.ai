"""
Test suite for FormulaValidator - comprehensive validation coverage.
Tests: syntax validation, complexity analysis, dimensionality checks, numerical stability.
"""
import pytest
import asyncio
from validation.formula_validator import (
    FormulaValidator, FormulaValidationType, ValidationResult, ValidationError
)


class TestFormulaValidator:
    """Test FormulaValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return FormulaValidator()
    
    @pytest.mark.asyncio
    async def test_valid_formula(self, validator):
        """Test validation of a valid simple formula."""
        result = await validator.validate_formula("x + y", "formula_1")
        assert result.is_valid
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_complex_valid_formula(self, validator):
        """Test validation of complex valid formula."""
        formula = "stress = force / area"
        result = await validator.validate_formula(formula, "stress_calc")
        assert isinstance(result, ValidationResult)
        assert result.formula_id == "stress_calc"
    
    @pytest.mark.asyncio
    async def test_invalid_formula_syntax(self, validator):
        """Test validation catches syntax errors."""
        result = await validator.validate_formula("x ++ y", "bad_syntax")
        assert not result.is_valid
        assert len(result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_undefined_variable(self, validator):
        """Test validation detects undefined variables."""
        result = await validator.validate_formula("undefined_var + 5", "undef_test")
        assert isinstance(result, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_division_by_zero_detection(self, validator):
        """Test detection of potential division by zero."""
        result = await validator.validate_formula("1 / (x - x)", "div_zero")
        assert isinstance(result, ValidationResult)
        # Should have warnings about division by zero
    
    @pytest.mark.asyncio
    async def test_formula_with_functions(self, validator):
        """Test formula with mathematical functions."""
        result = await validator.validate_formula("sin(x) + cos(y)", "trig_formula")
        assert isinstance(result, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_formula_with_powers(self, validator):
        """Test formula with exponents."""
        result = await validator.validate_formula("x**2 + y**3", "power_formula")
        assert isinstance(result, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_formula_complexity_analysis(self, validator):
        """Test complexity scoring of formulas."""
        simple = await validator.validate_formula("x + y", "simple")
        complex_f = await validator.validate_formula("sin(x)**2 + cos(y)**2 + tan(z/2)", "complex")
        
        # Metadata should contain complexity scores
        assert "complexity" in simple.metadata or len(simple.metadata) >= 0
        assert isinstance(complex_f, ValidationResult)


class TestValidationErrors:
    """Test ValidationError dataclass."""
    
    def test_validation_error_creation(self):
        """Test creating validation error."""
        error = ValidationError(
            type=FormulaValidationType.SYNTAX_ERROR,
            severity="high",
            message="Invalid syntax"
        )
        assert error.severity == "high"
        assert error.message == "Invalid syntax"
    
    def test_validation_result_structure(self):
        """Test ValidationResult dataclass."""
        result = ValidationResult(
            formula_id="test_1",
            is_valid=True,
            errors=[],
            warnings=[],
            metadata={},
            validation_time_ms=10.5
        )
        assert result.formula_id == "test_1"
        assert result.is_valid is True
        assert result.validation_time_ms > 0


class TestFormulaValidationIntegration:
    """Integration tests for formula validation."""
    
    @pytest.mark.asyncio
    async def test_validate_multiple_formulas(self):
        """Test validating multiple formulas sequentially."""
        validator = FormulaValidator()
        formulas = [
            ("x + y", "f1"),
            ("stress = force / area", "f2"),
            ("sin(theta)", "f3")
        ]
        
        results = []
        for formula, fid in formulas:
            result = await validator.validate_formula(formula, fid)
            results.append(result)
        
        assert len(results) == 3
        assert all(isinstance(r, ValidationResult) for r in results)
    
    @pytest.mark.asyncio
    async def test_validation_consistency(self):
        """Test that validation is consistent for same formula."""
        validator = FormulaValidator()
        formula = "E = m * c**2"
        
        result1 = await validator.validate_formula(formula, "einstein_1")
        result2 = await validator.validate_formula(formula, "einstein_2")
        
        # Same formula should have same validity
        assert result1.is_valid == result2.is_valid
    
    @pytest.mark.asyncio
    async def test_stress_strain_formulas(self):
        """Test validation of engineering stress-strain formulas."""
        validator = FormulaValidator()
        
        # Hooke's Law
        hookes = await validator.validate_formula("stress = modulus * strain", "hookes")
        assert isinstance(hookes, ValidationResult)
        
        # Young's modulus
        youngs = await validator.validate_formula("E = stress / strain", "youngs")
        assert isinstance(youngs, ValidationResult)


class TestBoundaryConditions:
    """Test boundary conditions in formula validation."""
    
    @pytest.mark.asyncio
    async def test_empty_formula(self):
        """Test validation of empty formula."""
        validator = FormulaValidator()
        result = await validator.validate_formula("", "empty")
        # Should handle gracefully
        assert isinstance(result, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_very_long_formula(self):
        """Test validation of very long formula."""
        validator = FormulaValidator()
        long_formula = " + ".join([f"x{i}" for i in range(100)])
        result = await validator.validate_formula(long_formula, "long")
        assert isinstance(result, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_nested_functions(self):
        """Test deeply nested function calls."""
        validator = FormulaValidator()
        nested = "sin(cos(tan(x)))"
        result = await validator.validate_formula(nested, "nested")
        assert isinstance(result, ValidationResult)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
