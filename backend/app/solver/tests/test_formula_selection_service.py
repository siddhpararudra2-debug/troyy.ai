"""
Troy — Formula Selection Service Tests
"""

from __future__ import annotations

import pytest
from app.solver.models.domain_models import VariableData
from app.solver.services.formula_selection_service import FormulaSelectionService


@pytest.mark.asyncio
async def test_formula_selection():
    service = FormulaSelectionService()
    variables = VariableData(
        known={"m_payload": {"value": 1.0}},
        unknown=["T_motor", "P", "v_i"],
        derived={"m": {"value": 3.5}},
    )
    formulas = await service.select_formulas("drones", variables)
    
    assert len(formulas) > 0
    formula_ids = [f.formula_id for f in formulas]
    assert "drones.flight_dynamics.hover_thrust" in formula_ids
