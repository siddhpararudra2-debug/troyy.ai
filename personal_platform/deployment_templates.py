"""
Sprint 12 — Personal Deployment Templates
Docker Compose template generation for self-service personal provisioning.
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TemplateType(str, Enum):
    DOCKER_COMPOSE = "docker_compose"
    DOCKERFILE = "dockerfile"
    LOCAL_CONFIG = "local_config"


@dataclass
class DeploymentTemplate:
    """A reusable local deployment template."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template_type: TemplateType = TemplateType.DOCKER_COMPOSE
    description: str = ""
    version: str = "1.0.0"
    parameters: Dict[str, Any] = field(default_factory=dict)
    content: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "template_type": self.template_type.value,
            "description": self.description,
            "version": self.version,
            "parameters": self.parameters,
        }


class DeploymentTemplateEngine:
    """
    Generates Docker Compose configuration files for local deployments.
    """

    def __init__(self):
        self._templates: Dict[str, DeploymentTemplate] = {}

    def generate_docker_compose(
        self,
        app_name: str,
        image: str,
        image_tag: str = "latest",
        port: int = 8080,
        env_vars: Optional[Dict[str, str]] = None,
        include_db: bool = True,
        include_redis: bool = True,
        include_minio: bool = True,
        include_nats: bool = True,
        include_neo4j: bool = False,
    ) -> str:
        """Generate a complete docker-compose.yml file for local workstation deployment."""
        
        services = {}
        
        # Main application service
        app_env = {
            "DATABASE_URL": "postgresql://postgres:postgres@db:5432/engineering_os",
            "REDIS_URL": "redis://redis:6379/0",
            "MINIO_ENDPOINT": "minio:9000",
            "NATS_URL": "nats://nats:4222",
            **(env_vars or {})
        }
        
        app_env_str = "\n".join(f"      - {k}={v}" for k, v in app_env.items())
        
        services[app_name] = f"""  {app_name}:
    image: {image}:{image_tag}
    ports:
      - "{port}:{port}"
    environment:
{app_env_str}
    depends_on:
"""
        if include_db:
            services[app_name] += "      - db\n"
        if include_redis:
            services[app_name] += "      - redis\n"
        if include_minio:
            services[app_name] += "      - minio\n"
        if include_nats:
            services[app_name] += "      - nats\n"
        
        services[app_name] += "    restart: always"

        # Dependencies services
        if include_db:
            services["db"] = """  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=engineering_os
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: always"""

        if include_redis:
            services["redis"] = """  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: always"""

        if include_minio:
            services["minio"] = """  minio:
    image: minio/minio:RELEASE.2024-01-28T22-35-50Z
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - miniodata:/data
    restart: always"""

        if include_nats:
            services["nats"] = """  nats:
    image: nats:2.10-alpine
    ports:
      - "4222:4222"
      - "8222:8222"
    restart: always"""

        if include_neo4j:
            services["neo4j"] = """  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4jdata:/data
    restart: always"""

        services_block = "\n\n".join(services.values())
        
        compose_file = f"""version: '3.8'

services:
{services_block}

volumes:
  pgdata:
  miniodata:
  neo4jdata:
"""
        logger.info(f"Docker Compose generated for '{app_name}'")
        return compose_file

    def get_template_summary(self) -> Dict[str, Any]:
        return {
            "available_template_types": [t.value for t in TemplateType],
            "registered_templates": len(self._templates),
        }
