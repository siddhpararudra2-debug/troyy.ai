from typing import Dict, List
import uuid
from verification.schemas.engineering_report import ReportContext, EngineeringReport
from project_execution.schemas.execution_models import ExecutionTask, ProjectWorkflow

class WorkflowPlanner:
    def plan_project(self, project_name: str, requirements: Dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Generate executable project workflow from requirements"],
            assumptions=["Requirements define complete scope", "Standard engineering process applies"],
            constraints=["No circular dependencies", "Each task has clear inputs/outputs"],
            formula_selection="Domain-Specific Workflow Templates",
            formula_explanation="Selects workflow template based on project domain and populates with requirement-specific parameters.",
            unit_analysis="Tasks are categorical, dependencies are referential."
        ) as ctx:
            domain = requirements.get('domain', 'DRONE')
            
            if domain == "DRONE":
                tasks = [
                    ExecutionTask(name="Requirements_Analysis", domain="SYSTEM", dependencies=[]),
                    ExecutionTask(name="Airframe_Sizing", domain="MECHANICAL", dependencies=["Requirements_Analysis"]),
                    ExecutionTask(name="Propulsion_Selection", domain="MECHANICAL", dependencies=["Airframe_Sizing"]),
                    ExecutionTask(name="Battery_Sizing", domain="ELECTRONICS", dependencies=["Propulsion_Selection"]),
                    ExecutionTask(name="Flight_Controller_Design", domain="ELECTRONICS", dependencies=["Battery_Sizing"]),
                    ExecutionTask(name="Schematic_Generation", domain="ELECTRONICS", dependencies=["Flight_Controller_Design"]),
                    ExecutionTask(name="Firmware_Architecture", domain="FIRMWARE", dependencies=["Flight_Controller_Design"]),
                    ExecutionTask(name="Mission_Simulation", domain="SIMULATION", dependencies=["Battery_Sizing", "Propulsion_Selection"]),
                    ExecutionTask(name="Compliance_Review", domain="COMPLIANCE", dependencies=["Mission_Simulation"]),
                    ExecutionTask(name="Verification_Testing", domain="VERIFICATION", dependencies=["Compliance_Review"]),
                    ExecutionTask(name="Final_Approval", domain="SYSTEM", dependencies=["Verification_Testing", "Schematic_Generation", "Firmware_Architecture"])
                ]
            else:
                tasks = [
                    ExecutionTask(name="Requirements_Analysis", domain="SYSTEM", dependencies=[]),
                    ExecutionTask(name="Design", domain="MECHANICAL", dependencies=["Requirements_Analysis"]),
                    ExecutionTask(name="Simulation", domain="SIMULATION", dependencies=["Design"]),
                    ExecutionTask(name="Review", domain="SYSTEM", dependencies=["Simulation"])
                ]
                
            workflow = ProjectWorkflow(project_id=str(uuid.uuid4()), name=project_name, tasks=tasks)
            
            ctx.add_matrix_op("Workflow Generation", "W = Template(domain) + Requirements", {"tasks": len(tasks)})
            
            ctx.finalize(
                final_results={
                    "project_id": workflow.project_id,
                    "workflow": [t.dict() for t in tasks],
                    "total_tasks": len(tasks),
                    "critical_path": self._compute_critical_path(tasks)
                },
                interpretation=f"Workflow planned with {len(tasks)} tasks. Critical path: {len(self._compute_critical_path(tasks))} tasks."
            )
        return ctx.report
        
    def _compute_critical_path(self, tasks: List[ExecutionTask]) -> List[str]:
        task_map = {t.name: t for t in tasks}
        longest = {}
        
        def dfs(task_name):
            if task_name in longest:
                return longest[task_name]
            task = task_map[task_name]
            if not task.dependencies:
                longest[task_name] = [task_name]
                return longest[task_name]
            max_path = []
            for dep in task.dependencies:
                path = dfs(dep)
                if len(path) > len(max_path):
                    max_path = path
            longest[task_name] = max_path + [task_name]
            return longest[task_name]
            
        for t in tasks:
            dfs(t.name)
        return max(longest.values(), key=len) if longest else []
