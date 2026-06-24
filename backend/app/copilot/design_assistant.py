"""
Design Assistant Module of Copilot
Provides help with engineering design decisions.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DesignAssistant:
    """
    Assistant for design-related queries and guidance.
    """

    async def help(self, message: str, context: Dict = None) -> Dict[str, Any]:
        message_lower = message.lower()
        if "material" in message_lower:
            return await self.recommend_material(context)
        elif "fastener" in message_lower:
            return await self.recommend_fastener(context)
        elif "tolerance" in message_lower:
            return await self.recommend_tolerances(context)
        else:
            return {
                "response": "I can help recommend materials, fasteners, or tolerances. What specific design question do you have?",
                "type": "design_assistance",
            }

    async def recommend_material(self, context: Dict = None) -> Dict:
        requirements = (context or {}).get("requirements", "")
        if "lightweight" in requirements.lower() or "drone" in requirements.lower():
            return {
                "response": "For lightweight applications, recommend Aluminum 6061 (high strength-to-weight) or Carbon Fiber (even lighter but more expensive).",
                "recommendations": ["Aluminum 6061", "Carbon Fiber Composite"],
                "type": "material_recommendation",
            }
        return {
            "response": "For general applications, Aluminum 6061 is a safe choice. Consider Stainless Steel for high strength, or Titanium for high performance.",
            "recommendations": ["Aluminum 6061", "Stainless Steel 304", "Titanium Ti-6Al-4V"],
            "type": "material_recommendation",
        }

    async def recommend_fastener(self, context: Dict = None) -> Dict:
        return {
            "response": "Common fasteners are M3/M4 socket head cap screws (SHCS) for small assemblies, M6/M8 for larger structures. Use stainless steel for corrosion resistance.",
            "recommendations": ["M3 SHCS", "M4 SHCS", "M6 SHCS"],
            "type": "fastener_recommendation",
        }

    async def recommend_tolerances(self, context: Dict = None) -> Dict:
        return {
            "response": "Use general tolerances (ISO 2768 medium) for non-critical features, tighter tolerances (e.g., ±0.1mm) for precision fits.",
            "type": "tolerance_recommendation",
        }
