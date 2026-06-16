"""
Troy — Formula Registry
Decorator-based formula registration system with discovery and search.
Every engineering formula registers itself via the @register_formula decorator,
making it discoverable by the API and calculation engine.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable

from app.core.logging import get_logger

logger = get_logger("registry")


# ── Parameter Definition ─────────────────────────────────────────
@dataclass
class ParameterDef:
    """Definition of a formula input parameter."""
    name: str
    symbol: str          # LaTeX symbol (e.g., "\\rho")
    unit: str            # SI unit string (e.g., "kg/m^3")
    description: str
    min_value: float | None = None
    max_value: float | None = None
    default: float | None = None


@dataclass
class OutputDef:
    """Definition of a formula output."""
    name: str
    symbol: str
    unit: str
    description: str


# ── Formula Definition ───────────────────────────────────────────
@dataclass
class FormulaDefinition:
    """Complete definition of a registered formula."""
    id: str                              # e.g., "aerospace.aerodynamics.lift_force"
    domain: str                          # e.g., "aerospace"
    category: str                        # e.g., "aerodynamics"
    name: str                            # e.g., "Lift Force"
    description: str
    formula_latex: str                   # LaTeX representation
    parameters: list[ParameterDef]
    outputs: list[OutputDef]
    reference: str = ""                  # Textbook/standard reference
    func: Callable | None = None         # The actual computation function
    tags: list[str] = field(default_factory=list)


# ── Registry Singleton ───────────────────────────────────────────
class FormulaRegistry:
    """
    Central registry of all engineering formulas.
    Formulas self-register via the @register_formula decorator.
    """

    _instance: FormulaRegistry | None = None
    _formulas: dict[str, FormulaDefinition]

    def __new__(cls) -> FormulaRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._formulas = {}
        return cls._instance

    def register(self, formula: FormulaDefinition) -> None:
        """Register a formula definition."""
        if formula.id in self._formulas:
            logger.warning(f"Overwriting formula: {formula.id}")
        self._formulas[formula.id] = formula
        logger.debug(f"Registered formula: {formula.id}")

    def get(self, formula_id: str) -> FormulaDefinition | None:
        """Get a formula by its ID."""
        return self._formulas.get(formula_id)

    def list_all(self) -> list[FormulaDefinition]:
        """List all registered formulas."""
        return list(self._formulas.values())

    def list_by_domain(self, domain: str) -> list[FormulaDefinition]:
        """List formulas filtered by domain."""
        return [f for f in self._formulas.values() if f.domain == domain]

    def list_by_category(self, domain: str, category: str) -> list[FormulaDefinition]:
        """List formulas filtered by domain and category."""
        return [
            f for f in self._formulas.values()
            if f.domain == domain and f.category == category
        ]

    def search(self, query: str) -> list[FormulaDefinition]:
        """Search formulas by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for f in self._formulas.values():
            searchable = f"{f.name} {f.description} {' '.join(f.tags)}".lower()
            if query_lower in searchable:
                results.append(f)
        return results

    @property
    def count(self) -> int:
        return len(self._formulas)

    def get_domains(self) -> list[str]:
        """Get list of all registered domains."""
        return sorted(set(f.domain for f in self._formulas.values()))

    def get_categories(self, domain: str) -> list[str]:
        """Get categories for a specific domain."""
        return sorted(set(
            f.category for f in self._formulas.values()
            if f.domain == domain
        ))


# ── Global registry instance ────────────────────────────────────
registry = FormulaRegistry()


# ── Registration Decorator ───────────────────────────────────────
def register_formula(
    id: str,
    domain: str,
    category: str,
    name: str,
    description: str,
    formula_latex: str,
    parameters: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
    reference: str = "",
    tags: list[str] | None = None,
) -> Callable:
    """
    Decorator to register an engineering formula.

    Usage:
        @register_formula(
            id="aerospace.aerodynamics.lift_force",
            domain="aerospace",
            category="aerodynamics",
            name="Lift Force",
            ...
        )
        def lift_force(rho, v, S, C_L):
            ...
    """
    def decorator(func: Callable) -> Callable:
        formula_def = FormulaDefinition(
            id=id,
            domain=domain,
            category=category,
            name=name,
            description=description,
            formula_latex=formula_latex,
            parameters=[ParameterDef(**p) for p in parameters],
            outputs=[OutputDef(**o) for o in outputs],
            reference=reference,
            func=func,
            tags=tags or [],
        )
        registry.register(formula_def)
        return func

    return decorator
