from fastapi import APIRouter, HTTPException
from simulation_execution.schemas.simulation_models import SimulationJob
from simulation_execution.services.simulation_orchestrator import SimulationOrchestrator
from simulation_execution.services.simulation_repository import SimulationRepository
from simulation_execution.services.solver_manager import SolverManager

router = APIRouter(prefix="/simulation-execution", tags=["Multi-Physics Simulation Execution"])

orchestrator = SimulationOrchestrator()
repository = SimulationRepository()
solver_manager = SolverManager()

@router.post("/submit")
async def submit_job(job: SimulationJob):
    job_id = await orchestrator.submit_job(job)
    repository.save_job(job)
    return {"job_id": job_id, "status": "QUEUED"}

@router.post("/execute/{job_id}")
async def execute_job(job_id: str):
    try:
        result = await orchestrator.execute_job(job_id)
        repository.save_result(result)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{job_id}")
async def get_result(job_id: str):
    result = repository.get_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result.model_dump()

@router.get("/jobs")
async def list_jobs(project_id: str = None):
    return [j.model_dump() for j in repository.list_jobs(project_id)]

@router.get("/solvers")
async def list_solvers():
    return solver_manager.list_solvers()
