"""Workflow Templates - Pre-built templates for Sprint 17."""
from typing import Dict, Any


class WorkflowTemplates:
    """Pre-built workflow templates."""

    @staticmethod
    def mechanical_design_release() -> Dict[str, Any]:
        """Mechanical design release workflow template."""
        return {
            "name": "Mechanical Design Release",
            "initial_state": "design_draft",
            "states": ["design_draft", "design_review", "simulation", "approval", "release"],
            "transitions": [
                {"from": "design_draft", "to": "design_review"},
                {"from": "design_review", "to": "simulation"},
                {"from": "design_review", "to": "design_draft"},
                {"from": "simulation", "to": "approval"},
                {"from": "approval", "to": "release"}
            ]
        }
