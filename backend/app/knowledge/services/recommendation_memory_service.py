"""
Recommendation Memory Service
"""


class RecommendationMemoryService:
    @staticmethod
    def store_recommendation(project_id: str, recommendation: dict, outcome: str = None):
        return True

    @staticmethod
    def get_successful_recommendations(project_type: str):
        return []
