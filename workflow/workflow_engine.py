"""Workflow Engine - Workflow Management for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class WorkflowEngine:
    """Core workflow execution engine."""

    def __init__(self):
        self.workflows: Dict[str, Dict[str, Any]] = {}

    def create_workflow(
        self,
        project_id: str,
        name: str,
        definition: Dict[str, Any],
        workflow_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new workflow."""
        workflow_id = str(uuid.uuid4())
        workflow = {
            "id": workflow_id,
            "project_id": project_id,
            "name": name,
            "workflow_type": workflow_type or "custom",
            "definition": definition,
            "current_state": definition.get("initial_state", "draft"),
            "status": "active",
            "history": [],
            "created_at": datetime.utcnow().isoformat()
        }
        self.workflows[workflow_id] = workflow
        return workflow

    def advance_workflow(
        self,
        workflow_id: str,
        next_state: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Advance a workflow to the next state."""
        if workflow_id not in self.workflows:
            return None

        workflow = self.workflows[workflow_id]
        workflow["history"].append({
            "from_state": workflow["current_state"],
            "to_state": next_state,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        })
        workflow["current_state"] = next_state
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)
