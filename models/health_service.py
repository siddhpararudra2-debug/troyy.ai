"""
Health monitoring service for local AI infrastructure.
Tracks model availability, response times, and system health.
"""
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ModelHealth:
    """Health status for a single model."""
    model_name: str
    available: bool = False
    last_check: Optional[datetime] = None
    avg_response_time: float = 0.0
    error_count: int = 0
    total_requests: int = 0


@dataclass
class SystemHealth:
    """Overall system health status."""
    ollama_available: bool = False
    redis_available: bool = False
    postgres_available: bool = False
    qdrant_available: bool = False
    models: dict[str, ModelHealth] = field(default_factory=dict)
    last_updated: Optional[datetime] = None


class HealthService:
    """Service for monitoring AI infrastructure health."""

    def __init__(self):
        self._models: dict[str, ModelHealth] = {}
        self._ollama_available = False
        self._redis_available = False
        self._postgres_available = False
        self._qdrant_available = False
        self._last_update: Optional[datetime] = None

    def register_model(self, model_name: str) -> ModelHealth:
        """Register a model for health tracking."""
        if model_name not in self._models:
            self._models[model_name] = ModelHealth(model_name=model_name)
        return self._models[model_name]

    def record_success(self, model_name: str, response_time: float):
        """Record a successful model invocation."""
        health = self.register_model(model_name)
        health.available = True
        health.last_check = datetime.utcnow()
        health.total_requests += 1
        # Exponential moving average
        if health.avg_response_time == 0:
            health.avg_response_time = response_time
        else:
            health.avg_response_time = (
                0.9 * health.avg_response_time + 0.1 * response_time
            )

    def record_error(self, model_name: str):
        """Record a model invocation error."""
        health = self.register_model(model_name)
        health.error_count += 1
        health.total_requests += 1
        health.last_check = datetime.utcnow()

    def set_availability(self, model_name: str, available: bool):
        """Set model availability status."""
        health = self.register_model(model_name)
        health.available = available
        health.last_check = datetime.utcnow()

    def get_model_health(self, model_name: str) -> Optional[ModelHealth]:
        """Get health status for a specific model."""
        return self._models.get(model_name)

    def get_system_health(self) -> SystemHealth:
        """Get overall system health."""
        return SystemHealth(
            ollama_available=self._ollama_available,
            redis_available=self._redis_available,
            postgres_available=self._postgres_available,
            qdrant_available=self._qdrant_available,
            models=self._models.copy(),
            last_updated=datetime.utcnow(),
        )

    def update_infrastructure_health(
        self,
        ollama: bool = False,
        redis: bool = False,
        postgres: bool = False,
        qdrant: bool = False,
    ):
        """Update infrastructure component health."""
        self._ollama_available = ollama
        self._redis_available = redis
        self._postgres_available = postgres
        self._qdrant_available = qdrant
        self._last_update = datetime.utcnow()