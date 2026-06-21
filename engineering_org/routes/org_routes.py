from fastapi import APIRouter
from engineering_org.schemas.org_models import Department
from engineering_org.services.engineering_operations import EngineeringOperations

router = APIRouter(prefix="/org", tags=["Autonomous Engineering Organization"])
ops = EngineeringOperations()

@router.post("/project")
async def create_project(project_name: str, requirements: dict, priority: str = "MEDIUM"):
    return await ops.execute_full_project(project_name, requirements, priority)

@router.post("/directive")
async def set_directive(title: str, objectives: list, constraints: dict = {}):
    return ops.ceo.set_strategic_directive(title, objectives, constraints)

@router.get("/portfolio")
async def get_portfolio():
    return {pid: p.dict() for pid, p in ops.org.portfolio.items()}

@router.get("/department/{dept}")
async def get_department_status(dept: str):
    try:
        d = Department(dept)
        return ops.departments[d].get_status()
    except ValueError:
        return {"status": "UNKNOWN_DEPARTMENT"}
