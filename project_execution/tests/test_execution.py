import pytest
from project_execution.services.workflow_planner import WorkflowPlanner
from project_execution.services.dependency_manager import DependencyManager
from project_execution.services.project_executor import ProjectExecutor
from project_execution.schemas.execution_models import ExecutionTask

def test_workflow_planning():
    planner = WorkflowPlanner()
    report = planner.plan_project("Test Drone", {"domain": "DRONE", "payload_kg": 5})
    assert report.final_results['total_tasks'] > 0
    assert len(report.final_results['critical_path']) > 0

def test_cycle_detection():
    dm = DependencyManager()
    tasks = [
        ExecutionTask(name="A", domain="SYSTEM", dependencies=["B"]),
        ExecutionTask(name="B", domain="SYSTEM", dependencies=["C"]),
        ExecutionTask(name="C", domain="SYSTEM", dependencies=["A"])
    ]
    cycles = dm.detect_cycles(tasks)
    assert len(cycles) > 0

def test_no_cycle():
    dm = DependencyManager()
    tasks = [
        ExecutionTask(name="A", domain="SYSTEM", dependencies=[]),
        ExecutionTask(name="B", domain="SYSTEM", dependencies=["A"]),
        ExecutionTask(name="C", domain="SYSTEM", dependencies=["B"])
    ]
    cycles = dm.detect_cycles(tasks)
    assert len(cycles) == 0

@pytest.mark.asyncio
async def test_project_execution():
    executor = ProjectExecutor()
    result = await executor.execute_project("Test", {"domain": "DRONE"})
    assert result["status"] in ["APPROVED", "REJECTED"]
    assert result["tasks_completed"] > 0
