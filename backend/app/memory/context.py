"""
Troy — Context Retrieval Engine
Gathers project data (calculations, reports, assumptions, decisions, chat history)
into a unified prompt context for the AI Copilot.
"""

from __future__ import annotations

import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger

logger = get_logger("context_engine")


class ContextEngine:
    """Retrieves and formats project memory for the AI."""

    @staticmethod
    async def build_context(project_id: str, db: AsyncSession, session_id: str = None) -> str:
        """
        Builds a comprehensive system prompt string for the AI, 
        incorporating all known project artifacts.
        """
        # 1. Project Info
        proj_res = await db.execute(
            text("SELECT name, description, domain FROM projects WHERE id = :id"),
            {"id": project_id}
        )
        proj = proj_res.fetchone()
        if not proj:
            return "Context unavailable (Project not found)."
        
        name, desc, domain = proj
        context = f"You are Troy, an expert Engineering Copilot.\n"
        context += f"Current Project: {name} (Domain: {domain})\n"
        context += f"Description: {desc}\n\n"

        # 2. Design Decisions & Assumptions
        mem_res = await db.execute(
            text("""
                SELECT entry_type, content, tags_json 
                FROM memory_entries 
                WHERE project_id = :pid 
                ORDER BY created_at ASC
            """),
            {"pid": project_id}
        )
        memories = mem_res.fetchall()
        if memories:
            context += "### Active Project Memory (Constraints & Decisions)\n"
            for m_type, content, tags_json in memories:
                tags = json.loads(tags_json) if tags_json else []
                tags_str = f" [{','.join(tags)}]" if tags else ""
                context += f"- [{m_type.upper()}]{tags_str} {content}\n"
            context += "\n"

        # 3. Recent Calculations
        calc_res = await db.execute(
            text("""
                SELECT title, formula_id, inputs_json, outputs_json 
                FROM calculations 
                WHERE project_id = :pid AND status = 'completed'
                ORDER BY created_at DESC LIMIT 5
            """),
            {"pid": project_id}
        )
        calcs = calc_res.fetchall()
        if calcs:
            context += "### Recent Calculations\n"
            for title, formula_id, inputs_json, outputs_json in calcs:
                inputs = json.loads(inputs_json) if inputs_json else {}
                outputs = json.loads(outputs_json) if outputs_json else {}
                in_str = ", ".join([f"{k}={v}" for k, v in inputs.items()])
                out_str = ", ".join([f"{k}={v}" for k, v in outputs.items()])
                context += f"- {title} ({formula_id}):\n  Inputs: {in_str}\n  Outputs: {out_str}\n"
            context += "\n"

        # 4. Reports/Documents Summary
        doc_res = await db.execute(
            text("""
                SELECT title, doc_type 
                FROM documents 
                WHERE project_id = :pid 
                ORDER BY created_at DESC LIMIT 5
            """),
            {"pid": project_id}
        )
        docs = doc_res.fetchall()
        if docs:
            context += "### Generated Reports\n"
            for title, doc_type in docs:
                context += f"- {title} ({doc_type})\n"
            context += "\n"
        
        # 5. Instructions
        context += "### Instructions\n"
        context += "Use the above project memory to answer the user's queries accurately.\n"
        context += "If suggesting new design constraints, clearly label them so they can be saved to memory.\n"

        return context
