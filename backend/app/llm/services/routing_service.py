"""
Model Routing Service.
"""
from typing import Literal, Optional
from app.core.config import settings
from app.llm.schemas.schemas import RoutingDecision
from app.llm.services.ollama_service import OllamaService


class RoutingService:
    """Service to route requests to appropriate models with fallback."""

    def __init__(self, ollama_service: OllamaService) -> None:
        self.ollama_service = ollama_service
        self.model_map = {
            "coding": settings.OLLAMA_MODEL_CODING,
            "engineering": settings.OLLAMA_MODEL_ENGINEERING,
            "reasoning": settings.OLLAMA_MODEL_REASONING
        }
        # Fallback chain: try other models in order
        self.fallback_order = [
            settings.OLLAMA_MODEL_ENGINEERING,
            settings.OLLAMA_MODEL_REASONING,
            settings.OLLAMA_MODEL_CODING
        ]

    async def get_model(self, model_type: Literal["coding", "engineering", "reasoning"]) -> RoutingDecision:
        """Get the appropriate model, checking availability and using fallbacks if needed."""
        requested_model = self.model_map[model_type]

        # Check if requested model is available
        is_available, _ = await self.ollama_service.is_model_available(requested_model)
        if is_available:
            return RoutingDecision(
                requested_model_type=model_type,
                selected_model=requested_model,
                fallback_available=True,
                reasoning="Primary model selected"
            )

        # Try fallbacks
        for fallback_model in self.fallback_order:
            if fallback_model == requested_model:
                continue
            is_fallback_available, _ = await self.ollama_service.is_model_available(fallback_model)
            if is_fallback_available:
                return RoutingDecision(
                    requested_model_type=model_type,
                    selected_model=fallback_model,
                    fallback_available=True,
                    reasoning=f"Fallback: using {fallback_model} because {requested_model} was unavailable"
                )

        # No models available
        return RoutingDecision(
            requested_model_type=model_type,
            selected_model=requested_model,
            fallback_available=False,
            reasoning="No models available"
        )
