from verification.schemas.verification_models import VerificationMatrixEntry
from verification.schemas.engineering_report import ReportContext, EngineeringReport

class VerificationMatrixService:
    def build_matrix(self, requirements: list, test_cases: list, test_results: list) -> EngineeringReport:
        with ReportContext(
            requirements=["Build bidirectional verification matrix linking requirements to tests and results"],
            assumptions=["All requirements have unique IDs", "Test cases reference valid requirement IDs"],
            constraints=["Every requirement must have ≥1 verification artifact", "Matrix must be complete before certification"],
            formula_selection="Bidirectional Traceability Matrix",
            formula_explanation="Maps each requirement to its verifying tests, analyses, and inspections with status.",
            unit_analysis="Matrix entries are referential, status is categorical."
        ) as ctx:
            matrix = {}
            
            for req in requirements:
                req_id = req.get('id') if isinstance(req, dict) else req.id
                matrix[req_id] = VerificationMatrixEntry(requirement_id=req_id)
                
            for tc in test_cases:
                tc_dict = tc if isinstance(tc, dict) else tc.dict()
                req_id = tc_dict.get('requirement_id')
                if req_id in matrix:
                    matrix[req_id].test_ids.append(tc_dict.get('id'))
                    
            results_by_test = {r.get('test_id') if isinstance(r, dict) else r.test_id: r for r in test_results}
            
            for req_id, entry in matrix.items():
                if not entry.test_ids:
                    entry.coverage_status = "NOT_VERIFIED"
                else:
                    statuses = [results_by_test[tid].get('status') if isinstance(results_by_test.get(tid), dict) 
                                else results_by_test[tid].status 
                                for tid in entry.test_ids if tid in results_by_test]
                    if all(s == 'PASSED' for s in statuses):
                        entry.coverage_status = "VERIFIED"
                    elif any(s == 'FAILED' for s in statuses):
                        entry.coverage_status = "FAILED"
                    else:
                        entry.coverage_status = "PARTIAL"
                        
            verified = sum(1 for e in matrix.values() if e.coverage_status == "VERIFIED")
            total = len(matrix)
            coverage_pct = (verified / total * 100) if total > 0 else 0
            
            ctx.add_matrix_op("Matrix Assembly", "M = R × T × Results", {"requirements": total, "verified": verified})
            
            ctx.finalize(
                final_results={
                    "total_requirements": total,
                    "verified": verified,
                    "coverage_pct": coverage_pct,
                    "matrix": [e.dict() for e in matrix.values()]
                },
                interpretation=f"Verification matrix: {verified}/{total} requirements verified ({coverage_pct:.1f}%)."
            )
        return ctx.report
