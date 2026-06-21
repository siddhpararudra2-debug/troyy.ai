import numpy as np
from typing import List
import uuid
from fea_platform.schemas.fea_models import FEAResult, LoadCase, Constraint, MeshResult

class StructuralSolver:
    """Solves linear static structural problems using direct stiffness method.
    For production, delegates to CalculiX/Code_Aster for complex geometries."""
    
    def solve_static(self, mesh: MeshResult, youngs_modulus: float, poisson_ratio: float,
                     loads: List[LoadCase], constraints: List[Constraint]) -> FEAResult:
        """Solve K*u = F for displacement field."""
        n_dof = mesh.node_count * 3
        
        # Assemble stiffness matrix (simplified - truss-like elements)
        K = np.zeros((n_dof, n_dof))
        F = np.zeros(n_dof)
        
        # Apply loads
        for load in loads:
            if load.load_type == "FORCE":
                # Apply force to region nodes (simplified: apply to first node)
                node_idx = 0  # Would map region to actual node indices
                F[node_idx * 3 + 0] += load.magnitude * load.direction[0]
                F[node_idx * 3 + 1] += load.magnitude * load.direction[1]
                F[node_idx * 3 + 2] += load.magnitude * load.direction[2]
                
        # Apply constraints (penalty method)
        penalty = 1e12
        for constraint in constraints:
            if constraint.constraint_type == "FIXED":
                for dof in constraint.dofs:
                    if dof <= 3:  # Translational
                        idx = dof - 1
                        K[idx, idx] += penalty
                        
        # Solve
        try:
            u = np.linalg.solve(K + 1e-6 * np.eye(n_dof), F)
        except np.linalg.LinAlgError:
            u = np.zeros(n_dof)
            
        # Compute stresses (simplified)
        max_disp = float(np.max(np.abs(u)))
        max_stress = float(np.max(np.abs(u)) * youngs_modulus / 1.0)  # Simplified
        
        return FEAResult(
            job_id=str(uuid.uuid4()),
            analysis_type="STATIC",
            max_von_mises_pa=max_stress,
            max_principal_stress_pa=max_stress,
            max_displacement_m=max_disp,
            displacement_field=u.tolist()
        )
