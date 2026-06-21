from typing import Dict
from engineering_org.schemas.org_models import EngineeringOrganization, Department
from engineering_org.services.ceo_agent import CEOAgent
from engineering_org.services.department_manager import DepartmentManager
from engineering_org.services.chief_engineer_agent import ChiefEngineerAgent

class EngineeringOperations:
    def __init__(self):
        self.org = EngineeringOrganization()
        self.ceo = CEOAgent(self.org)
        self.departments = {dept: DepartmentManager(dept) for dept in Department}
        self.chief_engineer = ChiefEngineerAgent(self.org, self.departments)
        
    async def execute_full_project(self, project_name: str, requirements: Dict, priority: str = "MEDIUM") -> Dict:
        init_report = self.ceo.initiate_project(project_name, requirements, priority)
        project_id = init_report.final_results['project_id']
        project = self.org.portfolio[project_id]
        
        for allocation in project.resources:
            manager = self.departments.get(allocation.department)
            if manager:
                manager.accept_project(project, allocation)
                
        governance = self.chief_engineer.govern_project(project_id)
        
        execution_results = {}
        for dept in project.department_assignments:
            manager = self.departments[dept]
            execution_results[dept.value] = manager.execute_work(project_id, {"name": "design"})
            
        return {
            "project_id": project_id,
            "initiation": init_report.final_results,
            "governance": governance,
            "execution": execution_results,
            "status": "EXECUTED"
        }
