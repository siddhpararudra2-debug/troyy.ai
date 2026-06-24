"""
Expertise Mapper for Enterprise Knowledge Hub
Maps user expertise.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ExpertiseMapper:
    """
    Maps user expertise for recommendations.
    """

    def __init__(self):
        self._user_expertise: Dict[str, List[str]] = {}

    async def add_user_expertise(
        self,
        user_id: str,
        expertise: List[str],
    ) -> Dict[str, Any]:
        if user_id not in self._user_expertise:
            self._user_expertise[user_id] = []
        self._user_expertise[user_id].extend(expertise)
        return {"user_id": user_id, "expertise": self._user_expertise[user_id]}

    async def get_experts(self, expertise: str) -> List[str]:
        return [
            user_id
            for user_id, user_expertise in self._user_expertise.items()
            if expertise in user_expertise
        ]
