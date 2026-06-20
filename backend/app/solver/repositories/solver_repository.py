"""
Troy — Solver Repository
Async database persistence for solver sessions, runs, and all
associated child records (requirements, assumptions, constraints,
variables, recommendations).

Uses raw ``sqlalchemy.text`` queries consistent with the rest of
the Troy codebase rather than ORM session.add() patterns.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.solver.models.domain_models import SolverState

logger = logging.getLogger("solver.repository")


class SolverRepository:
    """Persistence layer for the Engineering Solver & Reasoning Engine."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Session ──────────────────────────────────────────────────
    async def get_or_create_session(
        self,
        session_id: str,
        project_id: str,
        user_query: str,
    ) -> str:
        """Return existing session or create a new one."""
        result = await self.db.execute(
            text("SELECT id FROM solver_sessions WHERE id = :id"),
            {"id": session_id},
        )
        row = result.fetchone()
        if row:
            return row[0]

        now = datetime.utcnow().isoformat()
        await self.db.execute(
            text("""
                INSERT INTO solver_sessions (id, project_id, user_query, status, created_at, updated_at)
                VALUES (:id, :pid, :query, 'pending', :now, :now)
            """),
            {"id": session_id, "pid": project_id, "query": user_query, "now": now},
        )
        await self.db.commit()
        logger.debug(f"Created solver session {session_id}")
        return session_id

    async def update_session_status(self, session_id: str, status: str) -> None:
        """Update the status of a solver session."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            text("UPDATE solver_sessions SET status = :status, updated_at = :now WHERE id = :id"),
            {"id": session_id, "status": status, "now": now},
        )
        await self.db.commit()

    # ── Full Run Persistence ─────────────────────────────────────
    async def save_run(
        self,
        run_id: str,
        session_id: str,
        domain: str,
        status: str,
        execution_time_ms: float,
        error_message: Optional[str],
        state: SolverState,
    ) -> str:
        """
        Persist a complete solver run and all its child records
        (requirements, assumptions, constraints, variables, recommendations).
        """
        now = datetime.utcnow().isoformat()

        # ── Run header ───────────────────────────────────────────
        await self.db.execute(
            text("""
                INSERT INTO solver_runs
                    (id, session_id, domain, status, execution_time_ms, error_message, created_at)
                VALUES
                    (:id, :sid, :domain, :status, :exec_ms, :error, :now)
            """),
            {
                "id": run_id,
                "sid": session_id,
                "domain": domain,
                "status": status,
                "exec_ms": execution_time_ms,
                "error": error_message,
                "now": now,
            },
        )

        # ── Requirements ─────────────────────────────────────────
        req = state.requirements
        await self.db.execute(
            text("""
                INSERT INTO solver_requirements
                    (id, run_id, project_type, mission_type, payload,
                     flight_time, missing_requirements, raw_extracted)
                VALUES
                    (:id, :rid, :pt, :mt, :pl, :ft, :missing, :raw)
            """),
            {
                "id": f"req_{run_id}",
                "rid": run_id,
                "pt": req.project_type,
                "mt": req.mission_type,
                "pl": req.payload,
                "ft": req.flight_time,
                "missing": json.dumps(req.missing_requirements),
                "raw": json.dumps(req.raw_extracted),
            },
        )

        # ── Assumptions ──────────────────────────────────────────
        for idx, a in enumerate(state.assumptions):
            await self.db.execute(
                text("""
                    INSERT INTO solver_assumptions
                        (id, run_id, missing_information, assumption, reasoning,
                         confidence_score, editable, user_override)
                    VALUES
                        (:id, :rid, :mi, :ass, :reason, :conf, :edit, :override)
                """),
                {
                    "id": f"ass_{run_id}_{idx}",
                    "rid": run_id,
                    "mi": a.missing_information,
                    "ass": a.assumption,
                    "reason": a.reasoning,
                    "conf": a.confidence_score,
                    "edit": a.editable,
                    "override": a.user_override,
                },
            )

        # ── Constraints ──────────────────────────────────────────
        for idx, c in enumerate(state.constraints):
            await self.db.execute(
                text("""
                    INSERT INTO solver_constraints
                        (id, run_id, category, limit_value, source)
                    VALUES
                        (:id, :rid, :cat, :lim, :src)
                """),
                {
                    "id": f"cons_{run_id}_{idx}",
                    "rid": run_id,
                    "cat": c.category,
                    "lim": c.limit,
                    "src": c.source,
                },
            )

        # ── Variables ────────────────────────────────────────────
        var_idx = 0
        for name, data in state.variables.known.items():
            await self._insert_variable(run_id, var_idx, name, data, "known")
            var_idx += 1

        for name, data in state.variables.derived.items():
            await self._insert_variable(run_id, var_idx, name, data, "derived")
            var_idx += 1

        for name, data in state.variables.constants.items():
            await self._insert_variable(run_id, var_idx, name, data, "constant")
            var_idx += 1

        for name in state.variables.unknown:
            await self.db.execute(
                text("""
                    INSERT INTO solver_variables
                        (id, run_id, name, value, unit, description, var_type)
                    VALUES
                        (:id, :rid, :name, NULL, NULL, :desc, 'unknown')
                """),
                {
                    "id": f"var_{run_id}_{var_idx}",
                    "rid": run_id,
                    "name": name,
                    "desc": f"Unknown: {name}",
                },
            )
            var_idx += 1

        # ── Recommendations ──────────────────────────────────────
        for idx, r in enumerate(state.recommendations.recommendations):
            await self.db.execute(
                text("""
                    INSERT INTO solver_recommendations
                        (id, run_id, recommendation, reasoning,
                         expected_benefits, potential_risks)
                    VALUES
                        (:id, :rid, :rec, :reason, :benefits, :risks)
                """),
                {
                    "id": f"rec_{run_id}_{idx}",
                    "rid": run_id,
                    "rec": r.recommendation,
                    "reason": r.reasoning,
                    "benefits": r.expected_benefits,
                    "risks": r.potential_risks,
                },
            )

        # ── Selected Formulas ────────────────────────────────────
        for idx, f in enumerate(state.selected_formulas):
            await self.db.execute(
                text("""
                    INSERT INTO solver_selected_formulas
                        (id, run_id, formula_id, name, relevance_score, reasoning,
                         required_inputs, expected_outputs, dependencies)
                    VALUES
                        (:id, :rid, :fid, :name, :score, :reason, :req_inputs, :exp_outputs, :deps)
                """),
                {
                    "id": f"selfor_{run_id}_{idx}",
                    "rid": run_id,
                    "fid": f.formula_id,
                    "name": f.name,
                    "score": f.relevance_score,
                    "reason": f.reasoning,
                    "req_inputs": json.dumps(f.required_inputs),
                    "exp_outputs": json.dumps(f.expected_outputs),
                    "deps": json.dumps(f.dependencies),
                },
            )

        await self.db.commit()
        logger.info(f"Persisted solver run {run_id}")
        return run_id


    # ── Helpers ───────────────────────────────────────────────────
    async def _insert_variable(
        self,
        run_id: str,
        idx: int,
        name: str,
        data: Dict[str, Any],
        var_type: str,
    ) -> None:
        """Insert a single variable row."""
        value = data.get("value")
        if isinstance(value, (int, float)):
            value = float(value)
        else:
            value = None

        await self.db.execute(
            text("""
                INSERT INTO solver_variables
                    (id, run_id, name, value, unit, description, var_type)
                VALUES
                    (:id, :rid, :name, :val, :unit, :desc, :vtype)
            """),
            {
                "id": f"var_{run_id}_{idx}",
                "rid": run_id,
                "name": name,
                "val": value,
                "unit": data.get("unit"),
                "desc": data.get("description"),
                "vtype": var_type,
            },
        )

    # ── Read Queries ─────────────────────────────────────────────
    async def get_session_runs(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve all runs for a session."""
        result = await self.db.execute(
            text("""
                SELECT id, domain, status, execution_time_ms, error_message, created_at
                FROM solver_runs WHERE session_id = :sid ORDER BY created_at DESC
            """),
            {"sid": session_id},
        )
        rows = result.fetchall()
        return [
            {
                "id": r[0],
                "domain": r[1],
                "status": r[2],
                "execution_time_ms": r[3],
                "error_message": r[4],
                "created_at": r[5],
            }
            for r in rows
        ]

    async def get_project_solver_history(
        self, project_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent solver sessions for a project (for memory integration)."""
        result = await self.db.execute(
            text("""
                SELECT s.id, s.user_query, s.status, s.created_at,
                       COUNT(r.id) as run_count
                FROM solver_sessions s
                LEFT JOIN solver_runs r ON r.session_id = s.id
                WHERE s.project_id = :pid
                GROUP BY s.id
                ORDER BY s.created_at DESC
                LIMIT :lim
            """),
            {"pid": project_id, "lim": limit},
        )
        rows = result.fetchall()
        return [
            {
                "session_id": r[0],
                "user_query": r[1],
                "status": r[2],
                "created_at": r[3],
                "run_count": r[4],
            }
            for r in rows
        ]

    async def get_latest_session_state(
        self, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve the latest run state for a given session."""
        # 1. Get session info
        sess_result = await self.db.execute(
            text("SELECT project_id, user_query, status FROM solver_sessions WHERE id = :sid"),
            {"sid": session_id},
        )
        sess_row = sess_result.fetchone()
        if not sess_row:
            return None

        project_id, user_query, status = sess_row

        # 2. Get latest run
        run_result = await self.db.execute(
            text("SELECT id, domain, status, execution_time_ms, error_message FROM solver_runs WHERE session_id = :sid ORDER BY created_at DESC LIMIT 1"),
            {"sid": session_id},
        )
        run_row = run_result.fetchone()
        if not run_row:
            # Rebuild a bare state if no runs exist yet
            return {
                "session_id": session_id,
                "project_id": project_id,
                "user_query": user_query,
                "status": status,
                "domain": "multi",
                "errors": [],
            }

        run_id, domain, run_status, exec_time, error_msg = run_row

        # 3. Load Requirements
        req_res = await self.db.execute(
            text("SELECT project_type, mission_type, payload, flight_time, missing_requirements, raw_extracted FROM solver_requirements WHERE run_id = :rid"),
            {"rid": run_id},
        )
        req_row = req_res.fetchone()
        requirements = {}
        if req_row:
            requirements = {
                "project_type": req_row[0],
                "mission_type": req_row[1],
                "payload": req_row[2],
                "flight_time": req_row[3],
                "missing_requirements": json.loads(req_row[4]) if req_row[4] else [],
                "raw_extracted": json.loads(req_row[5]) if req_row[5] else {},
            }

        # 4. Load Assumptions
        ass_res = await self.db.execute(
            text("SELECT missing_information, assumption, reasoning, confidence_score, editable, user_override FROM solver_assumptions WHERE run_id = :rid"),
            {"rid": run_id},
        )
        assumptions = []
        for r in ass_res.fetchall():
            assumptions.append({
                "missing_information": r[0],
                "assumption": r[1],
                "reasoning": r[2],
                "confidence_score": r[3],
                "editable": bool(r[4]),
                "user_override": r[5],
            })

        # 5. Load Constraints
        const_res = await self.db.execute(
            text("SELECT category, limit_value, source FROM solver_constraints WHERE run_id = :rid"),
            {"rid": run_id},
        )
        constraints = []
        for r in const_res.fetchall():
            constraints.append({
                "category": r[0],
                "limit": r[1],
                "source": r[2],
            })

        # 6. Load Variables
        var_res = await self.db.execute(
            text("SELECT name, value, unit, description, var_type FROM solver_variables WHERE run_id = :rid"),
            {"rid": run_id},
        )
        variables = {
            "known": {},
            "unknown": [],
            "dependent": [],
            "derived": {},
            "constants": {},
        }
        for r in var_res.fetchall():
            name, val, unit, desc, vtype = r
            entry = {"value": val, "unit": unit, "description": desc}
            if vtype == "known":
                variables["known"][name] = entry
            elif vtype == "derived":
                variables["derived"][name] = entry
            elif vtype == "constant":
                variables["constants"][name] = entry
            elif vtype == "unknown":
                variables["unknown"].append(name)

        # 7. Load Recommendations
        rec_res = await self.db.execute(
            text("SELECT recommendation, reasoning, expected_benefits, potential_risks FROM solver_recommendations WHERE run_id = :rid"),
            {"rid": run_id},
        )
        recs = []
        for r in rec_res.fetchall():
            recs.append({
                "recommendation": r[0],
                "reasoning": r[1],
                "expected_benefits": r[2],
                "potential_risks": r[3],
            })


        # 8. Load Selected Formulas
        formula_res = await self.db.execute(
            text("SELECT formula_id, name, relevance_score, reasoning, required_inputs, expected_outputs, dependencies FROM solver_selected_formulas WHERE run_id = :rid"),
            {"rid": run_id},
        )
        selected_formulas = []
        for r in formula_res.fetchall():
            selected_formulas.append({
                "formula_id": r[0],
                "name": r[1],
                "relevance_score": r[2],
                "reasoning": r[3],
                "required_inputs": json.loads(r[4]) if r[4] else [],
                "expected_outputs": json.loads(r[5]) if r[5] else [],
                "dependencies": json.loads(r[6]) if r[6] else [],
            })

        errors = [error_msg] if error_msg else []

        return {
            "session_id": session_id,
            "project_id": project_id,
            "user_query": user_query,
            "status": run_status,
            "domain": domain,
            "errors": errors,
            "requirements": requirements,
            "assumptions": assumptions,
            "constraints": constraints,
            "variables": variables,
            "selected_formulas": selected_formulas,
            "recommendations": {
                "recommendations": recs,
                "reasoning": "Restored from database run record",
            },
        }

