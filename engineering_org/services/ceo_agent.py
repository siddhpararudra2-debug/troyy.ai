from typing import List, Dict
from verification.schemas.engineering_report import ReportContext, EngineeringReport
from engineering_org.schemas.org_models import (
    EngineeringOrganization, PortfolioProject, ResourceAllocation, 
    Department, ProjectPriority, StrategicDirective
)

class CEOAgent:
    def __init__(self, org: EngineeringOrganization):
        self.org = org
        
    def initiate_project(self, project_name: str, requirements: Dict, priority: str) -> EngineeringReport:
        with ReportContext(
            requirements=["Initiate new engineering project within organizational portfolio"],
            assumptions=["Project aligns with strategic objectives", "Resources are available"],
            constraints=["Priority determines resource allocation", "Must not exceed department budgets"],
            formula_selection="Portfolio Management & Resource Allocation",
            formula_explanation="Evaluates project against strategic directives and allocates resources based on priority.",
            unit_analysis="Resources in hours/USD, priority is categorical."
        ) as ctx:
            domain = requirements.get('domain', 'DRONE')
            dept_map = {
                'DRONE': [Department.MECHANICAL, Department.ELECTRONICS, Department.FIRMWARE,
                          Department.SIMULATION, Department.COMPLIANCE, Department.VERIFICATION],
                'ROBOTICS': [Department.MECHANICAL, Department.ELECTRONICS, Department.FIRMWARE,
                             Department.SIMULATION, Department.COMPLIANCE],
                'AEROSPACE': [Department.MECHANICAL, Department.ELECTRONICS, Department.FIRMWARE,
                              Department.SIMULATION, Department.MANUFACTURING, Department.COMPLIANCE,
                              Department.VERIFICATION]
            }
            departments = dept_map.get(domain, [Department.MECHANICAL, Department.ELECTRONICS])
            
            project = PortfolioProject(
                name=project_name,
                priority=ProjectPriority(priority),
                department_assignments=departments
            )
            
            priority_multiplier = {"CRITICAL": 2.0, "HIGH": 1.5, "MEDIUM": 1.0, "LOW": 0.5}
            mult = priority_multiplier.get(priority, 1.0)
            
            for dept in departments:
                allocation = ResourceAllocation(
                    department=dept,
                    project_id=project.id,
                    compute_hours=100 * mult,
                    engineer_hours=40 * mult,
                    budget_usd=10000 * mult
                )
                project.resources.append(allocation)
                
            self.org.portfolio[project.id] = project
            
            ctx.add_matrix_op("Resource Allocation", "R = Base × PriorityMult", 
                              {"departments": len(departments), "total_compute_h": sum(r.compute_hours for r in project.resources)})
            
            ctx.finalize(
                final_results={
                    "project_id": project.id,
                    "project_name": project_name,
                    "priority": priority,
                    "departments": [d.value for d in departments],
                    "total_resources": {
                        "compute_hours": sum(r.compute_hours for r in project.resources),
                        "engineer_hours": sum(r.engineer_hours for r in project.resources),
                        "budget_usd": sum(r.budget_usd for r in project.resources)
                    }
                },
                interpretation=f"Project '{project_name}' initiated with priority {priority}. {len(departments)} departments engaged."
            )
        return ctx.report
        
    def set_strategic_directive(self, title: str, objectives: List[str], constraints: Dict) -> EngineeringReport:
        directive = StrategicDirective(title=title, objectives=objectives, constraints=constraints)
        self.org.directives.append(directive)
        
        return EngineeringReport(
            requirements=["Set strategic directive for engineering organization"],
            assumptions=["Directive is achievable with current resources"],
            constraints=["Must align with company mission"],
            formula_selection="Strategic Planning",
            formula_explanation="Establishes organizational objectives and constraints.",
            unit_analysis="Objectives are categorical, constraints are referential.",
            final_results={"directive_id": directive.id, "title": title, "objectives": objectives},
            engineering_interpretation=f"Strategic directive '{title}' issued."
        )
