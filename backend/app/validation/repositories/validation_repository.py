"""
Troy — Validation Repository
Provides async database CRUD capabilities using raw ``sqlalchemy.text`` queries
matching the repository design pattern in the rest of the application.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.validation.schemas.validation_schemas import (
    ValidationIssueSchema,
    ValidationReportResponse,
    EngineeringReviewResponse,
    RiskItem,
    RiskAssessmentResponse,
    ApprovalDecisionResponse,
    AuditReportResponse,
    AuditLogResponse,
)

logger = logging.getLogger("validation.repository")


class ValidationRepository:
    """Handles async persistence for validation runs, issues, reviews, risks, and approvals."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def save_validation_run(
        self,
        run_id: str,
        project_id: str,
        solver_run_id: Optional[str],
        domain: str,
        total_errors: int,
        total_warnings: int,
        is_approved: bool,
        execution_time_ms: Optional[float],
        issues: List[ValidationIssueSchema],
    ) -> str:
        """Persist a validation run and all its child validation issues."""
        now = datetime.utcnow().isoformat()

        # Insert ValidationRun
        await self.db.execute(
            text("""
                INSERT INTO validation_runs
                    (id, project_id, solver_run_id, domain, total_errors, total_warnings, is_approved, execution_time_ms, created_at)
                VALUES
                    (:id, :pid, :srid, :domain, :errors, :warnings, :approved, :exec_ms, :created)
            """),
            {
                "id": run_id,
                "pid": project_id,
                "srid": solver_run_id,
                "domain": domain,
                "errors": total_errors,
                "warnings": total_warnings,
                "approved": 1 if is_approved else 0,
                "exec_ms": execution_time_ms,
                "created": now,
            },
        )

        # Insert ValidationIssues
        for idx, issue in enumerate(issues):
            issue_id = f"iss_{run_id}_{idx}"
            await self.db.execute(
                text("""
                    INSERT INTO validation_issues
                        (id, run_id, severity, category, message, validator_name, engineering_reasoning, recommendation)
                    VALUES
                        (:id, :rid, :sev, :cat, :msg, :val, :reason, :rec)
                """),
                {
                    "id": issue_id,
                    "rid": run_id,
                    "sev": issue.severity,
                    "cat": issue.category,
                    "msg": issue.message,
                    "val": issue.validator_name,
                    "reason": issue.engineering_reasoning,
                    "rec": issue.recommendation,
                },
            )

        await self.db.commit()
        logger.debug(f"Persisted validation run {run_id}")
        return run_id

    async def save_engineering_review(
        self,
        review_id: str,
        run_id: str,
        checks: Dict[str, str],
        overall_assessment: str,
    ) -> str:
        """Persist the engineering review report details."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            text("""
                INSERT INTO engineering_reviews
                    (id, run_id, design_decisions_check, component_choices_check,
                     structural_choices_check, electrical_choices_check,
                     weight_budgets_check, power_budgets_check,
                     thermal_assumptions_check, overall_assessment, created_at)
                VALUES
                    (:id, :rid, :dec, :comp, :struct, :elec, :weight, :power, :thermal, :overall, :created)
            """),
            {
                "id": review_id,
                "rid": run_id,
                "dec": checks.get("design_decisions_check", "Passed"),
                "comp": checks.get("component_choices_check", "Passed"),
                "struct": checks.get("structural_choices_check", "Passed"),
                "elec": checks.get("electrical_choices_check", "Passed"),
                "weight": checks.get("weight_budgets_check", "Passed"),
                "power": checks.get("power_budgets_check", "Passed"),
                "thermal": checks.get("thermal_assumptions_check", "Passed"),
                "overall": overall_assessment,
                "created": now,
            },
        )
        await self.db.commit()
        return review_id

    async def save_risk_assessment(
        self,
        assessment_id: str,
        run_id: str,
        overall_risk_level: str,
        risks: List[RiskItem],
    ) -> str:
        """Persist a risk assessment record."""
        now = datetime.utcnow().isoformat()
        risks_list = [r.model_dump() for r in risks]
        await self.db.execute(
            text("""
                INSERT INTO risk_assessments (id, run_id, overall_risk_level, risks_json, created_at)
                VALUES (:id, :rid, :level, :risks, :created)
            """),
            {
                "id": assessment_id,
                "rid": run_id,
                "level": overall_risk_level,
                "risks": json.dumps(risks_list),
                "created": now,
            },
        )
        await self.db.commit()
        return assessment_id

    async def save_approval_decision(
        self,
        decision_id: str,
        run_id: str,
        status: str,
        engineering_reasoning: str,
        risk_summary: str,
        validation_summary: str,
    ) -> str:
        """Persist an approval gate decision."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            text("""
                INSERT INTO approval_decisions
                    (id, run_id, status, engineering_reasoning, risk_summary, validation_summary, created_at)
                VALUES
                    (:id, :rid, :status, :reason, :risk, :val, :created)
            """),
            {
                "id": decision_id,
                "rid": run_id,
                "status": status,
                "reason": engineering_reasoning,
                "risk": risk_summary,
                "val": validation_summary,
                "created": now,
            },
        )
        await self.db.commit()
        return decision_id

    async def save_audit_report(
        self,
        report_id: str,
        run_id: str,
        report_type: str,
        fmt: str,
        content: str,
    ) -> str:
        """Save a copy of a generated report."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            text("""
                INSERT INTO audit_reports (id, run_id, report_type, format, content, created_at)
                VALUES (:id, :rid, :type, :format, :content, :created)
            """),
            {
                "id": report_id,
                "rid": run_id,
                "type": report_type,
                "format": fmt,
                "content": content,
                "created": now,
            },
        )
        await self.db.commit()
        return report_id

    async def save_audit_log(
        self,
        log_id: str,
        project_id: str,
        action: str,
        user_id: Optional[str],
        details: Optional[str],
    ) -> str:
        """Log a validation event."""
        now = datetime.utcnow().isoformat()
        await self.db.execute(
            text("""
                INSERT INTO audit_logs (id, project_id, action, user_id, details, created_at)
                VALUES (:id, :pid, :action, :uid, :details, :created)
            """),
            {
                "id": log_id,
                "pid": project_id,
                "action": action,
                "uid": user_id,
                "details": details,
                "created": now,
            },
        )
        await self.db.commit()
        return log_id

    async def get_validation_history(
        self, project_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch past validation runs for a project."""
        result = await self.db.execute(
            text("""
                SELECT id, solver_run_id, domain, total_errors, total_warnings, is_approved, execution_time_ms, created_at
                FROM validation_runs
                WHERE project_id = :pid
                ORDER BY created_at DESC
                LIMIT :lim
            """),
            {"pid": project_id, "lim": limit},
        )
        rows = result.fetchall()
        runs = []
        for r in rows:
            runs.append({
                "id": r[0],
                "solver_run_id": r[1],
                "domain": r[2],
                "total_errors": r[3],
                "total_warnings": r[4],
                "is_approved": bool(r[5]),
                "execution_time_ms": r[6],
                "created_at": r[7],
            })
        return runs

    async def get_validation_run_issues(self, run_id: str) -> List[ValidationIssueSchema]:
        """Fetch all validation issues associated with a run."""
        result = await self.db.execute(
            text("""
                SELECT severity, category, message, validator_name, engineering_reasoning, recommendation
                FROM validation_issues
                WHERE run_id = :rid
            """),
            {"rid": run_id},
        )
        rows = result.fetchall()
        return [
            ValidationIssueSchema(
                severity=r[0],
                category=r[1],
                message=r[2],
                validator_name=r[3],
                engineering_reasoning=r[4],
                recommendation=r[5],
            )
            for r in rows
        ]

    async def get_validation_run_state(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Reconstruct the validation run state details."""
        result = await self.db.execute(
            text("""
                SELECT id, project_id, solver_run_id, domain, total_errors, total_warnings, is_approved, execution_time_ms, created_at
                FROM validation_runs
                WHERE id = :rid
            """),
            {"rid": run_id},
        )
        row = result.fetchone()
        if not row:
            return None

        issues = await self.get_validation_run_issues(run_id)

        return {
            "id": row[0],
            "project_id": row[1],
            "solver_run_id": row[2],
            "domain": row[3],
            "total_errors": row[4],
            "total_warnings": row[5],
            "is_approved": bool(row[6]),
            "execution_time_ms": row[7],
            "created_at": row[8],
            "issues": [issue.model_dump() for issue in issues],
        }

    async def get_audit_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Fetch audit report contents by ID."""
        result = await self.db.execute(
            text("SELECT id, run_id, report_type, format, content, created_at FROM audit_reports WHERE id = :id"),
            {"id": report_id},
        )
        row = result.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "run_id": row[1],
            "report_type": row[2],
            "format": row[3],
            "content": row[4],
            "created_at": row[5],
        }

    async def get_audit_report_by_run_and_format(
        self, run_id: str, fmt: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch audit report contents by run ID and format."""
        result = await self.db.execute(
            text("""
                SELECT id, run_id, report_type, format, content, created_at
                FROM audit_reports
                WHERE run_id = :rid AND format = :fmt
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"rid": run_id, "fmt": fmt},
        )
        row = result.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "run_id": row[1],
            "report_type": row[2],
            "format": row[3],
            "content": row[4],
            "created_at": row[5],
        }

    async def get_latest_approval(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest approval decision for a project's runs."""
        result = await self.db.execute(
            text("""
                SELECT a.id, a.run_id, a.status, a.engineering_reasoning, a.risk_summary, a.validation_summary, a.created_at
                FROM approval_decisions a
                JOIN validation_runs r ON r.id = a.run_id
                WHERE r.project_id = :pid
                ORDER BY a.created_at DESC
                LIMIT 1
            """),
            {"pid": project_id},
        )
        row = result.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "run_id": row[1],
            "status": row[2],
            "engineering_reasoning": row[3],
            "risk_summary": row[4],
            "validation_summary": row[5],
            "created_at": row[6],
        }
