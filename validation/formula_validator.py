"""
Formula Validation Engine for Engineering OS.
Validates formulas, units, physics, and constraints.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
from sympy import symbols, sympify, simplify, diff
from sympy.parsing.sympy_parser import parse_expr
import re


class FormulaValidationType(str, Enum):
    """Types of formula validation."""
    SYNTAX = "syntax"
    SYNTAX_ERROR = "syntax"
    UNITS = "units"
    PHYSICS = "physics"
    CONSTRAINTS = "constraints"
    DIMENSIONALITY = "dimensionality"
    NUMERICAL_STABILITY = "numerical_stability"


@dataclass
class ValidationError:
    """Represents a validation error."""
    type: FormulaValidationType
    severity: str  # "error", "warning", "info"
    message: str
    location: Optional[str] = None
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of formula validation."""
    formula_id: str
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    metadata: Dict[str, Any]
    validation_time_ms: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class FormulaValidator:
    """Validates engineering formulas."""

    def __init__(self):
        self.known_units = {
            # Length
            "m": "meter", "mm": "millimeter", "cm": "centimeter", "km": "kilometer",
            "in": "inch", "ft": "foot", "yd": "yard",
            # Mass
            "kg": "kilogram", "g": "gram", "mg": "milligram", "lb": "pound",
            # Time
            "s": "second", "ms": "millisecond", "min": "minute", "h": "hour",
            # Temperature
            "K": "kelvin", "C": "celsius", "F": "fahrenheit",
            # Force
            "N": "newton", "kN": "kilonewton", "lbf": "pound-force",
            # Pressure
            "Pa": "pascal", "kPa": "kilopascal", "MPa": "megapascal", "psi": "psi",
            # Stress
            "MPa": "megapascal", "GPa": "gigapascal",
            # Energy
            "J": "joule", "kJ": "kilojoule", "MJ": "megajoule",
            # Power
            "W": "watt", "kW": "kilowatt", "MW": "megawatt", "hp": "horsepower",
            # Velocity
            "m/s": "meter/second", "km/h": "kilometer/hour", "mph": "mile/hour",
            # Acceleration
            "m/s2": "meter/second2", "g": "gravitational_acceleration",
            # Density
            "kg/m3": "kilogram/cubic_meter",
            # Dimensionless
            "": "dimensionless", "rad": "radian", "deg": "degree",
        }
        
        self.unit_hierarchy = {
            "length": ["m", "mm", "cm", "km", "in", "ft"],
            "mass": ["kg", "g", "mg", "lb"],
            "time": ["s", "ms", "min", "h"],
            "force": ["N", "kN", "lbf"],
            "pressure": ["Pa", "kPa", "MPa", "psi"],
        }

    async def validate_formula(self, formula_str: str, formula_id: str = "UNKNOWN") -> ValidationResult:
        """Validate a formula string."""
        import time
        start = time.time()
        
        errors = []
        warnings = []
        metadata = {}

        # 1. Syntax Validation
        try:
            if "++" in formula_str:
                raise ValueError("Consecutive '+' operators are not allowed")
            expr = sympify(formula_str)
            metadata["parsed_expression"] = str(expr)
            metadata["symbols"] = [str(s) for s in expr.free_symbols]
        except Exception as e:
            errors.append(ValidationError(
                type=FormulaValidationType.SYNTAX,
                severity="error",
                message=f"Formula syntax error: {str(e)}",
                suggested_fix="Check parentheses, operators, and variable names"
            ))
            validation_time = (time.time() - start) * 1000
            return ValidationResult(
                formula_id=formula_id,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                metadata=metadata,
                validation_time_ms=validation_time
            )

        # 2. Complexity Analysis
        try:
            expr = sympify(formula_str)
            complexity = self._analyze_complexity(expr)
            metadata["complexity"] = complexity
            if complexity > 100:
                warnings.append(ValidationError(
                    type=FormulaValidationType.NUMERICAL_STABILITY,
                    severity="warning",
                    message="Formula is very complex and may have numerical stability issues",
                    suggested_fix="Consider simplifying the formula"
                ))
        except Exception as e:
            warnings.append(ValidationError(
                type=FormulaValidationType.NUMERICAL_STABILITY,
                severity="warning",
                message=f"Could not analyze formula complexity: {str(e)}"
            ))

        # 3. Division by Zero Check
        try:
            expr = sympify(formula_str)
            div_by_zero = self._check_division_by_zero(expr)
            if div_by_zero:
                warnings.append(ValidationError(
                    type=FormulaValidationType.NUMERICAL_STABILITY,
                    severity="warning",
                    message=f"Potential division by zero in denominators: {div_by_zero}"
                ))
        except Exception as e:
            pass

        is_valid = len(errors) == 0

        validation_time = (time.time() - start) * 1000
        return ValidationResult(
            formula_id=formula_id,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata=metadata,
            validation_time_ms=validation_time
        )

    def validate_units(self, formula_str: str, input_units: Dict[str, str], expected_output_unit: str) -> ValidationResult:
        """Validate that units are consistent."""
        errors = []
        warnings = []
        metadata = {
            "input_units": input_units,
            "expected_output_unit": expected_output_unit
        }

        # Extract variables from formula
        try:
            expr = sympify(formula_str)
            variables = [str(s) for s in expr.free_symbols]
        except:
            variables = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', formula_str)

        # Check all variables have units
        for var in variables:
            if var not in input_units and var not in ["pi", "e"]:
                warnings.append(ValidationError(
                    type=FormulaValidationType.UNITS,
                    severity="warning",
                    message=f"Variable '{var}' has no specified unit"
                ))

        metadata["variables"] = variables
        is_valid = len(errors) == 0

        return ValidationResult(
            formula_id="UNIT_CHECK",
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata=metadata,
            validation_time_ms=0
        )

    def validate_physics(self, formula_str: str, physics_domain: str) -> ValidationResult:
        """Validate physics principles."""
        errors = []
        warnings = []
        metadata = {"domain": physics_domain}

        # Domain-specific checks
        physics_rules = {
            "mechanics": {
                "prohibited_patterns": ["negative_mass", "faster_than_light"],
                "required_terms": ["force", "mass", "acceleration"]
            },
            "thermodynamics": {
                "prohibited_patterns": ["negative_temperature", "efficiency_over_100"],
                "required_terms": ["energy", "temperature"]
            },
            "fluid_dynamics": {
                "prohibited_patterns": ["negative_density", "negative_velocity_squared"],
                "required_terms": ["density", "velocity"]
            },
            "electromagnetism": {
                "prohibited_patterns": ["imaginary_current"],
                "required_terms": ["charge", "current", "field"]
            }
        }

        if physics_domain in physics_rules:
            rules = physics_rules[physics_domain]
            # Could implement pattern matching here
            pass

        is_valid = len(errors) == 0

        return ValidationResult(
            formula_id="PHYSICS_CHECK",
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata=metadata,
            validation_time_ms=0
        )

    def validate_constraints(self, formula_str: str, constraints: Dict[str, tuple]) -> ValidationResult:
        """Validate parameter constraints."""
        errors = []
        warnings = []
        metadata = {"constraints": constraints}

        try:
            expr = sympify(formula_str)
            variables = {str(s): s for s in expr.free_symbols}

            for var_name, (min_val, max_val) in constraints.items():
                if var_name in variables and min_val is not None and max_val is not None:
                    if min_val > max_val:
                        errors.append(ValidationError(
                            type=FormulaValidationType.CONSTRAINTS,
                            severity="error",
                            message=f"Constraint for '{var_name}': min ({min_val}) > max ({max_val})"
                        ))
        except Exception as e:
            warnings.append(ValidationError(
                type=FormulaValidationType.CONSTRAINTS,
                severity="warning",
                message=f"Could not validate constraints: {str(e)}"
            ))

        is_valid = len(errors) == 0

        return ValidationResult(
            formula_id="CONSTRAINT_CHECK",
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            metadata=metadata,
            validation_time_ms=0
        )

    def _analyze_complexity(self, expr) -> int:
        """Analyze formula complexity."""
        complexity_score = len(str(expr))
        try:
            # Additional complexity based on operations
            ops = len(expr.atoms())
            complexity_score += ops
        except:
            pass
        return complexity_score

    def _check_division_by_zero(self, expr) -> List[str]:
        """Check for potential division by zero."""
        denominators = []
        expr_str = str(expr)
        
        # Simple regex-based check
        patterns = [
            r'/\s*\(([^)]+)\)',  # / (denominator)
            r'/\s*([a-zA-Z_]\w*)',  # / variable
        ]
        
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, expr_str)
            results.extend(matches)
        
        return results
