"""
Unit converter for Engineering OS.
Handles SI, Imperial, and engineering unit conversions with dimensional analysis.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class UnitConverter:
    """
    Comprehensive unit conversion system for engineering calculations.
    Supports SI, Imperial, and custom engineering units.
    """
    
    # Base SI units
    SI_BASE = {
        "m": {"dimension": "length", "si": 1.0},
        "kg": {"dimension": "mass", "si": 1.0},
        "s": {"dimension": "time", "si": 1.0},
        "A": {"dimension": "current", "si": 1.0},
        "K": {"dimension": "temperature", "si": 1.0},
        "mol": {"dimension": "amount", "si": 1.0},
        "cd": {"dimension": "luminosity", "si": 1.0},
    }
    
    # Derived units and their SI conversion factors
    UNITS = {
        # Length
        "m": {"dimension": "length", "si": 1.0},
        "km": {"dimension": "length", "si": 1000.0},
        "cm": {"dimension": "length", "si": 0.01},
        "mm": {"dimension": "length", "si": 0.001},
        "um": {"dimension": "length", "si": 1e-6},
        "nm": {"dimension": "length", "si": 1e-9},
        "in": {"dimension": "length", "si": 0.0254},
        "ft": {"dimension": "length", "si": 0.3048},
        "yd": {"dimension": "length", "si": 0.9144},
        "mi": {"dimension": "length", "si": 1609.344},
        # Mass
        "kg": {"dimension": "mass", "si": 1.0},
        "g": {"dimension": "mass", "si": 0.001},
        "mg": {"dimension": "mass", "si": 1e-6},
        "tonne": {"dimension": "mass", "si": 1000.0},
        "lb": {"dimension": "mass", "si": 0.45359237},
        "oz": {"dimension": "mass", "si": 0.0283495},
        "slug": {"dimension": "mass", "si": 14.5939},
        # Time
        "s": {"dimension": "time", "si": 1.0},
        "ms": {"dimension": "time", "si": 0.001},
        "us": {"dimension": "time", "si": 1e-6},
        "min": {"dimension": "time", "si": 60.0},
        "hr": {"dimension": "time", "si": 3600.0},
        "day": {"dimension": "time", "si": 86400.0},
        # Force
        "N": {"dimension": "force", "si": 1.0},
        "kN": {"dimension": "force", "si": 1000.0},
        "lbf": {"dimension": "force", "si": 4.4482216152605},
        "kip": {"dimension": "force", "si": 4448.2216},
        # Pressure
        "Pa": {"dimension": "pressure", "si": 1.0},
        "kPa": {"dimension": "pressure", "si": 1000.0},
        "MPa": {"dimension": "pressure", "si": 1e6},
        "GPa": {"dimension": "pressure", "si": 1e9},
        "bar": {"dimension": "pressure", "si": 100000.0},
        "atm": {"dimension": "pressure", "si": 101325.0},
        "psi": {"dimension": "pressure", "si": 6894.757293168},
        "psf": {"dimension": "pressure", "si": 47.8802589803},
        # Energy
        "J": {"dimension": "energy", "si": 1.0},
        "kJ": {"dimension": "energy", "si": 1000.0},
        "MJ": {"dimension": "energy", "si": 1e6},
        "Wh": {"dimension": "energy", "si": 3600.0},
        "kWh": {"dimension": "energy", "si": 3.6e6},
        "cal": {"dimension": "energy", "si": 4.184},
        "BTU": {"dimension": "energy", "si": 1055.06},
        "ft_lbf": {"dimension": "energy", "si": 1.3558179483},
        # Power
        "W": {"dimension": "power", "si": 1.0},
        "kW": {"dimension": "power", "si": 1000.0},
        "MW": {"dimension": "power", "si": 1e6},
        "hp": {"dimension": "power", "si": 745.69987158227},
        # Temperature
        "K": {"dimension": "temperature", "si": 1.0, "offset": 0},
        "degC": {"dimension": "temperature", "si": 1.0, "offset": 273.15},
        "degF": {"dimension": "temperature", "si": 0.5555555555555556, "offset": 255.372222},
        # Area
        "m2": {"dimension": "area", "si": 1.0},
        "cm2": {"dimension": "area", "si": 1e-4},
        "mm2": {"dimension": "area", "si": 1e-6},
        "in2": {"dimension": "area", "si": 0.00064516},
        "ft2": {"dimension": "area", "si": 0.09290304},
        # Volume
        "m3": {"dimension": "volume", "si": 1.0},
        "L": {"dimension": "volume", "si": 0.001},
        "mL": {"dimension": "volume", "si": 1e-6},
        "gal": {"dimension": "volume", "si": 0.003785411784},
        "ft3": {"dimension": "volume", "si": 0.028316846592},
        # Velocity
        "m_s": {"dimension": "velocity", "si": 1.0},
        "km_h": {"dimension": "velocity", "si": 0.27777777777778},
        "ft_s": {"dimension": "velocity", "si": 0.3048},
        "mph": {"dimension": "velocity", "si": 0.44704},
        "knot": {"dimension": "velocity", "si": 0.514444},
        # Acceleration
        "m_s2": {"dimension": "acceleration", "si": 1.0},
        "g": {"dimension": "acceleration", "si": 9.80665},
        # Moment of inertia
        "kg_m2": {"dimension": "inertia", "si": 1.0},
        "lb_ft2": {"dimension": "inertia", "si": 0.0421401},
    }

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> dict:
        """Convert a value between units."""
        if from_unit not in cls.UNITS:
            raise ValueError(f"Unknown unit: {from_unit}")
        if to_unit not in cls.UNITS:
            raise ValueError(f"Unknown unit: {to_unit}")
        
        from_info = cls.UNITS[from_unit]
        to_info = cls.UNITS[to_unit]
        
        if from_info["dimension"] != to_info["dimension"]:
            raise ValueError(
                f"Dimension mismatch: {from_unit} ({from_info['dimension']}) "
                f"vs {to_unit} ({to_info['dimension']})"
            )
        
        # Handle temperature offsets
        from_offset = from_info.get("offset", 0)
        to_offset = to_info.get("offset", 0)
        
        value_si = (value + from_offset) * from_info["si"]
        result = value_si / to_info["si"] - to_offset
        
        return {
            "original_value": value,
            "original_unit": from_unit,
            "converted_value": result,
            "target_unit": to_unit,
            "dimension": from_info["dimension"],
            "conversion_factor": to_info["si"] / from_info["si"],
        }

    @classmethod
    def is_convertible(cls, unit1: str, unit2: str) -> bool:
        """Check if two units are dimensionally compatible."""
        if unit1 not in cls.UNITS or unit2 not in cls.UNITS:
            return False
        return cls.UNITS[unit1]["dimension"] == cls.UNITS[unit2]["dimension"]

    @classmethod
    def get_dimension(cls, unit: str) -> Optional[str]:
        """Get the dimension of a unit."""
        info = cls.UNITS.get(unit)
        return info["dimension"] if info else None

    @classmethod
    def list_units_by_dimension(cls, dimension: str) -> list[str]:
        """List all units of a given dimension."""
        return [u for u, info in cls.UNITS.items() if info["dimension"] == dimension]

    @classmethod
    def get_si_unit(cls, dimension: str) -> Optional[str]:
        """Get the SI base unit for a dimension."""
        si_units = {
            "length": "m", "mass": "kg", "time": "s",
            "force": "N", "pressure": "Pa", "energy": "J",
            "power": "W", "temperature": "K",
            "area": "m2", "volume": "m3", "velocity": "m_s",
            "acceleration": "m_s2", "inertia": "kg_m2",
            "current": "A", "amount": "mol", "luminosity": "cd",
        }
        return si_units.get(dimension)