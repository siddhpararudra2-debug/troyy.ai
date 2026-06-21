from typing import Dict, List, Optional
from simulation_execution.schemas.simulation_models import SimulationJob, SimulationResult

class SimulationRepository:
    """In-memory repository. In production, backed by PostgreSQL + MinIO."""
    
    def __init__(self):
        self.jobs: Dict[str, SimulationJob] = {}
        self.results: Dict[str, SimulationResult] = {}
        
    def save_job(self, job: SimulationJob):
        self.jobs[job.id] = job
        
    def get_job(self, job_id: str) -> Optional[SimulationJob]:
        return self.jobs.get(job_id)
        
    def save_result(self, result: SimulationResult):
        self.results[result.job_id] = result
        
    def get_result(self, job_id: str) -> Optional[SimulationResult]:
        return self.results.get(job_id)
        
    def list_jobs(self, project_id: Optional[str] = None) -> List[SimulationJob]:
        if project_id:
            return [j for j in self.jobs.values() if j.project_id == project_id]
        return list(self.jobs.values())
