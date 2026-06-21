from fastapi import APIRouter
from project_execution.services.project_executor import ProjectExecutor

router = APIRouter(prefix="/execution", tags=["Autonomous Project Execution"])
executor = ProjectExecutor()

@router.post("/project")
async def execute_project(project_name: str, requirements: dict):
    return await executor.execute_project(project_name, requirements)

@router.get("/project/{project_id}")
async def get_project(project_id: str):
    workflow = executor.workflows.get(project_id)
    if not workflow:
        return {"status": "NOT_FOUND"}
    return {"project_id": project_id, "state": workflow.state.value, "tasks": [t.dict() for t in workflow.tasks]}
