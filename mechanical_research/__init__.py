"""Mechanical Deep Research Platform - Module 2 for Sprint 16."""
from .material_research import MaterialResearch
from .structural_research import StructuralResearch
from .manufacturing_research import ManufacturingResearch
from .thermal_research import ThermalResearch
from .fatigue_research import FatigueResearch
from .benchmark_engine import BenchmarkEngine
from .failure_analysis import FailureAnalysis

__all__ = [
    "MaterialResearch",
    "StructuralResearch",
    "ManufacturingResearch",
    "ThermalResearch",
    "FatigueResearch",
    "BenchmarkEngine",
    "FailureAnalysis",
]
