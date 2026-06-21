from simulation_execution.schemas.simulation_models import SimulationJob, SimulationResult
from simulation_execution.schemas.enums import JobStatus
import numpy as np

class ResultProcessor:
    """Post-processes simulation results: computes derived quantities, 
    checks convergence, generates engineering metrics."""
    
    def process(self, result: SimulationResult, job: SimulationJob) -> SimulationResult:
        if result.status != JobStatus.COMPLETED:
            return result
            
        # Compute factor of safety if stress data available
        if result.max_stress_pa and job.materials:
            mat = job.materials[0]
            if mat.yield_strength_pa > 0:
                fos = mat.yield_strength_pa / result.max_stress_pa
                result.solver_output += f"\nFactor of Safety: {fos:.2f}"
                
        # Check convergence
        if result.convergence_data:
            final_residual = result.convergence_data[-1]
            if final_residual > 1e-4:
                result.solver_output += f"\nWARNING: Poor convergence (final residual: {final_residual:.2e})"
                
        # Compute CFD coefficients if lift/drag available
        if result.lift_n is not None and result.drag_n is not None and result.drag_n > 0:
            ld_ratio = result.lift_n / result.drag_n
            result.solver_output += f"\nL/D Ratio: {ld_ratio:.2f}"
            
        return result
