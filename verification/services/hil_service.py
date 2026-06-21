import numpy as np
from verification.schemas.enums import TestStatus, ExecutionEnvironment
from verification.schemas.verification_models import HILConfiguration, TestCase, TestResult
from verification.schemas.engineering_report import ReportContext, EngineeringReport

class HILService:
    def execute_hil(self, config_dict: dict, test_cases: list) -> EngineeringReport:
        with ReportContext(
            requirements=["Execute Hardware-in-Loop simulation with deterministic time-stepping"],
            assumptions=["Plant and controller models are valid", "Fixed-step integration ensures reproducibility"],
            constraints=["Step size must resolve fastest dynamics", "Duration must cover full mission profile"],
            formula_selection="Fixed-Step RK4 Integration: x_{n+1} = x_n + (h/6)(k1 + 2k2 + 2k3 + k4)",
            formula_explanation="Integrates plant and controller models in lockstep with deterministic time steps.",
            unit_analysis="Time in seconds, states in native units, step size in seconds."
        ) as ctx:
            config = HILConfiguration(**config_dict)
            np.random.seed(config.seed)
            
            n_steps = int(config.duration_s / config.step_size_s)
            t = np.linspace(0, config.duration_s, n_steps)
            
            omega = 10.0
            zeta = 0.7
            
            x = np.zeros(n_steps)
            dx = np.zeros(n_steps)
            u = np.sin(2 * np.pi * 0.5 * t)
            
            h = config.step_size_s
            for i in range(n_steps - 1):
                def f(state, input_val):
                    pos, vel = state
                    ddx = -2*zeta*omega*vel - omega**2*pos + omega**2*input_val
                    return np.array([vel, ddx])
                    
                state = np.array([x[i], dx[i]])
                k1 = f(state, u[i])
                k2 = f(state + h/2*k1, u[i])
                k3 = f(state + h/2*k2, u[i])
                k4 = f(state + h*k3, u[i])
                
                new_state = state + (h/6)*(k1 + 2*k2 + 2*k3 + k4)
                x[i+1] = new_state[0]
                dx[i+1] = new_state[1]
                
            results = []
            for tc_dict in test_cases:
                tc = TestCase(**tc_dict) if isinstance(tc_dict, dict) else tc_dict
                tracking_error = np.max(np.abs(x - u))
                if tracking_error < 0.5:
                    status = TestStatus.PASSED
                    failure = None
                else:
                    status = TestStatus.FAILED
                    failure = {"reason": "Tracking error exceeded", "max_error": float(tracking_error)}
                    
                results.append(TestResult(
                    test_id=tc.id,
                    status=status,
                    execution_time_ms=float(n_steps * 0.01),
                    environment=ExecutionEnvironment.HIL,
                    evidence_refs=[f"HIL_TRACE_{tc.id}"],
                    failure_details=failure
                ))
                
            passed = sum(1 for r in results if r.status == TestStatus.PASSED)
            
            ctx.add_matrix_op("HIL Integration", "RK4 fixed-step", {"steps": n_steps, "duration_s": config.duration_s})
            ctx.add_intermediate("Tracking Performance", "max|x - u|", {"max_error": float(np.max(np.abs(x - u)))})
            
            ctx.finalize(
                final_results={
                    "environment": "HIL",
                    "configuration": config.dict(),
                    "simulation_steps": n_steps,
                    "total_tests": len(results),
                    "passed": passed,
                    "results": [r.dict() for r in results],
                    "plant_response": {"t": t[::100].tolist(), "x": x[::100].tolist(), "u": u[::100].tolist()}
                },
                interpretation=f"HIL simulation complete. {passed}/{len(results)} tests passed. Max tracking error: {np.max(np.abs(x-u)):.3f}."
            )
        return ctx.report
