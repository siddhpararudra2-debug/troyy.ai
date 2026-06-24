"""
Health Monitoring Service for LLM infrastructure.
"""
from typing import List
from datetime import datetime
from app.core.config import settings
from app.llm.schemas.schemas import ModelHealth, HealthCheckResponse
from app.llm.services.ollama_service import OllamaService


class HealthService:
    """Service to monitor health of all local AI models."""

    def __init__(self, ollama_service: OllamaService) -> None:
        self.ollama_service = ollama_service
        self.models_to_check = [
            settings.OLLAMA_MODEL_CODING,
            settings.OLLAMA_MODEL_ENGINEERING,
            settings.OLLAMA_MODEL_REASONING
        ]

    async def check_health(self) -> HealthCheckResponse:
        """Check health status of all configured models."""
        model_health_list: List[ModelHealth] = []
        all_healthy = True

        for model in self.models_to_check:
            is_available, response_time = await self.ollama_service.is_model_available(model)
            status = "available" if is_available else "unavailable"
            if not is_available:
                all_healthy = False
            model_health_list.append(
                ModelHealth(
                    name=model,
                    status=status,
                    response_time_ms=response_time,
                    last_checked=datetime.utcnow()
                )
            )

        overall_status: str = "healthy"
        if not all_healthy:
            # Check if at least one model is available
            any_available = any(m.status == "available" for m in model_health_list)
            overall_status = "degraded" if any_available else "unhealthy"

        return HealthCheckResponse(
            overall_status=overall_status,  # type: ignore
            models=model_health_list,
            timestamp=datetime.utcnow()
        )
