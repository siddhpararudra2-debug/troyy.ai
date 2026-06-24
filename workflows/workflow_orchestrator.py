"""
Workflow Orchestrator - Orchestrates autonomous engineering workflows.

Capabilities:
- Workflow Plan Generation
- Task Sequencing
- Pipeline Orchestration
"""

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class WorkflowStatus(str, Enum):
    """Status of workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class WorkflowTask:
    """A task within an engineering workflow."""

    def __init__(self, task_id: str, name: str, task_type: str,
                 description: Optional[str] = None):
        self.id = task_id
        self.name = name
        self.task_type = task_type
        self.description = description
        self.status = "pending"
        self.dependencies: List[str] = []
        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self.assigned_to: Optional[str] = None
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "task_type": self.task_type,
            "description": self.description,
            "status": self.status,
            "dependencies": self.dependencies,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "assigned_to": self.assigned_to,
        }


class Workflow:
    """An engineering workflow plan."""

    def __init__(self, workflow_id: str, name: str, description: Optional[str] = None):
        self.id = workflow_id
        self.name = name
        self.description = description
        self.status = WorkflowStatus.PENDING
        self.tasks: Dict[str, WorkflowTask] = {}
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_task(self, name: str, task_type: str, description: Optional[str] = None,
                 dependencies: Optional[List[str]] = None) -> WorkflowTask:
        task_id = str(uuid.uuid4())
        task = WorkflowTask(task_id, name, task_type, description)
        task.dependencies = dependencies or []
        self.tasks[task_id] = task
        return task

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class WorkflowOrchestrator:
    """Orchestrates engineering workflows."""

    ENGINEERING_FLOW = [
        "requirement", "architecture", "design", "simulation",
        "verification", "documentation"
    ]

    def __init__(self):
        self._workflows: Dict[str, Workflow] = {}

    def create_workflow(self, name: str, description: Optional[str] = None) -> Workflow:
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(workflow_id, name, description)
        self._workflows[workflow_id] = workflow
        return workflow

    def generate_engineering_workflow(self, system_name: str) -> Workflow:
        """Generate standard engineering workflow from requirements to documentation."""
        wf = self.create_workflow(
            f"Engineering Workflow: {system_name}",
            f"Complete engineering workflow for {system_name}"
        )

        prev_id = None
        for step in self.ENGINEERING_FLOW:
            task = wf.add_task(
                name=f"{step.title()} Phase",
                task_type=step,
                description=f"Execute {step} phase for {system_name}",
                dependencies=[prev_id] if prev_id else [],
            )
            prev_id = task.id

        return wf

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
        workflow.status = WorkflowStatus.RUNNING
        topo_sorted = self._topological_sort(list(workflow.tasks.values()))
        executed = []
        for task in topo_sorted:
            deps_met = all(
                workflow.tasks[d].status == "completed"
                for d in task.dependencies if d in workflow.tasks
            )
            if deps_met:
                task.status = "completed"
                executed.append(task.name)
        workflow.status = WorkflowStatus.COMPLETED
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "tasks_executed": executed,
        }

    def _topological_sort(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        visited = set()
        result = []
        task_map = {t.id: t for t in tasks}

        def _visit(task_id: str):
            if task_id in visited:
                return
            visited.add(task_id)
            task = task_map.get(task_id)
            if task:
                for dep_id in task.dependencies:
                    _visit(dep_id)
                result.append(task)

        for task in tasks:
            _visit(task.id)

        return result

    def get_all_workflows(self) -> List[Workflow]:
        return list(self._workflows.values())

    def generate_execution_report(self, workflow_id: str) -> Dict[str, Any]:
        wf = self._workflows.get(workflow_id)
        if not wf:
            return {}
        return {
            "workflow": wf.to_dict(),
            "task_count": len(wf.tasks),
            "completed_tasks": sum(1 for t in wf.tasks.values() if t.status == "completed"),
            "pending_tasks": sum(1 for t in wf.tasks.values() if t.status == "pending"),
        }