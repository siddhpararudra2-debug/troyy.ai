"""
Troy — Unit Conversion Engine
Uses Pint for dimensional analysis and unit conversion.
"""

from __future__ import annotations

from dataclasses import dataclass

import pint

from app.core.logging import get_logger

logger = get_logger("units")

# ── Unit Registry (singleton) ────────────────────────────────────
ureg = pint.UnitRegistry()
Q_ = ureg.Quantity


# ── Conversion Result ────────────────────────────────────────────
@dataclass
class ConversionResult:
    """Result of a unit conversion."""
    original_value: float
    original_unit: str
    converted_value: float
    target_unit: str
    formula: str  # e.g., "1 m = 3.28084 ft"


# ── Unit Conversion Functions ────────────────────────────────────
def convert_unit(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """
    Convert a value from one unit to another.

    Args:
        value: Numerical value to convert
        from_unit: Source unit string (e.g., "m/s", "kg", "psi")
        to_unit: Target unit string

    Returns:
        ConversionResult with converted value and formula

    Raises:
        pint.DimensionalityError: If units are incompatible
    """
    try:
        quantity = Q_(value, from_unit)
        converted = quantity.to(to_unit)

        # Build the conversion formula string
        factor = Q_(1, from_unit).to(to_unit).magnitude
        formula = f"1 {from_unit} = {factor:.6g} {to_unit}"

        return ConversionResult(
            original_value=value,
            original_unit=from_unit,
            converted_value=converted.magnitude,
            target_unit=to_unit,
            formula=formula,
        )

    except pint.DimensionalityError as e:
        raise ValueError(
            f"Cannot convert {from_unit} to {to_unit}: incompatible dimensions"
        ) from e
    except pint.UndefinedUnitError as e:
        raise ValueError(f"Unknown unit: {str(e)}") from e


def get_unit_systems() -> dict[str, dict[str, str]]:
    """
    Return available unit system definitions.

    Returns a mapping of system name → {quantity_type: unit_string}
    """
    return {
        "SI": {
            "length": "m",
            "mass": "kg",
            "time": "s",
            "force": "N",
            "pressure": "Pa",
            "velocity": "m/s",
            "acceleration": "m/s^2",
            "area": "m^2",
            "volume": "m^3",
            "density": "kg/m^3",
            "energy": "J",
            "power": "W",
            "temperature": "K",
            "angle": "rad",
            "angular_velocity": "rad/s",
            "torque": "N*m",
            "voltage": "V",
            "current": "A",
            "resistance": "ohm",
            "capacitance": "F",
            "inductance": "H",
            "frequency": "Hz",
        },
        "Imperial": {
            "length": "ft",
            "mass": "lb",
            "time": "s",
            "force": "lbf",
            "pressure": "psi",
            "velocity": "ft/s",
            "acceleration": "ft/s^2",
            "area": "ft^2",
            "volume": "ft^3",
            "density": "lb/ft^3",
            "energy": "BTU",
            "power": "hp",
            "temperature": "degF",
            "angle": "deg",
            "angular_velocity": "deg/s",
            "torque": "lbf*ft",
            "voltage": "V",
            "current": "A",
            "resistance": "ohm",
            "capacitance": "F",
            "inductance": "H",
            "frequency": "Hz",
        },
    }


def convert_to_system(
    value: float, from_unit: str, target_system: str = "SI"
) -> ConversionResult:
    """
    Convert a value to the preferred unit in a target system.

    Uses dimensional analysis to determine the correct target unit.
    """
    systems = get_unit_systems()
    if target_system not in systems:
        raise ValueError(f"Unknown unit system: {target_system}")

    # Determine the dimension of the source unit
    quantity = Q_(1, from_unit)
    dimensionality = str(quantity.dimensionality)

    # Map common dimensionalities to system units
    dim_map = {
        "[length]": "length",
        "[mass]": "mass",
        "[time]": "time",
        "[length] * [mass] / [time] ** 2": "force",
        "[mass] / [length] / [time] ** 2": "pressure",
        "[length] / [time]": "velocity",
        "[length] / [time] ** 2": "acceleration",
        "[length] ** 2": "area",
        "[length] ** 3": "volume",
        "[mass] / [length] ** 3": "density",
        "[length] ** 2 * [mass] / [time] ** 2": "energy",
        "[length] ** 2 * [mass] / [time] ** 3": "power",
        "[temperature]": "temperature",
    }

    quantity_type = dim_map.get(dimensionality)
    if quantity_type is None:
        raise ValueError(
            f"Cannot auto-detect unit type for dimensionality: {dimensionality}"
        )

    target_unit = systems[target_system][quantity_type]
    return convert_unit(value, from_unit, target_unit)
