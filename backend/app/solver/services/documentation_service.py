"""
Troy — Documentation Service
Generates a comprehensive engineering report from the SolverState and persists
it using the Document Generation Service.
"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.schemas import DocumentGenerateRequest
from app.documents.service import generate_document
from app.solver.models.domain_models import SolverState

logger = logging.getLogger("solver.services.documentation")


class DocumentationService:
    """Formats solver session results into a professional markdown document."""

    async def generate_report(self, state: SolverState, db: AsyncSession) -> str:
        """
        Build a markdown report, call generate_document, and return the document ID.
        """
        logger.info(f"Generating engineering report for solver session {state.session_id}")

        # ── Formulate markdown content ───────────────────────────
        md = f"# Engineering Solver Report\n\n"
        md += f"**Session ID:** `{state.session_id}`  \n"
        md += f"**Project ID:** `{state.project_id}`  \n"
        md += f"**Domain:** {state.domain.capitalize()}  \n"
        md += f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  \n\n"

        md += f"## User Query\n\n> {state.user_query}\n\n"

        # 1. Requirements
        md += "## 1. Extracted Requirements\n\n"
        req = state.requirements
        md += f"- **Project Type:** {req.project_type}  \n"
        md += f"- **Mission Type:** {req.mission_type}  \n"
        if req.payload:
            md += f"- **Payload:** {req.payload}  \n"
        if req.flight_time:
            md += f"- **Flight/Endurance Time:** {req.flight_time}  \n"
        md += f"- **Environment:** {req.environment}  \n"
        if req.safety_factor:
            md += f"- **Safety Factor:** {req.safety_factor}  \n"
        
        if req.missing_requirements:
            md += "\n**Missing / Unspecified Parameters:**\n"
            for mr in req.missing_requirements:
                md += f"- {mr}\n"
        md += "\n"

        # 2. Assumptions
        md += "## 2. Engineering Assumptions\n\n"
        if state.assumptions:
            md += "| Parameter | Assumption | Reasoning | Confidence | Override |\n"
            md += "|---|---|---|---|---|\n"
            for a in state.assumptions:
                override = a.user_override or "None"
                md += f"| {a.missing_information} | {a.assumption} | {a.reasoning} | {a.confidence_score} | {override} |\n"
        else:
            md += "*No assumptions generated.*\n"
        md += "\n"

        # 3. Constraints
        md += "## 3. Engineering Constraints\n\n"
        if state.constraints:
            md += "| Category | Limit Bound | Source / Rationale |\n"
            md += "|---|---|---|\n"
            for c in state.constraints:
                md += f"| {c.category} | {c.limit} | {c.source} |\n"
        else:
            md += "*No constraints defined.*\n"
        md += "\n"

        # 4. Variables
        md += "## 4. Variable Trace\n\n"
        vars_data = state.variables
        
        md += "### Known / Input Variables\n\n"
        if vars_data.known:
            md += "| Name | Value | Unit | Description |\n"
            md += "|---|---|---|---|\n"
            for name, data in vars_data.known.items():
                md += f"| `{name}` | {data.get('value')} | {data.get('unit')} | {data.get('description', '')} |\n"
        else:
            md += "*No known variables.*\n"
        md += "\n"

        md += "### Derived Variables\n\n"
        if vars_data.derived:
            md += "| Name | Value | Unit | Description |\n"
            md += "|---|---|---|---|\n"
            for name, data in vars_data.derived.items():
                md += f"| `{name}` | {data.get('value')} | {data.get('unit')} | {data.get('description', '')} |\n"
        else:
            md += "*No derived variables.*\n"
        md += "\n"

        # 5. Calculations
        md += "## 5. Calculation Trace\n\n"
        if state.calculation_results:
            md += "The following calculations were executed in the Calculation Core:\n\n"
            for k, val in state.calculation_results.items():
                md += f"- **`{k}`**: {val}\n"
        else:
            md += "*No calculations executed.*\n"
        md += "\n"

        # 6. Interpretations
        md += "## 6. Engineering Interpretation\n\n"
        if state.interpretation.interpretation:
            md += state.interpretation.interpretation
        else:
            md += "*No interpretation provided.*"
        md += "\n\n"

        # 7. Recommendations
        md += "## 7. Actionable Recommendations\n\n"
        recs = state.recommendations
        if recs.recommendations:
            for i, r in enumerate(recs.recommendations):
                md += f"### {i+1}. {r.recommendation}\n\n"
                md += f"**Reasoning:** {r.reasoning}  \n"
                if r.expected_benefits:
                    md += f"**Expected Benefits:** {r.expected_benefits}  \n"
                if r.potential_risks:
                    md += f"**Potential Risks:** {r.potential_risks}  \n"
                md += "\n"
        else:
            md += "*No recommendations generated.*\n"

        md += "\n---\n*Report generated automatically by Troy Engineering Solver & Reasoning Engine.*\n"

        # ── Persist document using standard generate_document ──────
        request_data = DocumentGenerateRequest(
            project_id=state.project_id,
            calculation_id=None,
            doc_type="custom",
            title=f"Solver Session Report: {state.session_id}",
            format="markdown",
        )

        try:
            # Inject our generated content directly by mocking/overriding or updating
            # Wait, app/documents/service.py uses generate_document(data, db).
            # If doc_type is "custom", it defaults to content = "# Custom Document\\n\\n...".
            # To set our custom content, we can run raw SQL to insert or we can temporarily
            # edit documents service to accept content in the request, or we can update the database
            # record after creation.
            # Let's call generate_document first, then update the document content in the database using raw SQL!
            # That is extremely clean and avoids changing the documents schema.
            doc_res = await generate_document(request_data, db=db)
            
            # Now update the content with our real formatted markdown
            await db.execute(
                text("UPDATE documents SET content = :content WHERE id = :id"),
                {"content": md, "id": doc_res.id}
            )
            await db.commit()
            
            logger.info(f"Successfully saved and updated solver report document: {doc_res.id}")
            return doc_res.id

        except Exception as e:
            logger.error(f"Failed to generate and persist solver document: {e}")
            raise e
from sqlalchemy import text
