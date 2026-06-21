import asyncio
from typing import Dict
from datetime import datetime
from project_execution.schemas.execution_models import ExecutionTask, ProjectWorkflow, ProjectState, TaskState
from project_execution.services.workflow_planner import WorkflowPlanner
from project_execution.services.dependency_manager import DependencyManager

class ProjectExecutor:
    def __init__(self):
        self.planner = WorkflowPlanner()
        self.dep_manager = DependencyManager()
        self.workflows = {}
        
    async def execute_project(self, project_name: str, requirements: Dict) -> Dict:
        plan_report = self.planner.plan_project(project_name, requirements)
        workflow = ProjectWorkflow(
            project_id=plan_report.final_results['project_id'],
            name=project_name,
            state=ProjectState.EXECUTING,
            tasks=[ExecutionTask(**t) for t in plan_report.final_results['workflow']]
        )
        
        cycles = self.dep_manager.detect_cycles(workflow.tasks)
        if cycles:
            return {"status": "FAILED", "reason": f"Circular dependencies detected: {cycles}"}
            
        self.workflows[workflow.project_id] = workflow
        
        max_total_iterations = 100
        iteration = 0
        
        while iteration < max_total_iterations:
            ready_tasks = self.dep_manager.get_ready_tasks(workflow.tasks)
            
            if not ready_tasks:
                if all(t.state == TaskState.COMPLETED for t in workflow.tasks):
                    workflow.state = ProjectState.APPROVED
                    workflow.completed_at = datetime.utcnow()
                    break
                if any(t.state in [TaskState.FAILED, TaskState.BLOCKED] for t in workflow.tasks):
                    workflow.state = ProjectState.REJECTED
                    break
                await asyncio.sleep(0.01)
                iteration += 1
                continue
                
            await asyncio.gather(*[self._execute_task(t, workflow) for t in ready_tasks])
            iteration += 1
            
        return {
            "project_id": workflow.project_id,
            "status": workflow.state.value,
            "tasks_completed": sum(1 for t in workflow.tasks if t.state == TaskState.COMPLETED),
            "total_tasks": len(workflow.tasks),
            "iterations": iteration,
            "task_details": [t.dict() for t in workflow.tasks]
        }
        
    async def _execute_task(self, task: ExecutionTask, workflow: ProjectWorkflow):
        task.state = TaskState.RUNNING
        task.started_at = datetime.utcnow()
        task.iteration += 1
        
        await asyncio.sleep(0.01)
        
        if task.name == "Mission_Simulation" and task.iteration < 2:
            task.state = TaskState.FAILED
            task.outputs = {"status": "FAIL", "reason": "Endurance below target"}
        else:
            task.state = TaskState.COMPLETED
            task.outputs = {"status": "PASS", "artifacts": [f"{task.name}_v{task.iteration}"]}
            task.completed_at = datetime.utcnow()
