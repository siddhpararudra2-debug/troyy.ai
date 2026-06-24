"""
Engineering Pipeline - Defines standard engineering pipelines and process flows.

Capabilities:
- Pipeline Definition
- Standard Engineering Processes
- Phase Gates
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from workflows.workflow_orchestrator import Workflow, WorkflowTask, WorkflowOrchestrator


class PhaseGate:
    """A phase gate in the engineering pipeline."""

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.criteria: List[str] = []
        self.status = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description,
                "criteria": self.criteria, "status": self.status}


class EngineeringPipeline:
    """Defines standard engineering pipelines."""

    STANDARD_PHASES = [
        "Mission Definition", "Requirements Engineering", "System Architecture",
        "Trade Studies", "CAD / PCB Design", "Simulation",
        "Verification", "Risk Analysis", "Manufacturing Readiness"
    ]

    def __init__(self):
        self._pipelines: Dict[str, Dict[str, Any]] = {}

    def create_pipeline(self, name: str, description: Optional[str] = None) -> str:
        pipeline_id = str(uuid.uuid4())
        self._pipelines[pipeline_id] = {
            "id": pipeline_id,
            "name": name,
            "description": description,
            "phases": [],
            "gates": [],
        }
        return pipeline_id

    def generate_standard_pipeline(self, system_name: str) -> Dict[str, Any]:
        pid = str(uuid.uuid4())
        phases = []
        for i, phase in enumerate(self.STANDARD_PHASES):
            phases.append({
                "order": i + 1,
                "name": phase,
                "status": "pending",
                "gate": PhaseGate(f"{phase} Gate", f"Gate review for {phase}").to_dict(),
            })
        pipeline = {
            "id": pid,
            "name": f"Engineering Pipeline: {system_name}",
            "phases": phases,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._pipelines[pid] = pipeline
        return pipeline

    def get_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        return self._pipelines.get(pipeline_id)

    def get_all_pipelines(self) -> List[Dict[str, Any]]:
        return list(self._pipelines.values())