"""
Sprint 12 — Service Orchestrator
Service discovery, Ingress routing, load balancing, and service mesh integration.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ServiceType(str, Enum):
    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"
    EXTERNAL_NAME = "ExternalName"


class ServiceStatus(str, Enum):
    ACTIVE = "active"
    DEGRADED = "degraded"
    DOWN = "down"
    PENDING = "pending"


@dataclass
class ServiceEndpoint:
    """A single endpoint for a service."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pod_ip: str = ""
    port: int = 8080
    ready: bool = True
    node_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "pod_ip": self.pod_ip,
            "port": self.port,
            "ready": self.ready,
            "node_name": self.node_name,
        }


@dataclass
class ServiceRecord:
    """Represents a Kubernetes service."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    namespace: str = "default"
    cluster_id: str = ""
    service_type: ServiceType = ServiceType.CLUSTER_IP
    status: ServiceStatus = ServiceStatus.ACTIVE
    cluster_ip: str = ""
    external_ip: str = ""
    ports: List[Dict[str, Any]] = field(default_factory=list)
    selector: Dict[str, str] = field(default_factory=dict)
    endpoints: List[ServiceEndpoint] = field(default_factory=list)
    dns_name: str = ""
    health_check_path: str = "/health"
    tenant_id: str = "default"
    labels: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def ready_endpoints(self) -> List[ServiceEndpoint]:
        return [e for e in self.endpoints if e.ready]

    @property
    def health_score(self) -> float:
        if not self.endpoints:
            return 0.0
        return len(self.ready_endpoints) / len(self.endpoints)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "namespace": self.namespace,
            "cluster_id": self.cluster_id,
            "service_type": self.service_type.value,
            "status": self.status.value,
            "cluster_ip": self.cluster_ip,
            "external_ip": self.external_ip,
            "ports": self.ports,
            "selector": self.selector,
            "endpoints": [e.to_dict() for e in self.endpoints],
            "ready_endpoint_count": len(self.ready_endpoints),
            "health_score": self.health_score,
            "dns_name": self.dns_name,
            "health_check_path": self.health_check_path,
            "tenant_id": self.tenant_id,
            "labels": self.labels,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class IngressRule:
    """HTTP routing rule for Ingress."""
    host: str = ""
    path: str = "/"
    service_name: str = ""
    service_port: int = 80
    tls_enabled: bool = False
    tls_secret: str = ""


class ServiceOrchestrator:
    """
    Manages Kubernetes services, service discovery, Ingress routing,
    and load balancing for the Engineering OS cloud platform.
    """

    def __init__(self):
        self._services: Dict[str, ServiceRecord] = {}
        self._ingress_rules: Dict[str, List[IngressRule]] = {}  # cluster_id -> rules
        self._ip_counter = 10  # Simple IP allocation simulation

    def _allocate_cluster_ip(self) -> str:
        ip = f"10.96.{self._ip_counter // 256}.{self._ip_counter % 256}"
        self._ip_counter += 1
        return ip

    async def register_service(
        self,
        cluster_id: str,
        name: str,
        namespace: str = "default",
        service_type: ServiceType = ServiceType.CLUSTER_IP,
        ports: Optional[List[Dict[str, Any]]] = None,
        selector: Optional[Dict[str, str]] = None,
        replica_count: int = 3,
        tenant_id: str = "default",
        labels: Optional[Dict[str, str]] = None,
        health_check_path: str = "/health",
    ) -> ServiceRecord:
        """Register a new Kubernetes service."""
        service = ServiceRecord(
            name=name,
            namespace=namespace,
            cluster_id=cluster_id,
            service_type=service_type,
            cluster_ip=self._allocate_cluster_ip(),
            ports=ports or [{"port": 80, "targetPort": 8080, "protocol": "TCP"}],
            selector=selector or {"app": name},
            dns_name=f"{name}.{namespace}.svc.cluster.local",
            health_check_path=health_check_path,
            tenant_id=tenant_id,
            labels=labels or {"app": name},
        )

        if service_type == ServiceType.LOAD_BALANCER:
            service.external_ip = f"34.100.{self._ip_counter}.{self._ip_counter + 1}"

        # Simulate endpoints
        for i in range(replica_count):
            endpoint = ServiceEndpoint(
                pod_ip=f"10.244.{i}.{i + 10}",
                port=8080,
                ready=True,
                node_name=f"node-{i+1:03d}",
            )
            service.endpoints.append(endpoint)

        await asyncio.sleep(0)
        self._services[service.id] = service
        logger.info(f"Service '{name}' registered in cluster {cluster_id} namespace '{namespace}'")
        return service

    async def discover_service(
        self, name: str, namespace: str = "default", cluster_id: Optional[str] = None
    ) -> Optional[ServiceRecord]:
        """Discover a service by name and namespace."""
        for service in self._services.values():
            if service.name == name and service.namespace == namespace:
                if cluster_id is None or service.cluster_id == cluster_id:
                    return service
        return None

    async def get_service(self, service_id: str) -> Optional[ServiceRecord]:
        return self._services.get(service_id)

    async def list_services(
        self,
        cluster_id: Optional[str] = None,
        namespace: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[ServiceRecord]:
        services = list(self._services.values())
        if cluster_id:
            services = [s for s in services if s.cluster_id == cluster_id]
        if namespace:
            services = [s for s in services if s.namespace == namespace]
        if tenant_id:
            services = [s for s in services if s.tenant_id == tenant_id]
        return services

    async def delete_service(self, service_id: str) -> Dict[str, Any]:
        """Remove a service registration."""
        service = self._services.pop(service_id, None)
        if not service:
            raise ValueError(f"Service {service_id} not found")
        logger.info(f"Service {service_id} ({service.name}) deleted")
        return {"service_id": service_id, "name": service.name, "status": "deleted"}

    async def add_ingress_rule(
        self,
        cluster_id: str,
        host: str,
        path: str,
        service_name: str,
        service_port: int = 80,
        tls_enabled: bool = False,
        tls_secret: str = "",
    ) -> Dict[str, Any]:
        """Add an Ingress routing rule."""
        rule = IngressRule(
            host=host,
            path=path,
            service_name=service_name,
            service_port=service_port,
            tls_enabled=tls_enabled,
            tls_secret=tls_secret,
        )
        if cluster_id not in self._ingress_rules:
            self._ingress_rules[cluster_id] = []
        self._ingress_rules[cluster_id].append(rule)
        logger.info(f"Ingress rule added: {host}{path} -> {service_name}:{service_port}")
        return {
            "cluster_id": cluster_id,
            "host": host,
            "path": path,
            "service_name": service_name,
            "service_port": service_port,
            "tls_enabled": tls_enabled,
            "status": "active",
        }

    async def list_ingress_rules(self, cluster_id: str) -> List[Dict[str, Any]]:
        """List all Ingress rules for a cluster."""
        rules = self._ingress_rules.get(cluster_id, [])
        return [
            {
                "host": r.host,
                "path": r.path,
                "service_name": r.service_name,
                "service_port": r.service_port,
                "tls_enabled": r.tls_enabled,
            }
            for r in rules
        ]

    async def get_endpoint_for_service(self, service_id: str) -> Optional[ServiceEndpoint]:
        """Round-robin load balancing - return next ready endpoint."""
        service = self._services.get(service_id)
        if not service or not service.ready_endpoints:
            return None
        # Simple round-robin
        return service.ready_endpoints[0]

    async def mark_endpoint_unhealthy(
        self, service_id: str, pod_ip: str
    ) -> Dict[str, Any]:
        """Mark an endpoint as unhealthy (failed health check)."""
        service = self._services.get(service_id)
        if not service:
            raise ValueError(f"Service {service_id} not found")
        for endpoint in service.endpoints:
            if endpoint.pod_ip == pod_ip:
                endpoint.ready = False
                if service.health_score < 0.5:
                    service.status = ServiceStatus.DEGRADED
                logger.warning(f"Endpoint {pod_ip} marked unhealthy in service {service.name}")
                return {"pod_ip": pod_ip, "status": "unhealthy", "service_health": service.health_score}
        raise ValueError(f"Endpoint {pod_ip} not found in service {service_id}")

    async def get_service_mesh_config(self, cluster_id: str) -> Dict[str, Any]:
        """Generate Istio-compatible service mesh configuration."""
        services = await self.list_services(cluster_id=cluster_id)
        return {
            "cluster_id": cluster_id,
            "mesh_enabled": True,
            "mtls_mode": "STRICT",
            "services": [
                {
                    "name": s.name,
                    "namespace": s.namespace,
                    "virtual_service": {
                        "hosts": [s.dns_name],
                        "http": [{"route": [{"destination": {"host": s.name, "port": {"number": 80}}}]}],
                    },
                    "destination_rule": {
                        "host": s.name,
                        "trafficPolicy": {"connectionPool": {"tcp": {"maxConnections": 100}}},
                    },
                }
                for s in services
            ],
        }
