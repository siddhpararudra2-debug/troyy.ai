"""
Physics Engine — Core Engineering Physics
"""
from .mechanics import MechanicsEngine
from .fluids import FluidEngine
from .thermodynamics import ThermodynamicsEngine
from .electromagnetics import ElectromagneticsEngine

__all__ = [
    "MechanicsEngine",
    "FluidEngine",
    "ThermodynamicsEngine",
    "ElectromagneticsEngine",
]
