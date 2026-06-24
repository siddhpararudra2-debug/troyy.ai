"""
Sprint 12 — API Routes
Cloud-Native Infrastructure REST API (Personal Workstation Edition)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from cloud.cluster_manager import ClusterManager, ClusterTier
from cloud.deployment_manager import DeploymentManager, DeploymentStrategy
from cloud.autoscaling_engine import AutoscalingEngine, ScalingPolicy
from distributed_agents.agent_scheduler import AgentScheduler, AgentTask, AgentCapability
from hpc.simulation_scheduler import SimulationScheduler, JobType, JobPriority
from hpc.gpu_allocator import GPUAllocator, GPUModel
from hpc.job_dispatcher import JobDispatcher
from data_platform.object_storage import ObjectStorageService, BucketPurpose
from data_platform.data_catalog import DataCatalogService, DatasetType
from data_platform.backup_manager import BackupManager, BackupType, BackupTarget
from streaming.event_bus import EventBus, EventBackend
from streaming.notification_engine import NotificationEngine, NotificationChannel, NotificationSeverity
from observability.metrics_collector import MetricsCollector
from observability.alert_manager import AlertManager, AlertSeverity
from cloud_security.secret_manager import SecretManager, SecretType
from cloud_security.certificate_manager import CertificateManager, CertificateType
from cloud_security.vulnerability_scanner import VulnerabilityScanner
from personal_platform.developer_portal import DeveloperPortal, ServiceCatalogCategory
from personal_platform.environment_manager import EnvironmentManager, EnvironmentType
from personal_platform.deployment_templates import DeploymentTemplateEngine
from cloud_core.resource_manager import ResourceManager, ResourceType
from cloud_core.health_monitor import HealthMonitor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/sprint12", tags=["Sprint 12 — Personal Infrastructure"])

# ─── Service Singletons ───────────────────────────────────────────────────────
_cluster_manager = ClusterManager()
_deployment_manager = DeploymentManager()
_autoscaling_engine = AutoscalingEngine()
_agent_scheduler = AgentScheduler()
_simulation_scheduler = SimulationScheduler()
_gpu_allocator = GPUAllocator()
_job_dispatcher = JobDispatcher()
_object_storage = ObjectStorageService()
_data_catalog = DataCatalogService()
_backup_manager = BackupManager()
_event_bus = EventBus()
_notification_engine = NotificationEngine()
_metrics_collector = MetricsCollector()
_alert_manager = AlertManager()
_secret_manager = SecretManager()
_certificate_manager = CertificateManager()
_vuln_scanner = VulnerabilityScanner()
_developer_portal = DeveloperPortal()
_environment_manager = EnvironmentManager()
_template_engine = DeploymentTemplateEngine()
_resource_manager = ResourceManager()
_health_monitor = HealthMonitor()


# ─── Pydantic Request/Response Models ────────────────────────────────────────

class CreateClusterRequest(BaseModel):
    name: str
    provider: str = "local"
    region: str = "local"
    node_count: int = Field(1, ge=1, le=10)
    cpu_per_node: int = Field(8, ge=1)
    memory_gb_per_node: float = Field(32.0, gt=0)
    tier: str = "standard"
    kubernetes_version: str = "docker-24.0"


class CreateDeploymentRequest(BaseModel):
    name: str
    service_name: str
    image: str
    image_tag: str = "latest"
    replicas: int = Field(1, ge=1)
    strategy: str = "recreate"
    cluster_id: str
    namespace: str = "default"
    env_vars: Dict[str, str] = {}
    resource_limits: Dict[str, str] = {}


class SubmitSimulationJobRequest(BaseModel):
    name: str
    job_type: str = "fea"
    cpu_cores: int = Field(4, ge=1)
    memory_gb: float = Field(16.0, gt=0)
    gpu_count: int = 0
    node_count: int = Field(1, ge=1)
    wall_time_hours: float = Field(2.0, gt=0)
    priority: str = "NORMAL"
    parameters: Dict[str, Any] = {}
    dependencies: List[str] = []
    partition: str = "compute"
    project_id: Optional[str] = None


class CreateBucketRequest(BaseModel):
    name: str
    purpose: str = "generic"
    region: str = "local"
    versioning_enabled: bool = True
    encryption_enabled: bool = False
    replication_regions: List[str] = []


class CreateAlertRuleRequest(BaseModel):
    name: str
    metric_name: str
    threshold: float
    operator: str = ">"
    severity: str = "warning"
    duration_minutes: int = 5
    description: str = ""
    notification_channels: List[str] = []


class CreateSecretRequest(BaseModel):
    name: str
    value: str
    secret_type: str = "generic"
    namespace: str = "default"
    rotation_days: Optional[int] = None
    expires_in_days: Optional[int] = None


class CreateEnvironmentRequest(BaseModel):
    name: str
    env_type: str = "development"
    team_name: str = ""
    region: str = "local"
    services: Dict[str, str] = {}
    ttl_hours: Optional[int] = None
    created_by: str = "local_user"


class ScanDependenciesRequest(BaseModel):
    packages: List[Dict[str, str]]
    target_name: str = "requirements.txt"


class SendNotificationRequest(BaseModel):
    title: str
    message: str
    recipient: str
    channel: str = "in_app"
    severity: str = "info"


class GenerateHelmChartRequest(BaseModel):
    app_name: str
    image: str
    image_tag: str = "latest"
    replicas: int = 1
    port: int = 8080
    namespace: str = "default"
    env_vars: Dict[str, str] = {}
    hpa_enabled: bool = False
    min_replicas: int = 1
    max_replicas: int = 1


# ─── MODULE 1: Cloud Orchestration ────────────────────────────────────────────

@router.post("/clusters", summary="Provision local workspace host")
async def create_cluster(req: CreateClusterRequest) -> Dict[str, Any]:
    cluster = await _cluster_manager.provision_cluster(
        name=req.name,
        region=req.region,
        node_count=req.node_count,
        cpu_per_node=req.cpu_per_node,
        memory_gb_per_node=req.memory_gb_per_node,
        tier=ClusterTier(req.tier),
        kubernetes_version=req.kubernetes_version,
    )
    return cluster.to_dict()


@router.get("/clusters", summary="List local workspace hosts")
async def list_clusters() -> List[Dict[str, Any]]:
    clusters = await _cluster_manager.list_clusters()
    return [c.to_dict() for c in clusters]


@router.get("/clusters/{cluster_id}/health", summary="Host health report")
async def get_cluster_health(cluster_id: str) -> Dict[str, Any]:
    return await _cluster_manager.generate_cluster_health_report(cluster_id)


@router.post("/deployments", summary="Start local service deployment")
async def start_deployment(req: CreateDeploymentRequest) -> Dict[str, Any]:
    record = await _deployment_manager.start_deployment(
        cluster_id=req.cluster_id,
        service_name=req.service_name,
        target_image=f"{req.image}:{req.image_tag}",
        strategy=DeploymentStrategy(req.strategy),
        namespace=req.namespace,
        replicas=req.replicas,
    )
    return record.to_dict()


# ─── MODULE 2: Distributed Agent Execution ────────────────────────────────────

@router.post("/agents/tasks", summary="Submit agent task to queue")
async def submit_agent_task(
    name: str = Body(...),
    agent_type: str = Body("generic"),
    capability: str = Body("reasoning"),
    priority: int = Body(2),
) -> Dict[str, Any]:
    spec = AgentTask(
        name=name,
        agent_type=agent_type,
        capability=AgentCapability(capability),
        priority=priority,
    )
    exec_record = await _agent_scheduler.submit_task(spec)
    return exec_record.to_dict()


@router.get("/agents/queue", summary="Get agent scheduler queue statistics")
async def agent_queue_stats() -> Dict[str, Any]:
    return await _agent_scheduler.get_queue_stats()


# ─── MODULE 3: High Performance Computing (HPC) ────────────────────────────────

@router.post("/simulation/jobs", summary="Submit local simulation job")
async def submit_simulation(req: SubmitSimulationJobRequest) -> Dict[str, Any]:
    job = await _simulation_scheduler.submit_job(
        name=req.name,
        job_type=JobType(req.job_type),
        priority=JobPriority(req.priority),
        cpu_cores=req.cpu_cores,
        memory_gb=req.memory_gb,
        gpu_count=req.gpu_count,
        parameters=req.parameters,
        project_id=req.project_id,
    )
    return job.to_dict()


@router.get("/gpus", summary="List local GPUs")
async def list_gpus(cluster_id: Optional[str] = Query(None)) -> List[Dict[str, Any]]:
    gpus = await _gpu_allocator.list_gpus(cluster_id=cluster_id)
    return [g.to_dict() for g in gpus]


# ─── MODULE 4: Data Platform ──────────────────────────────────────────────────

@router.post("/storage/buckets", summary="Create MinIO storage bucket")
async def create_bucket(req: CreateBucketRequest) -> Dict[str, Any]:
    bucket = await _object_storage.create_bucket(
        name=req.name,
        purpose=BucketPurpose(req.purpose),
        versioning_enabled=req.versioning_enabled,
        encryption_enabled=req.encryption_enabled,
    )
    return bucket.to_dict()


@router.post("/datasets", summary="Register local dataset catalog")
async def register_dataset(
    name: str = Body(...),
    bucket_name: str = Body(...),
    dataset_type: str = Body("generic"),
    project_id: Optional[str] = Body(None),
) -> Dict[str, Any]:
    ds = await _data_catalog.register_dataset(
        name=name,
        bucket_name=bucket_name,
        dataset_type=DatasetType(dataset_type),
        project_id=project_id,
    )
    return ds.to_dict()


@router.post("/backups", summary="Initiate local backup")
async def start_backup(
    name: str = Body(...),
    backup_type: str = Body("full"),
    target: str = Body("database"),
    source_location: str = Body(...),
    destination_bucket: str = Body(...),
    retention_days: int = Body(30),
) -> Dict[str, Any]:
    backup = await _backup_manager.start_backup(
        name=name,
        backup_type=BackupType(backup_type),
        target=BackupTarget(target),
        source_location=source_location,
        destination_bucket=destination_bucket,
        retention_days=retention_days,
    )
    return backup.to_dict()


@router.post("/backups/{backup_id}/verify", summary="Verify backup integrity")
async def verify_backup(backup_id: str) -> Dict[str, Any]:
    try:
        return await _backup_manager.verify_backup(backup_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/backups/summary", summary="Backup summary")
async def backup_summary() -> Dict[str, Any]:
    return await _backup_manager.get_backup_summary()


# ─── MODULE 5: Streaming ──────────────────────────────────────────────────────

@router.post("/events/topics", summary="Create event topic")
async def create_topic(
    name: str = Body(...),
    backend: str = Body("nats"),
    partitions: int = Body(1),
) -> Dict[str, Any]:
    topic = await _event_bus.create_topic(
        name=name,
        backend=EventBackend(backend),
        partitions=partitions,
    )
    return topic.to_dict()


@router.post("/events/publish", summary="Publish event")
async def publish_event(
    topic: str = Body(...),
    value: Any = Body(...),
    key: Optional[str] = Body(None),
) -> Dict[str, Any]:
    msg = await _event_bus.publish(topic=topic, value=value, key=key)
    return msg.to_dict()


@router.get("/events/bus/stats", summary="Event bus statistics")
async def event_bus_stats() -> Dict[str, Any]:
    return _event_bus.get_bus_stats()


@router.post("/notifications/send", summary="Send notification")
async def send_notification(req: SendNotificationRequest) -> Dict[str, Any]:
    record = await _notification_engine.send(
        title=req.title,
        message=req.message,
        recipient=req.recipient,
        channel=NotificationChannel(req.channel),
        severity=NotificationSeverity(req.severity),
    )
    return record.to_dict()


# ─── MODULE 6: Observability ──────────────────────────────────────────────────

@router.get("/observability/metrics", summary="Prometheus metrics snapshot")
async def get_metrics() -> Dict[str, Any]:
    return _metrics_collector.get_metrics_snapshot()


@router.get("/observability/metrics/prometheus", summary="Prometheus text format")
async def prometheus_metrics() -> str:
    return _metrics_collector.render_prometheus_text()


@router.post("/observability/alerts/rules", summary="Create alert rule")
async def create_alert_rule(req: CreateAlertRuleRequest) -> Dict[str, Any]:
    rule = await _alert_manager.create_rule(
        name=req.name,
        metric_name=req.metric_name,
        threshold=req.threshold,
        operator=req.operator,
        severity=AlertSeverity(req.severity),
        duration_minutes=req.duration_minutes,
        description=req.description,
        notification_channels=req.notification_channels,
    )
    return rule.to_dict()


# ─── MODULE 7: Local Security ──────────────────────────────────────────────────

@router.post("/security/secrets", summary="Create secret")
async def create_secret(req: CreateSecretRequest) -> Dict[str, Any]:
    secret = await _secret_manager.store_secret(
        name=req.name,
        value=req.value,
        secret_type=SecretType(req.secret_type),
        namespace=req.namespace,
        rotation_days=req.rotation_days,
        expires_in_days=req.expires_in_days,
    )
    return secret.to_dict()


@router.get("/security/report", summary="Security report for local workstation")
async def security_report() -> Dict[str, Any]:
    return await _vuln_scanner.generate_security_report()


# ─── MODULE 9: Platform Engineering ──────────────────────────────────────────

@router.get("/platform/catalog", summary="Browse service catalog")
async def browse_catalog(
    query: str = Query(""),
    category: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    items = await _developer_portal.search_catalog(
        query=query,
        category=ServiceCatalogCategory(category) if category else None,
    )
    return [i.to_dict() for i in items]


@router.post("/platform/provision", summary="Request self-service provisioning")
async def provision_resource(
    catalog_item_id: str = Body(...),
    requested_by: str = Body("local_user"),
    parameters: Dict[str, Any] = Body({}),
) -> Dict[str, Any]:
    try:
        req = await _developer_portal.request_provisioning(
            catalog_item_id=catalog_item_id,
            requested_by=requested_by,
            parameters=parameters,
        )
        return req.to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/platform/environments", summary="Create environment")
async def create_environment(req: CreateEnvironmentRequest) -> Dict[str, Any]:
    env = await _environment_manager.create_environment(
        name=req.name,
        env_type=EnvironmentType(req.env_type),
        services=list(req.services.keys()),
        config=req.services,
    )
    return env.to_dict()


@router.get("/platform/environments", summary="List environments")
async def list_environments(
    env_type: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    envs = await _environment_manager.list_environments(
        env_type=EnvironmentType(env_type) if env_type else None,
    )
    return [e.to_dict() for e in envs]


@router.post("/platform/templates/compose", summary="Generate Docker Compose")
async def generate_docker_compose(req: GenerateHelmChartRequest) -> Dict[str, str]:
    content = _template_engine.generate_docker_compose(
        app_name=req.app_name,
        image=req.image,
        image_tag=req.image_tag,
        port=req.port,
        env_vars=req.env_vars,
    )
    return {"docker-compose.yml": content}


# ─── MODULE 10: Cloud Core ────────────────────────────────────────────────────

@router.get("/resources/platform/summary", summary="Platform resource summary")
async def platform_summary() -> Dict[str, Any]:
    return _resource_manager.get_platform_summary()


@router.get("/health", summary="Sprint 12 platform health check")
async def platform_health() -> Dict[str, Any]:
    return await _health_monitor.get_platform_health()


@router.get("/health/status-page", summary="Public status page")
async def status_page() -> Dict[str, Any]:
    return await _health_monitor.generate_status_page()


@router.post("/health/check-all", summary="Run all service health checks")
async def run_all_health_checks() -> Dict[str, Any]:
    records = await _health_monitor.check_all_services()
    return {
        "total_services": len(records),
        "results": {name: rec.to_dict() for name, rec in records.items()},
    }


# ─── AGGREGATE ────────────────────────────────────────────────────────────────

@router.get("/overview", summary="Sprint 12 full platform overview")
async def sprint12_overview() -> Dict[str, Any]:
    """Aggregated overview of all Sprint 12 systems."""
    health = await _health_monitor.get_platform_health()
    clusters = await _cluster_manager.list_clusters()
    jobs = await _simulation_scheduler.list_jobs()

    return {
        "sprint": "Sprint 12 — Personal Infrastructure",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform_health": health["overall_status"],
        "sla_pct": health.get("platform_sla", 100.0),
        "modules": {
            "cloud_orchestration": {
                "clusters": len(clusters),
                "status": "operational",
            },
            "distributed_agents": (await _agent_scheduler.get_queue_status()),
            "hpc": {
                "jobs": len(jobs),
                "queue_stats": await _simulation_scheduler.get_queue_depth(),
            },
            "data_platform": await _object_storage.get_storage_stats(),
            "event_streaming": _event_bus.get_bus_stats(),
            "observability": _metrics_collector.get_collector_summary(),
            "cloud_security": _secret_manager.get_secret_summary(),
            "global_infrastructure": {
                "regions": 1,
                "active": 1,
            },
            "platform_engineering": _developer_portal.get_portal_stats(),
            "cloud_core": _resource_manager.get_platform_summary(),
        },
    }
