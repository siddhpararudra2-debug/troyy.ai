"""
Requirement Compliance Service
"""


class RequirementComplianceService:
    @staticmethod
    def link_requirement_to_standard(project_id: str, requirement_id: str, standard_id: str):
        return True

    @staticmethod
    def track_verification(project_id: str, requirement_id: str, evidence_id: str):
        return True
