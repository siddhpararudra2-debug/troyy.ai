from verification.schemas.engineering_report import ReportContext, EngineeringReport

class VerificationReportService:
    def generate_certification_package(self, plan: dict, matrix: dict, coverage: dict, test_results: list) -> EngineeringReport:
        with ReportContext(
            requirements=["Generate certification-ready verification package"],
            assumptions=["All verification activities are complete", "Evidence is traceable and hashed"],
            constraints=["Package must satisfy certification authority requirements"],
            formula_selection="Certification Package Assembly",
            formula_explanation="Compiles verification plan, matrix, coverage, and results into a unified certification package.",
            unit_analysis="Package sections are categorical, metrics are quantitative."
        ) as ctx:
            package = {
                "verification_plan": plan.get('final_results', {}),
                "verification_matrix": matrix.get('final_results', {}),
                "coverage_analysis": coverage.get('final_results', {}),
                "test_summary": {
                    "total_tests": len(test_results),
                    "passed": sum(1 for r in test_results if (r.get('status') if isinstance(r, dict) else r.status) == 'PASSED'),
                    "failed": sum(1 for r in test_results if (r.get('status') if isinstance(r, dict) else r.status) == 'FAILED')
                },
                "certification_readiness": "READY" if matrix.get('final_results', {}).get('coverage_pct', 0) == 100 else "PENDING"
            }
            
            ctx.finalize(
                final_results=package,
                interpretation=f"Certification package generated. Readiness: {package['certification_readiness']}."
            )
        return ctx.report
