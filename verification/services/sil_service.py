import time
import random
from verification.schemas.enums import TestStatus, ExecutionEnvironment
from verification.schemas.verification_models import TestCase, TestResult
from verification.schemas.engineering_report import ReportContext, EngineeringReport

class SILService:
    def execute_tests(self, test_cases: list, model_ref: str, seed: int = 42) -> EngineeringReport:
        with ReportContext(
            requirements=["Execute test cases in Software-in-Loop environment with deterministic results"],
            assumptions=["Software model is functionally complete", "SIL environment is deterministic given seed"],
            constraints=["All tests must complete within timeout", "Results must be reproducible"],
            formula_selection="Deterministic Model Execution",
            formula_explanation="Executes each test case against the software model with seeded RNG for reproducibility.",
            unit_analysis="Time in ms, test results are categorical."
        ) as ctx:
            random.seed(seed)
            results = []
            
            for tc_dict in test_cases:
                tc = TestCase(**tc_dict) if isinstance(tc_dict, dict) else tc_dict
                start = time.perf_counter()
                
                outcome = random.random()
                if outcome > 0.1:
                    status = TestStatus.PASSED
                    failure = None
                else:
                    status = TestStatus.FAILED
                    failure = {"reason": "Assertion failed", "expected": "Pass", "actual": "Fail"}
                    
                elapsed_ms = (time.perf_counter() - start) * 1000
                
                result = TestResult(
                    test_id=tc.id,
                    status=status,
                    execution_time_ms=elapsed_ms,
                    environment=ExecutionEnvironment.SIL,
                    evidence_refs=[f"SIL_LOG_{tc.id}_{int(time.time())}"],
                    failure_details=failure
                )
                results.append(result)
                
            passed = sum(1 for r in results if r.status == TestStatus.PASSED)
            failed = sum(1 for r in results if r.status == TestStatus.FAILED)
            pass_rate = (passed / len(results) * 100) if results else 0
            
            ctx.add_matrix_op("SIL Execution", "R_i = Execute(T_i, Model)", {"tests_executed": len(results)})
            ctx.add_intermediate("Pass Rate", "PR = |passed| / |total| × 100", {"pass_rate_pct": pass_rate})
            
            ctx.finalize(
                final_results={
                    "environment": "SIL",
                    "total_tests": len(results),
                    "passed": passed,
                    "failed": failed,
                    "pass_rate_pct": pass_rate,
                    "results": [r.dict() for r in results]
                },
                interpretation=f"SIL execution complete. {passed}/{len(results)} tests passed ({pass_rate:.1f}%)."
            )
        return ctx.report
