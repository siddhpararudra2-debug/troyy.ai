from verification.schemas.enums import VerificationMethod
from verification.schemas.verification_models import Requirement, VerificationMatrixEntry
from verification.schemas.engineering_report import ReportContext, EngineeringReport

class VerificationPlanningService:
    def generate_plan(self, requirements: list, target_dal: str) -> EngineeringReport:
        with ReportContext(
            requirements=["Generate verification plan mapping requirements to verification methods"],
            assumptions=["Requirements are unambiguous and testable", "Target DAL determines coverage requirements"],
            constraints=["Every requirement must have ≥1 verification method", "DAL A requires MC/DC coverage"],
            formula_selection="Requirements-to-Verification Mapping Matrix",
            formula_explanation="Builds a bidirectional traceability matrix linking each requirement to verification activities.",
            unit_analysis="Requirements are categorical, verification methods are categorical."
        ) as ctx:
            matrix = []
            coverage_targets = {
                "A": {"statement": 100, "branch": 100, "mcdc": 100},
                "B": {"statement": 100, "branch": 100, "mcdc": 0},
                "C": {"statement": 100, "branch": 100, "mcdc": 0},
                "D": {"statement": 100, "branch": 0, "mcdc": 0},
                "E": {"statement": 0, "branch": 0, "mcdc": 0}
            }
            
            for req_dict in requirements:
                req = Requirement(**req_dict)
                entry = VerificationMatrixEntry(requirement_id=req.id)
                
                if req.verification_method == VerificationMethod.TEST:
                    entry.coverage_status = "TEST_REQUIRED"
                elif req.verification_method == VerificationMethod.ANALYSIS:
                    entry.coverage_status = "ANALYSIS_REQUIRED"
                elif req.verification_method == VerificationMethod.SIMULATION:
                    entry.coverage_status = "SIMULATION_REQUIRED"
                else:
                    entry.coverage_status = "REVIEW_REQUIRED"
                    
                matrix.append(entry)
                
            ctx.add_matrix_op("Traceability Matrix", "M[i,j] = R_i → V_j", {"requirements": len(matrix)})
            ctx.add_intermediate("DAL Coverage Targets", f"DAL {target_dal}", {"targets": coverage_targets.get(target_dal, {})})
            
            ctx.finalize(
                final_results={
                    "target_dal": target_dal,
                    "coverage_targets": coverage_targets.get(target_dal, {}),
                    "total_requirements": len(matrix),
                    "verification_matrix": [m.dict() for m in matrix]
                },
                interpretation=f"Verification plan generated for DAL {target_dal}. {len(matrix)} requirements mapped."
            )
        return ctx.report
