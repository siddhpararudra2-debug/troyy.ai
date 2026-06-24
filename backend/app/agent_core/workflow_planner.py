"""
Workflow Planner for Engineering OS
Handles high-level workflow planning and task decomposition.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class WorkflowPlanner:
    """
    Plans engineering workflows and decomposes high-level requirements into tasks.
    """

    # Standard engineering workflow steps
    DEFAULT_WORKFLOW_STEPS = [
        {"name": "requirements_analysis", "agent_type": "mechanical"},
        {"name": "architectural_design", "agent_type": "mechanical"},
        {"name": "cad_modeling", "agent_type": "mechanical"},
        {"name": "simulation_planning", "agent_type": "simulation"},
        {"name": "fea_analysis", "agent_type": "simulation"},
        {"name": "cfd_analysis", "agent_type": "simulation"},
        {"name": "design_optimization", "agent_type": "simulation"},
        {"name": "verification", "agent_type": "documentation"},
        {"name": "documentation", "agent_type": "documentation"},
        {"name": "bom_generation", "agent_type": "mechanical"},
    ]

    def __init__(self):
        self._workflows: Dict[str, Dict] = {}

    async def plan_workflow(
        self,
        requirements: str,
        mission_id: str,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a workflow plan based on requirements.
        """
        workflow_id = str(uuid.uuid4())
        logger.info(f"Creating workflow plan {workflow_id} for mission {mission_id}")

        # Determine domain (aerospace/drone/robotics etc.)
        domain = self._detect_domain(requirements)

        # Create workflow steps
        steps = self._generate_workflow_steps(domain, requirements)

        workflow_plan = {
            "workflow_id": workflow_id,
            "mission_id": mission_id,
            "project_id": project_id,
            "requirements": requirements,
            "domain": domain,
            "steps": steps,
            "status": "planned",
            "started_at": datetime.utcnow().isoformat(),
        }

        self._workflows[workflow_id] = workflow_plan
        return workflow_plan

    async def decompose_tasks(self, workflow_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Decompose a workflow plan into executable tasks.
        """
        tasks = []
        steps = workflow_plan.get("steps", self.DEFAULT_WORKFLOW_STEPS)
        for i, step in enumerate(steps):
            task_id = str(uuid.uuid4())
            tasks.append({
                "task_id": task_id,
                "task_type": step.get("name", step.get("task_type", "unknown")),
                "agent_type": step.get("agent_type", "mechanical"),
                "priority": 10 - i,  # Earlier steps first
                "dependencies": [t["task_id"] for t in tasks[:i]],
                "requirements": workflow_plan.get("requirements", ""),
                "project_id": workflow_plan.get("project_id"),
            })
        logger.info(f"Decomposed workflow into {len(tasks)} tasks")
        return tasks

    def _detect_domain(self, requirements: str) -> str:
        """
        Detect engineering domain from requirements.
        """
        req_lower = requirements.lower()
        if "drone" in req_lower or "uav" in req_lower:
            return "drone"
        elif "aerospace" in req_lower or "aircraft" in req_lower or "wing" in req_lower:
            return "aerospace"
        elif "robot" in req_lower or "arm" in req_lower:
            return "robotics"
        elif "electronics" in req_lower or "circuit" in req_lower or "pcb" in req_lower:
            return "electronics"
        else:
            return "mechanical"

    def _generate_workflow_steps(self, domain: str, requirements: str) -> List[Dict[str, str]]:
        """
        Generate workflow steps based on domain and requirements.
        """
        steps = []
        # Common first step
        steps.append({"name": "requirements_analysis", "agent_type": "mechanical"})

        if domain in ["drone", "aerospace"]:
            steps.extend([
                {"name": "aerodynamic_analysis", "agent_type": "simulation"},
                {"name": "structural_design", "agent_type": "mechanical"},
                {"name": "cad_modeling", "agent_type": "mechanical"},
                {"name": "fea_stress_analysis", "agent_type": "simulation"},
                {"name": "cfd_aerodynamic_simulation", "agent_type": "simulation"},
                {"name": "propulsion_design", "agent_type": "mechanical"},
                {"name": "electronics_design", "agent_type": "electronics"},
                {"name": "pcb_layout", "agent_type": "pcb"},
                {"name": "firmware_design", "agent_type": "firmware"},
                {"name": "bom_generation", "agent_type": "mechanical"},
                {"name": "documentation", "agent_type": "documentation"},
            ])
        elif domain == "robotics":
            steps.extend([
                {"name": "kinematic_analysis", "agent_type": "simulation"},
                {"name": "structural_design", "agent_type": "mechanical"},
                {"name": "cad_modeling", "agent_type": "mechanical"},
                {"name": "electronics_design", "agent_type": "electronics"},
                {"name": "pcb_layout", "agent_type": "pcb"},
                {"name": "firmware_design", "agent_type": "firmware"},
                {"name": "bom_generation", "agent_type": "mechanical"},
                {"name": "documentation", "agent_type": "documentation"},
            ])
        else:
            # Default mechanical
            steps.extend([
                {"name": "structural_design", "agent_type": "mechanical"},
                {"name": "cad_modeling", "agent_type": "mechanical"},
                {"name": "fea_analysis", "agent_type": "simulation"},
                {"name": "bom_generation", "agent_type": "mechanical"},
                {"name": "documentation", "agent_type": "documentation"},
            ])
        return steps
