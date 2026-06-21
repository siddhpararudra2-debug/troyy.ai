from typing import Dict
from engineering_org.schemas.org_models import Department, PortfolioProject

class DepartmentManager:
    def __init__(self, department: Department):
        self.department = department
        self.assigned_projects = []
        
    def accept_project(self, project: PortfolioProject, allocation):
        self.assigned_projects.append({
            "project_id": project.id,
            "project_name": project.name,
            "allocation": allocation.dict(),
            "status": "ACCEPTED"
        })
        
    def execute_work(self, project_id: str, task: Dict) -> Dict:
        return {
            "department": self.department.value,
            "project_id": project_id,
            "task": task.get('name'),
            "status": "COMPLETED",
            "artifacts": [f"{self.department.value.lower()}_{task.get('name', 'output')}"]
        }
        
    def get_status(self) -> Dict:
        return {
            "department": self.department.value,
            "active_projects": len(self.assigned_projects),
            "projects": self.assigned_projects
        }
