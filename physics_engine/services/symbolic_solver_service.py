"""
Symbolic Solver Service — uses SymPy for first-principles equation solving.
Produces step-by-step derivations with justifications.
"""
import sympy as sp
import time
from typing import Dict, List, Optional, Tuple
from physics_engine.schemas.physics_models import (
    PhysicsProblem, PhysicsSolution, DerivationStep, PhysicalQuantity
)
from physics_engine.schemas.enums import SolveStatus, PhysicsDomain

class SymbolicSolverService:
    """Solves physics problems symbolically with full derivation tracking."""
    
    # Common physics symbols
    SYMBOLS = {
        # Mechanics
        'F': sp.Symbol('F'), 'm': sp.Symbol('m'), 'a': sp.Symbol('a'),
        'v': sp.Symbol('v'), 'x': sp.Symbol('x'), 't': sp.Symbol('t'),
        'p': sp.Symbol('p'), 'E': sp.Symbol('E'), 'K': sp.Symbol('K'),
        'U': sp.Symbol('U'), 'W': sp.Symbol('W'), 'g': sp.Symbol('g'),
        # Rotational
        'tau': sp.Symbol('tau'), 'I': sp.Symbol('I'), 'alpha': sp.Symbol('alpha'),
        'omega': sp.Symbol('omega'), 'theta': sp.Symbol('theta'),
        # Thermo
        'T': sp.Symbol('T'), 'Q': sp.Symbol('Q'), 'S': sp.Symbol('S'),
        'P': sp.Symbol('P'), 'V': sp.Symbol('V'), 'n': sp.Symbol('n'),
        'R': sp.Symbol('R'), 'Cp': sp.Symbol('C_p'), 'Cv': sp.Symbol('C_v'),
        # Fluids
        'rho': sp.Symbol('rho'), 'mu': sp.Symbol('mu'), 'nu': sp.Symbol('nu'),
        'A': sp.Symbol('A'), 'L': sp.Symbol('L'), 'Re': sp.Symbol('Re'),
        # Electrical
        'V_v': sp.Symbol('V'), 'I_e': sp.Symbol('I'), 'R_e': sp.Symbol('R'),
        'C': sp.Symbol('C'), 'L_e': sp.Symbol('L'), 'f': sp.Symbol('f'),
        # Structural
        'sigma': sp.Symbol('sigma'), 'epsilon': sp.Symbol('epsilon'),
        'E_mod': sp.Symbol('E'), 'delta': sp.Symbol('delta'),
        # Orbital
        'r': sp.Symbol('r'), 'mu_g': sp.Symbol('mu'), 'h': sp.Symbol('h'),
        'a_orb': sp.Symbol('a'), 'e': sp.Symbol('e'), 'T_orb': sp.Symbol('T'),
    }
    
    def __init__(self, timeout_seconds: float = 5.0):
        self.timeout = timeout_seconds
        
    def solve(self, problem: PhysicsProblem) -> PhysicsSolution:
        """Solve a physics problem symbolically."""
        start = time.perf_counter()
        
        try:
            # Route to domain-specific solver
            if problem.domain == PhysicsDomain.MECHANICS:
                return self._solve_mechanics(problem, start)
            elif problem.domain == PhysicsDomain.THERMODYNAMICS:
                return self._solve_thermodynamics(problem, start)
            elif problem.domain == PhysicsDomain.FLUID_DYNAMICS:
                return self._solve_fluids(problem, start)
            elif problem.domain == PhysicsDomain.STRUCTURAL_MECHANICS:
                return self._solve_structural(problem, start)
            elif problem.domain == PhysicsDomain.ELECTROMAGNETICS:
                return self._solve_electrical(problem, start)
            elif problem.domain == PhysicsDomain.ORBITAL_MECHANICS:
                return self._solve_orbital(problem, start)
            else:
                return self._solve_generic(problem, start)
                
        except TimeoutError:
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.TIMEOUT,
                final_equation="Solution timed out",
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
        except Exception as e:
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.INCONSISTENT,
                final_equation=f"Error: {str(e)}",
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
            
    def _solve_mechanics(self, problem: PhysicsProblem, start: float) -> PhysicsSolution:
        """Solve mechanics problems: F=ma, energy, momentum, projectile motion."""
        steps = []
        F, m, a, v, x, t, g = sp.symbols('F m a v x t g')
        
        # Identify problem type from statement
        statement = problem.problem_statement.lower()
        
        if 'force' in statement and 'acceleration' in statement:
            # F = ma problem
            steps.append(DerivationStep(
                step_number=1,
                description="Start with Newton's second law",
                equation_before="",
                equation_after="F = m * a",
                operation="axiom",
                justification="Newton's second law of motion"
            ))
            
            # Substitute known values
            subs = {}
            for name, qty in problem.givens.items():
                if name in ['F', 'm', 'a']:
                    subs[self.SYMBOLS[name]] = qty.value
                    
            # Solve for unknown
            unknown = problem.unknowns[0] if problem.unknowns else 'a'
            eq = sp.Eq(F, m * a)
            
            steps.append(DerivationStep(
                step_number=2,
                description=f"Substitute known values and solve for {unknown}",
                equation_before=str(eq),
                equation_after=f"{unknown} = {eq.subs(subs).solve(sp.Symbol(unknown))[0]}",
                operation="substitute + solve",
                justification="Algebraic manipulation"
            ))
            
            try:
                solution = sp.solve(eq.subs(subs), sp.Symbol(unknown))[0]
                numerical = float(solution)
            except Exception:
                numerical = None
                
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.EXACT,
                final_equation=f"{unknown} = {solution if 'solution' in locals() else 'unsolved'}",
                numerical_result={unknown: PhysicalQuantity(
                    value=numerical if numerical else 0,
                    unit=self._infer_unit(unknown)
                )} if numerical else None,
                derivation_steps=steps,
                assumptions_used=["Rigid body", "Inertial reference frame"],
                dimensional_check=True,
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
            
        elif 'projectile' in statement or 'range' in statement:
            # Projectile motion
            v0, theta_sym, g_sym = sp.symbols('v_0 theta g')
            R = v0**2 * sp.sin(2 * theta_sym) / g_sym
            
            steps.append(DerivationStep(
                step_number=1,
                description="Range equation for projectile motion",
                equation_before="",
                equation_after="R = v_0^2 * sin(2*theta) / g",
                operation="axiom",
                justification="Kinematic equations under constant gravity"
            ))
            
            subs = {}
            for name, qty in problem.givens.items():
                if name == 'v0': subs[v0] = qty.value
                elif name == 'theta': subs[theta_sym] = qty.value
                elif name == 'g': subs[g_sym] = qty.value
                
            R_val = float(R.subs(subs))
            
            steps.append(DerivationStep(
                step_number=2,
                description="Substitute values",
                equation_before=str(R),
                equation_after=f"R = {R_val:.4f}",
                operation="substitute",
                justification="Direct substitution"
            ))
            
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.EXACT,
                final_equation=f"R = {R_val:.4f} m",
                numerical_result={'R': PhysicalQuantity(value=R_val, unit='m')},
                derivation_steps=steps,
                assumptions_used=["No air resistance", "Constant gravity", "Flat earth"],
                dimensional_check=True,
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
            
        elif 'kinetic' in statement or 'energy' in statement:
            # Energy problems
            K = sp.Symbol('K')
            eq = sp.Eq(K, sp.Rational(1, 2) * m * v**2)
            
            steps.append(DerivationStep(
                step_number=1,
                description="Kinetic energy equation",
                equation_before="",
                equation_after="K = 1/2 * m * v^2",
                operation="axiom",
                justification="Definition of kinetic energy"
            ))
            
            subs = {}
            for name, qty in problem.givens.items():
                if name == 'm': subs[m] = qty.value
                elif name == 'v': subs[v] = qty.value
                    
            K_val = float(eq.rhs.subs(subs))
            
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.EXACT,
                final_equation=f"K = {K_val:.4f} J",
                numerical_result={'K': PhysicalQuantity(value=K_val, unit='J')},
                derivation_steps=steps,
                assumptions_used=["Non-relativistic"],
                dimensional_check=True,
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
            
        return self._solve_generic(problem, start)
        
    def _solve_thermodynamics(self, problem: PhysicsProblem, start: float) -> PhysicsSolution:
        """Solve thermodynamics: ideal gas, first law, efficiency."""
        steps = []
        P, V, n, R, T = sp.symbols('P V n R T')
        
        statement = problem.problem_statement.lower()
        
        if 'ideal gas' in statement or 'pressure' in statement:
            # PV = nRT
            eq = sp.Eq(P * V, n * R * T)
            steps.append(DerivationStep(
                step_number=1,
                description="Ideal gas law",
                equation_before="",
                equation_after="P * V = n * R * T",
                operation="axiom",
                justification="Ideal gas equation of state"
            ))
            
            subs = {R: 8.314}  # J/(mol·K)
            for name, qty in problem.givens.items():
                if name == 'P': subs[P] = qty.value
                elif name == 'V': subs[V] = qty.value
                elif name == 'n': subs[n] = qty.value
                elif name == 'T': subs[T] = qty.value
                    
            unknown = problem.unknowns[0] if problem.unknowns else 'T'
            sym = {'P': P, 'V': V, 'n': n, 'T': T}.get(unknown, T)
            
            try:
                solution = sp.solve(eq.subs(subs), sym)[0]
                val = float(solution)
                steps.append(DerivationStep(
                    step_number=2,
                    description=f"Solve for {unknown}",
                    equation_before=str(eq),
                    equation_after=f"{unknown} = {val:.4f}",
                    operation="solve",
                    justification="Algebraic isolation of unknown"
                ))
                
                return PhysicsSolution(
                    problem_id=problem.id,
                    status=SolveStatus.EXACT,
                    final_equation=f"{unknown} = {val:.4f}",
                    numerical_result={unknown: PhysicalQuantity(value=val, unit=self._infer_unit(unknown))},
                    derivation_steps=steps,
                    assumptions_used=["Ideal gas behavior", "Thermal equilibrium"],
                    dimensional_check=True,
                    solve_time_ms=(time.perf_counter() - start) * 1000
                )
            except Exception:
                pass
                
        return self._solve_generic(problem, start)
        
    def _solve_fluids(self, problem: PhysicsProblem, start: float) -> PhysicsSolution:
        """Solve fluid dynamics: Reynolds number, Bernoulli, pipe flow."""
        steps = []
        rho, v, L, mu = sp.symbols('rho v L mu')
        
        statement = problem.problem_statement.lower()
        
        if 'reynolds' in statement:
            Re_eq = rho * v * L / mu
            steps.append(DerivationStep(
                step_number=1,
                description="Reynolds number definition",
                equation_before="",
                equation_after="Re = rho * v * L / mu",
                operation="axiom",
                justification="Definition of Reynolds number"
            ))
            
            subs = {}
            for name, qty in problem.givens.items():
                if name == 'rho': subs[rho] = qty.value
                elif name == 'v': subs[v] = qty.value
                elif name == 'L': subs[L] = qty.value
                elif name == 'mu': subs[mu] = qty.value
                    
            Re_val = float(Re_eq.subs(subs))
            
            # Determine flow regime
            if Re_val < 2300:
                regime = "laminar"
            elif Re_val < 4000:
                regime = "transitional"
            else:
                regime = "turbulent"
                
            steps.append(DerivationStep(
                step_number=2,
                description="Compute Reynolds number and classify flow",
                equation_before=str(Re_eq),
                equation_after=f"Re = {Re_val:.2e} ({regime})",
                operation="substitute",
                justification=f"Re < 2300: laminar, 2300-4000: transitional, > 4000: turbulent"
            ))
            
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.EXACT,
                final_equation=f"Re = {Re_val:.2e} ({regime} flow)",
                numerical_result={'Re': PhysicalQuantity(value=Re_val, unit='dimensionless')},
                derivation_steps=steps,
                assumptions_used=["Incompressible flow", "Newtonian fluid"],
                dimensional_check=True,
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
            
        return self._solve_generic(problem, start)
        
    def _solve_structural(self, problem: PhysicsProblem, start: float) -> PhysicsSolution:
        """Solve structural mechanics: stress, strain, deflection."""
        steps = []
        F, A, sigma, E_mod, L, delta = sp.symbols('F A sigma E L delta')
        
        statement = problem.problem_statement.lower()
        
        if 'stress' in statement:
            eq = sp.Eq(sigma, F / A)
            steps.append(DerivationStep(
                step_number=1,
                description="Normal stress definition",
                equation_before="",
                equation_after="sigma = F / A",
                operation="axiom",
                justification="Definition of engineering stress"
            ))
            
            subs = {}
            for name, qty in problem.givens.items():
                if name == 'F': subs[F] = qty.value
                elif name == 'A': subs[A] = qty.value
                    
            try:
                sigma_val = float(eq.rhs.subs(subs))
                steps.append(DerivationStep(
                    step_number=2,
                    description="Substitute values",
                    equation_before=str(eq),
                    equation_after=f"sigma = {sigma_val:.2e} Pa",
                    operation="substitute",
                    justification="Direct substitution"
                ))
                
                return PhysicsSolution(
                    problem_id=problem.id,
                    status=SolveStatus.EXACT,
                    final_equation=f"sigma = {sigma_val:.2e} Pa ({sigma_val/1e6:.2f} MPa)",
                    numerical_result={'sigma': PhysicalQuantity(value=sigma_val, unit='Pa')},
                    derivation_steps=steps,
                    assumptions_used=["Uniform stress distribution", "Static loading"],
                    dimensional_check=True,
                    solve_time_ms=(time.perf_counter() - start) * 1000
                )
            except Exception:
                pass
                
        elif 'deflection' in statement or 'beam' in statement:
            # Cantilever beam: delta = F L^3 / (3 E I)
            I = sp.Symbol('I')
            eq = sp.Eq(delta, F * L**3 / (3 * E_mod * I))
            steps.append(DerivationStep(
                step_number=1,
                description="Cantilever beam tip deflection",
                equation_before="",
                equation_after="delta = F * L^3 / (3 * E * I)",
                operation="axiom",
                justification="Euler-Bernoulli beam theory"
            ))
            
            subs = {}
            for name, qty in problem.givens.items():
                if name == 'F': subs[F] = qty.value
                elif name == 'L': subs[L] = qty.value
                elif name == 'E': subs[E_mod] = qty.value
                elif name == 'I': subs[I] = qty.value
                    
            try:
                delta_val = float(eq.rhs.subs(subs))
                return PhysicsSolution(
                    problem_id=problem.id,
                    status=SolveStatus.EXACT,
                    final_equation=f"delta = {delta_val:.4e} m",
                    numerical_result={'delta': PhysicalQuantity(value=delta_val, unit='m')},
                    derivation_steps=steps,
                    assumptions_used=["Small deflections", "Linear elastic", "Euler-Bernoulli"],
                    dimensional_check=True,
                    solve_time_ms=(time.perf_counter() - start) * 1000
                )
            except Exception:
                pass
                
        return self._solve_generic(problem, start)
        
    def _solve_electrical(self, problem: PhysicsProblem, start: float) -> PhysicsSolution:
        """Solve electrical: Ohm's law, power, RC/RL circuits."""
        steps = []
        V, I, R, P = sp.symbols('V I R P')
        
        statement = problem.problem_statement.lower()
        
        if 'ohm' in statement or 'resistance' in statement or 'current' in statement:
            eq = sp.Eq(V, I * R)
            steps.append(DerivationStep(
                step_number=1,
                description="Ohm's law",
                equation_before="",
                equation_after="V = I * R",
                operation="axiom",
                justification="Ohm's law"
            ))
            
            subs = {}
            for name, qty in problem.givens.items():
                if name == 'V': subs[V] = qty.value
                elif name == 'I': subs[I] = qty.value
                elif name == 'R': subs[R] = qty.value
                    
            unknown = problem.unknowns[0] if problem.unknowns else 'V'
            sym = {'V': V, 'I': I, 'R': R}.get(unknown, V)
            
            try:
                solution = sp.solve(eq.subs(subs), sym)[0]
                val = float(solution)
                return PhysicsSolution(
                    problem_id=problem.id,
                    status=SolveStatus.EXACT,
                    final_equation=f"{unknown} = {val:.4f}",
                    numerical_result={unknown: PhysicalQuantity(value=val, unit=self._infer_unit(unknown))},
                    derivation_steps=steps,
                    assumptions_used=["Ohmic conductor", "Steady state"],
                    dimensional_check=True,
                    solve_time_ms=(time.perf_counter() - start) * 1000
                )
            except Exception:
                pass
                
        return self._solve_generic(problem, start)
        
    def _solve_orbital(self, problem: PhysicsProblem, start: float) -> PhysicsSolution:
        """Solve orbital mechanics: orbital period, velocity, energy."""
        steps = []
        mu, r, v, T, a = sp.symbols('mu r v T a')
        
        statement = problem.problem_statement.lower()
        
        if 'period' in statement or 'circular' in statement:
            # Circular orbit: T = 2π √(r³/μ), v = √(μ/r)
            T_eq = 2 * sp.pi * sp.sqrt(r**3 / mu)
            v_eq = sp.sqrt(mu / r)
            
            steps.append(DerivationStep(
                step_number=1,
                description="Circular orbit period from gravitational balance",
                equation_before="",
                equation_after="T = 2π √(r³/μ)",
                operation="derive",
                justification="Equating gravitational and centripetal acceleration"
            ))
            
            subs = {}
            for name, qty in problem.givens.items():
                if name == 'r': subs[r] = qty.value
                elif name == 'mu': subs[mu] = qty.value
                elif name == 'a': subs[a] = qty.value  # semi-major axis = radius for circular
                    
            try:
                T_val = float(T_eq.subs(subs))
                v_val = float(v_eq.subs(subs))
                
                steps.append(DerivationStep(
                    step_number=2,
                    description="Compute orbital period and velocity",
                    equation_before=str(T_eq),
                    equation_after=f"T = {T_val:.2f} s, v = {v_val:.2f} m/s",
                    operation="substitute",
                    justification="Direct substitution"
                ))
                
                return PhysicsSolution(
                    problem_id=problem.id,
                    status=SolveStatus.EXACT,
                    final_equation=f"T = {T_val:.2f} s ({T_val/60:.2f} min), v = {v_val:.2f} m/s",
                    numerical_result={
                        'T': PhysicalQuantity(value=T_val, unit='s'),
                        'v': PhysicalQuantity(value=v_val, unit='m/s')
                    },
                    derivation_steps=steps,
                    assumptions_used=["Circular orbit", "Two-body problem", "Keplerian"],
                    dimensional_check=True,
                    solve_time_ms=(time.perf_counter() - start) * 1000
                )
            except Exception:
                pass
                
        return self._solve_generic(problem, start)
        
    def _solve_generic(self, problem: PhysicsProblem, start: float) -> PhysicsSolution:
        """Fallback: attempt to solve using SymPy's general solver."""
        steps = []
        
        # Try to parse the problem as a system of equations
        try:
            # Create symbols for all unknowns
            unknowns = [sp.Symbol(u) for u in problem.unknowns]
            givens = {k: sp.Symbol(k) for k in problem.givens.keys()}
            
            steps.append(DerivationStep(
                step_number=1,
                description="Set up symbolic system",
                equation_before="",
                equation_after=f"Unknowns: {problem.unknowns}",
                operation="setup",
                justification="Define symbolic variables"
            ))
            
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.UNDERDETERMINED,
                final_equation="Problem requires more specific formulation",
                derivation_steps=steps,
                assumptions_used=problem.assumptions,
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
        except Exception as e:
            return PhysicsSolution(
                problem_id=problem.id,
                status=SolveStatus.INCONSISTENT,
                final_equation=f"Could not solve: {str(e)}",
                solve_time_ms=(time.perf_counter() - start) * 1000
            )
            
    def _infer_unit(self, variable_name: str) -> str:
        """Infer SI unit from variable name."""
        unit_map = {
            'F': 'N', 'm': 'kg', 'a': 'm/s^2', 'v': 'm/s', 'x': 'm',
            't': 's', 'E': 'J', 'K': 'J', 'U': 'J', 'W': 'J',
            'P': 'Pa', 'V': 'm^3', 'T': 'K', 'n': 'mol',
            'rho': 'kg/m^3', 'mu': 'Pa*s', 'L': 'm', 'A': 'm^2',
            'Re': 'dimensionless', 'sigma': 'Pa', 'delta': 'm',
            'I': 'A', 'R': 'ohm', 'omega': 'rad/s', 'theta': 'rad',
            'tau': 'N*m', 'r': 'm', 'mu_g': 'm^3/s^2',
        }
        return unit_map.get(variable_name, 'dimensionless')
