from typing import List, Dict
from engineering_org.schemas.org_models import EngineeringOrganization, Department, PortfolioProject
from engineering_org.services.department_manager import DepartmentManager

class ChiefEngineerAgent:
    def __init__(self, org: EngineeringOrganization, departments: Dict[Department, DepartmentManager]):
        self.org = org
        self.departments = departments
        
    def govern_project(self, project_id: str) -> Dict:
        project = self.org.portfolio.get(project_id)
        if not project:
            return {"status": "NOT_FOUND"}
            
        dept_statuses = {}
        for dept in project.department_assignments:
            manager = self.departments.get(dept)
            if manager:
                dept_statuses[dept.value] = manager.get_status()
                
        return {
            "project_id": project_id,
            "project_name": project.name,
            "governance_status": "ACTIVE",
            "department_statuses": dept_statuses,
            "technical_risks": self._assess_technical_risks(project)
        }
        
    def _assess_technical_risks(self, project) -> List[str]:
        risks = []
        if project.priority.value == "CRITICAL":
            risks.append("High-priority project requires accelerated timeline")
        if len(project.department_assignments) > 5:
            risks.append("Cross-departmental coordination complexity")
        return risks
