"""
Sprint 12 — Environment Manager
Manages local environments and workspaces via Docker Compose.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    SIMULATION = "simulation"
    TESTING = "testing"


@dataclass
class LocalEnvironment:
    """Represents a local Docker Compose environment."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    env_type: EnvironmentType = EnvironmentType.DEVELOPMENT
    status: str = "provisioning"
    services: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "env_type": self.env_type.value,
            "status": self.status,
            "services": self.services,
            "config": self.config,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
        }


class EnvironmentManager:
    """
    Manages local Docker-based workstation environments for calculations, simulations, and agents.
    """

    def __init__(self):
        self._environments: Dict[str, LocalEnvironment] = {}

    async def create_environment(
        self,
        name: str,
        env_type: EnvironmentType = EnvironmentType.DEVELOPMENT,
        services: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> LocalEnvironment:
        """Create and start a local docker compose environment."""
        env = LocalEnvironment(
            name=name,
            env_type=env_type,
            services=services or ["db", "redis", "minio", "nats"],
            config=config or {},
            status="running",
        )
        self._environments[env.id] = env
        logger.info(f"Local environment '{name}' started successfully with services: {env.services}")
        return env

    async def get_environment(self, env_id: str) -> Optional[LocalEnvironment]:
        env = self._environments.get(env_id)
        if env:
            env.last_accessed = datetime.now(timezone.utc)
        return env

    async def delete_environment(self, env_id: str) -> bool:
        if env_id in self._environments:
            env = self._environments[env_id]
            env.status = "terminated"
            del self._environments[env_id]
            logger.info(f"Local environment '{env.name}' stopped and removed.")
            return True
        return False

    async def list_environments(self, env_type: Optional[EnvironmentType] = None) -> List[LocalEnvironment]:
        envs = list(self._environments.values())
        if env_type:
            envs = [e for e in envs if e.env_type == env_type]
        return envs

    def get_manager_stats(self) -> Dict[str, Any]:
        envs = list(self._environments.values())
        return {
            "total_environments": len(envs),
            "running_environments": sum(1 for e in envs if e.status == "running"),
            "services_count": sum(len(e.services) for e in envs),
        }
