"""
Uncertainty Engine — Gaussian uncertainty propagation
"""
from typing import Dict, Any, List, Callable
from dataclasses import dataclass


@dataclass
class UncertainQuantity:
    value: float
    uncertainty: float
    unit: str = ""


@dataclass
class UncertaintyResult:
    value: float
    uncertainty: float
    relative_uncertainty: float
    formula: str


class UncertaintyEngine:
    """Calculates uncertainty propagation"""

    def add_subtract(
        self,
        quantities: List[UncertainQuantity],
        operation: str = "add",
    ) -> UncertaintyResult:
        """Add/subtract: u = sqrt(du1² + du2² + ...)"""
        total_value = 0.0
        for q in quantities:
            if operation == "add":
                total_value += q.value
            else:
                total_value -= q.value

        total_uncert_sq = 0.0
        for q in quantities:
            total_uncert_sq += q.uncertainty**2

        total_uncert = total_uncert_sq**0.5
        rel_uncert = total_uncert / abs(total_value) if total_value != 0 else 0.0

        return UncertaintyResult(
            value=total_value,
            uncertainty=total_uncert,
            relative_uncertainty=rel_uncert,
            formula="u = sqrt(u1² + u2² + ...)",
        )

    def multiply_divide(
        self,
        quantities: List[UncertainQuantity],
        operation: str = "multiply",
    ) -> UncertaintyResult:
        """Multiply/divide: u/x = sqrt( (u1/x1)² + ... )"""
        total_value = 1.0
        rel_uncert_sq = 0.0

        for i, q in enumerate(quantities):
            if operation == "multiply" or i == 0:
                total_value *= q.value
            else:
                total_value /= q.value

            rel_uncert_sq += (q.uncertainty / q.value)**2 if q.value !=0 else 0.0

        total_uncert = total_value * (rel_uncert_sq**0.5)
        rel_uncert = rel_uncert_sq**0.5

        return UncertaintyResult(
            value=total_value,
            uncertainty=total_uncert,
            relative_uncertainty=rel_uncert,
            formula="u/x = sqrt( (u1/x1)² + ... )",
        )

    def power(
        self,
        quantity: UncertainQuantity,
        exponent: float,
    ) -> UncertaintyResult:
        """x^n: u/x = n * u_q/q"""
        result_value = quantity.value**exponent
        rel_uncert = exponent * (quantity.uncertainty / quantity.value) if quantity.value !=0 else 0.0
        result_uncert = rel_uncert * result_value

        return UncertaintyResult(
            value=result_value,
            uncertainty=result_uncert,
            relative_uncertainty=rel_uncert,
            formula="u/x = n * u_q/q",
        )

    def propagate(
        self,
        func: Callable[..., float],
        quantities: Dict[str, UncertainQuantity],
        h: float = 1e-6,
    ) -> UncertaintyResult:
        """General uncertainty propagation using central differences"""
        value_dict = {k: v.value for k, v in quantities.items()}
        result_value = func(**value_dict)

        total_uncert_sq = 0.0
        for name, q in quantities.items():
            # Central difference for derivative
            v_plus = value_dict.copy()
            v_plus[name] = q.value + h

            v_minus = value_dict.copy()
            v_minus[name] = q.value - h

            deriv = (func(**v_plus) - func(**v_minus)) / (2 * h)

            total_uncert_sq += (deriv * q.uncertainty)**2

        total_uncert = total_uncert_sq**0.5
        rel_uncert = total_uncert / abs(result_value) if result_value != 0 else 0.0

        return UncertaintyResult(
            value=result_value,
            uncertainty=total_uncert,
            relative_uncertainty=rel_uncert,
            formula="General propagation via central differences",
        )
