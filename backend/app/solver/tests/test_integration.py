"""
Troy — Solver Pipeline Integration Tests
"""

from __future__ import annotations

import time
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.solver.services.orchestration_service import OrchestrationService


@pytest.mark.asyncio
async def test_full_solver_pipeline(db_session: AsyncSession):
    """
    Run the full 10-phase solver reasoning pipeline on a drone design query.
    Verify:
      - Requirements, assumptions, constraints, variables, and formulas are identified.
      - Chained calculations execute via SymPy Calculation Core.
      - Result interpretation and design recommendations are generated.
      - Assumptions, constraints, and recommendations are persisted to project memory.
      - A comprehensive solver report is generated and saved as a document.
      - The complete run record is saved in the solver repository.
    """
    # Initialize default project in DB if missing (safety check for testing)
    await db_session.execute(
        text("""
            INSERT OR IGNORE INTO projects (id, name, description, domain, status)
            VALUES ('test_project', 'Test Project', 'Test workspace', 'multi', 'active')
        """)
    )
    await db_session.commit()

    orchestrator = OrchestrationService()
    session_id = "test_sess_integration"
    project_id = "test_project"
    user_query = "Design a surveillance drone carrying 2.0 kg payload with 30 minutes endurance"

    start_time = time.perf_counter()
    state = await orchestrator.solve(
        session_id=session_id,
        project_id=project_id,
        user_query=user_query,
        db=db_session,
    )
    elapsed_s = time.perf_counter() - start_time

    # 1. Basic properties
    assert not state.errors, f"Pipeline errors: {state.errors}"
    assert state.session_id == session_id
    assert state.project_id == project_id
    assert state.domain == "drones"

    # 2. Requirements & Assumptions
    assert "2.0kg" in state.requirements.payload
    assert "30minutes" in state.requirements.flight_time
    assert len(state.assumptions) > 0
    
    # 3. Constraints & Variables
    assert len(state.constraints) > 0
    assert "m_payload" in state.variables.known
    assert "T_motor" in state.variables.unknown

    # 4. Calculation Core results (e.g. hover thrust, hover power)
    assert len(state.calculation_results) > 0
    assert "T_motor" in state.calculation_results
    assert "P" in state.calculation_results or "T_total" in state.calculation_results

    # 5. Interpretation & Recommendations
    assert state.interpretation.interpretation != ""
    assert len(state.recommendations.recommendations) > 0

    # 6. Report generation
    assert state.generated_report_id is not None

    # 7. Check database persistence
    # Verify Solver Session and Run exist
    res = await db_session.execute(
        text("SELECT status FROM solver_sessions WHERE id = :sid"),
        {"sid": session_id},
    )
    assert res.scalar() == "completed"

    res_run = await db_session.execute(
        text("SELECT domain, status FROM solver_runs WHERE session_id = :sid"),
        {"sid": session_id},
    )
    run_row = res_run.fetchone()
    assert run_row is not None
    assert run_row[0] == "drones"
    assert run_row[1] == "completed"

    # Verify Document exists
    res_doc = await db_session.execute(
        text("SELECT title, doc_type FROM documents WHERE id = :id"),
        {"id": state.generated_report_id},
    )
    doc_row = res_doc.fetchone()
    assert doc_row is not None
    assert "Solver Session Report" in doc_row[0]
    assert doc_row[1] == "custom"

    # Verify Memory Entries exist
    res_mem = await db_session.execute(
        text("SELECT COUNT(*) FROM memory_entries WHERE project_id = :pid"),
        {"pid": project_id},
    )
    assert res_mem.scalar() > 0

    # 8. Performance Check (< 2 seconds target)
    assert elapsed_s < 2.0, f"Full pipeline took too long: {elapsed_s:.2f} seconds"
