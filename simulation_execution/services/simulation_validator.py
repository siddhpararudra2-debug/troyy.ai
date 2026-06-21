from simulation_execution.schemas.simulation_models import SimulationJob
from simulation_execution.schemas.enums import SimulationDomain

class SimulationValidator:
    """Validates simulation jobs before execution."""
    
    def validate(self, job: SimulationJob) -> dict:
        errors = []
        warnings = []
        
        # Check materials
        if not job.materials and job.domain in [SimulationDomain.STRUCTURAL, SimulationDomain.THERMAL]:
            errors.append("Structural/thermal simulations require at least one material")
            
        for mat in job.materials:
            if mat.youngs_modulus_pa <= 0:
                errors.append(f"Material {mat.name}: Young's modulus must be positive")
            if mat.density_kg_m3 <= 0:
                errors.append(f"Material {mat.name}: Density must be positive")
            if not (0 <= mat.poisson_ratio < 0.5):
                errors.append(f"Material {mat.name}: Poisson's ratio must be in [0, 0.5)")
                
        # Check boundary conditions
        if not job.boundary_conditions:
            warnings.append("No boundary conditions specified - solver defaults will apply")
            
        # Check mesh config
        if job.mesh_config:
            if job.mesh_config.element_size_m <= 0:
                errors.append("Element size must be positive")
            if job.mesh_config.max_aspect_ratio < 1:
                errors.append("Max aspect ratio must be >= 1")
                
        # Check solver config
        if job.solver_config.cores < 1:
            errors.append("Must allocate at least 1 core")
        if job.solver_config.memory_gb < 0.5:
            errors.append("Must allocate at least 0.5 GB memory")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
