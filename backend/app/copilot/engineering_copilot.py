"""
Engineering Copilot Module
Provides engineering assistance through various assistant modules.
"""
import logging
from typing import Dict, Any
from app.copilot.design_assistant import DesignAssistant
from app.copilot.review_assistant import ReviewAssistant
from app.copilot.planning_assistant import PlanningAssistant

logger = logging.getLogger(__name__)


class EngineeringCopilot:
    """
    Unified engineering copilot interface that aggregates multiple assistants.
    """

    def __init__(
        self,
        design_assistant: DesignAssistant = None,
        review_assistant: ReviewAssistant = None,
        planning_assistant: PlanningAssistant = None,
    ):
        self.design = design_assistant or DesignAssistant()
        self.review = review_assistant or ReviewAssistant()
        self.planning = planning_assistant or PlanningAssistant()

    async def chat(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        General chat interface for the copilot.
        """
        message_lower = message.lower()
        if "design" in message_lower or "cadd" in message_lower or "cad" in message_lower:
            return await self.design.help(message, context)
        elif "review" in message_lower or "validate" in message_lower:
            return await self.review.help(message, context)
        elif "plan" in message_lower or "schedule" in message_lower or "milestone" in message_lower:
            return await self.planning.help(message, context)
        else:
            return {
                "response": "I'm your engineering copilot! I can help with design, review, and planning tasks. What do you need?",
                "type": "general",
            }
