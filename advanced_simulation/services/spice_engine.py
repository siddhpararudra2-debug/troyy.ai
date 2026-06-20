import numpy as np
from scipy.integrate import solve_ivp
from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport
from advanced_simulation.schemas.requests import SPICERequest

class SPICEEngine:
    def simulate_transient(self, req: SPICERequest) -> EngineeringReport:
        G = np.array(req.conductance_matrix)
        C = np.array(req.capacitance_matrix)
        I = np.array(req.current_sources)
        
        with ReportContext(
            requirements=["Perform transient nodal analysis of the circuit"],
            assumptions=["Linear time-invariant components", "Ideal sources"],
            constraints=["Capacitance matrix must be positive semi-definite"],
            formula_selection="Modified Nodal Analysis with Capacitive Transients: C * dV/dt + G * V = I",
            formula_explanation="Solves the system of differential equations governing node voltages over time using SciPy's RK45 solver.",
            unit_analysis="G in Siemens (S), C in Farads (F), V in Volts (V), I in Amps (A), t in seconds (s)."
        ) as ctx:
            # Add source contribution to current vector (simplified)
            I_vec = I + req.source_voltage * np.sum(G, axis=1) 
            
            def circuit_ode(t, v):
                # C * dv/dt = I - G * v  =>  dv/dt = C^-1 * (I - G * v)
                # To avoid singular C, we use a pseudo-inverse or ensure C is non-singular
                dvdt = np.linalg.solve(C + 1e-12*np.eye(len(v)), I_vec - G @ v)
                return dvdt

            ctx.add_matrix_op("ODE Formulation", "dv/dt = C^-1 * (I - G*v)", {"G": G.tolist(), "C": C.tolist()})
            
            t_span = (0, req.simulation_time_s)
            t_eval = np.arange(0, req.simulation_time_s, req.time_step_s)
            v0 = np.zeros(req.nodes)
            
            sol = solve_ivp(circuit_ode, t_span, v0, t_eval=t_eval, method='RK45')
            
            if not sol.success:
                raise ValueError(f"SPICE Transient Diverged: {sol.message}")
                
            final_v = sol.y[:, -1]
            max_v = np.max(sol.y, axis=1)
            
            ctx.add_intermediate("Integration Result", "RK45 over t_span", {"status": sol.status, "steps": sol.nfev})
            
            ctx.finalize(
                final_results={"final_voltages_v": final_v.tolist(), "peak_voltages_v": max_v.tolist(), "time_steps": len(t_eval)},
                interpretation=f"Transient simulation completed in {sol.nfev} function evaluations. Peak voltage observed: {np.max(max_v):.3f}V."
            )
        return ctx.report
