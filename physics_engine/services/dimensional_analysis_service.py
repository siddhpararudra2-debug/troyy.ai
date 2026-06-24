"""
Dimensional Analysis Service — implements the Buckingham Pi theorem.
Given a set of physical variables, derives the dimensionless groups that
govern the system behavior. This is how engineers discover scaling laws.
"""
import numpy as np
from typing import List, Dict, Tuple
from physics_engine.schemas.physics_models import (
    DimensionalAnalysisResult, DimensionlessGroup
)
from physics_engine.services.units_engine import UnitsEngine

class DimensionalAnalysisService:
    """Applies Buckingham Pi theorem to derive dimensionless groups."""
    
    # Fundamental dimensions and their symbols
    FUNDAMENTAL_DIMS = {
        'length': 'L',
        'mass': 'M',
        'time': 'T',
        'temperature': 'Θ',
        'electric_current': 'I',
        'amount_of_substance': 'N',
        'luminous_intensity': 'J'
    }
    
    def __init__(self, units_engine: UnitsEngine):
        self.units = units_engine
        
    def analyze(self, variables: Dict[str, str]) -> DimensionalAnalysisResult:
        """
        Perform Buckingham Pi analysis.
        variables: dict of {variable_name: unit_string}
        Returns: dimensionless groups and functional relationship.
        """
        # Step 1: Get dimensions of each variable
        var_dims = {}
        for name, unit in variables.items():
            var_dims[name] = self.units.get_dimension(unit)
            
        # Step 2: Identify fundamental dimensions present
        all_dims = set()
        for dims in var_dims.values():
            all_dims.update(dims.keys())
        fundamental_dims = sorted(all_dims)
        
        n_vars = len(variables)
        n_dims = len(fundamental_dims)
        
        if n_vars <= n_dims:
            raise ValueError(f"Need more variables ({n_vars}) than fundamental dimensions ({n_dims})")
            
        # Step 3: Build dimensional matrix
        var_names = list(variables.keys())
        dim_matrix = np.zeros((n_dims, n_vars))
        for j, var in enumerate(var_names):
            for i, dim in enumerate(fundamental_dims):
                dim_matrix[i, j] = var_dims[var].get(dim, 0)
                
        # Step 4: Choose repeating variables (first n_dims variables that form a non-singular matrix)
        repeating_vars, repeating_indices = self._choose_repeating_vars(dim_matrix, n_dims, var_names)
        
        # Step 5: Compute Pi groups via null space
        pi_groups = []
        non_repeating = [i for i in range(n_vars) if i not in repeating_indices]
        
        for idx, non_rep_idx in enumerate(non_repeating):
            # Solve for exponents such that the group is dimensionless
            # D_repeating * k = -d_non_repeating
            D_rep = dim_matrix[:, repeating_indices]
            d_non = dim_matrix[:, non_rep_idx]
            
            try:
                exponents = np.linalg.solve(D_rep, -d_non)
            except np.linalg.LinAlgError:
                # Singular — use pseudo-inverse
                exponents = np.linalg.lstsq(D_rep, -d_non, rcond=None)[0]
                
            # Build the Pi group
            pi_vars = {}
            for i, rep_idx in enumerate(repeating_indices):
                exp = round(exponents[i], 4)
                if abs(exp) > 1e-6:
                    pi_vars[var_names[rep_idx]] = f"^{exp}" if exp != 1 else ""
            pi_vars[var_names[non_rep_idx]] = ""
            
            # Format the group
            formula_parts = []
            for var, exp in pi_vars.items():
                if exp:
                    formula_parts.append(f"{var}{exp}")
                else:
                    formula_parts.append(var)
            formula = " * ".join(formula_parts)
            
            # Assign a conventional name if recognizable
            pi_name = self._recognize_pi_group(pi_vars, var_names)
            
            pi_groups.append(DimensionlessGroup(
                name=pi_name,
                symbol=f"π_{idx + 1}",
                formula=formula,
                physical_meaning=self._describe_meaning(pi_name, pi_vars),
                variables={k: variables[k] for k in pi_vars.keys()}
            ))
            
        # Step 6: Express functional relationship
        if len(pi_groups) == 1:
            func_rel = f"{pi_groups[0].symbol} = constant"
        elif len(pi_groups) == 2:
            func_rel = f"{pi_groups[0].symbol} = f({pi_groups[1].symbol})"
        else:
            symbols = [g.symbol for g in pi_groups[1:]]
            func_rel = f"{pi_groups[0].symbol} = f({', '.join(symbols)})"
            
        return DimensionalAnalysisResult(
            problem_description=f"Dimensional analysis of {n_vars} variables in {n_dims} dimensions",
            variables=[{"name": n, "unit": u, "dimensions": str(var_dims[n])}
                      for n, u in variables.items()],
            fundamental_dimensions=[self.FUNDAMENTAL_DIMS.get(d, d) for d in fundamental_dims],
            pi_groups=pi_groups,
            functional_relationship=func_rel
        )
        
    def _choose_repeating_vars(self, dim_matrix: np.ndarray, n_dims: int,
                               var_names: List[str]) -> Tuple[List[str], List[int]]:
        """Choose repeating variables that form a non-singular dimensional matrix."""
        n_vars = len(var_names)
        from itertools import combinations
        
        for indices in combinations(range(n_vars), n_dims):
            submatrix = dim_matrix[:, list(indices)]
            if abs(np.linalg.det(submatrix)) > 1e-10:
                return [var_names[i] for i in indices], list(indices)
                
        raise ValueError("Could not find non-singular set of repeating variables")
        
    def _recognize_pi_group(self, pi_vars: Dict[str, str], all_vars: List[str]) -> str:
        """Recognize well-known dimensionless groups by their variable composition."""
        var_set = set(pi_vars.keys())
        
        # Reynolds number: ρ v L / μ
        if {'rho', 'v', 'L', 'mu'}.issubset(var_set) or \
           {'density', 'velocity', 'length', 'viscosity'}.issubset(var_set):
            return "Reynolds Number (Re)"
            
        # Mach number: v / a (or v / c)
        if {'v', 'a'}.issubset(var_set) or {'v', 'c'}.issubset(var_set):
            if 'v' in var_set and ('a' in var_set or 'c' in var_set):
                return "Mach Number (M)"
                
        # Froude number: v / sqrt(g L)
        if {'v', 'g', 'L'}.issubset(var_set):
            return "Froude Number (Fr)"
            
        # Nusselt number: h L / k
        if {'h', 'L', 'k'}.issubset(var_set):
            return "Nusselt Number (Nu)"
            
        # Prandtl number: μ cp / k or ν / α
        if {'mu', 'cp', 'k'}.issubset(var_set):
            return "Prandtl Number (Pr)"
            
        # Drag coefficient: F / (0.5 ρ v^2 A)
        if {'F', 'rho', 'v', 'A'}.issubset(var_set):
            return "Drag Coefficient (Cd)"
            
        return "Dimensionless Group"
        
    def _describe_meaning(self, name: str, pi_vars: Dict[str, str]) -> str:
        """Provide physical meaning of a dimensionless group."""
        meanings = {
            "Reynolds Number (Re)": "Ratio of inertial to viscous forces; determines flow regime (laminar/turbulent)",
            "Mach Number (M)": "Ratio of flow velocity to speed of sound; determines compressibility effects",
            "Froude Number (Fr)": "Ratio of inertial to gravitational forces; important in free-surface flows",
            "Nusselt Number (Nu)": "Ratio of convective to conductive heat transfer",
            "Prandtl Number (Pr)": "Ratio of momentum diffusivity to thermal diffusivity",
            "Drag Coefficient (Cd)": "Dimensionless measure of drag force on a body",
            "Dimensionless Group": "A dimensionless combination of variables governing system behavior"
        }
        return meanings.get(name, "A dimensionless combination of physical variables")
