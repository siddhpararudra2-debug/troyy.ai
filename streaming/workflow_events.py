"""
Sprint 12 — Workflow Events
Engineering workflow event definitions and schema registry.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class WorkflowEventType(str, Enum):
    # Agent events
    AGENT_SUBMITTED = "agent.submitted"
    AGENT_SCHEDULED = "agent.scheduled"
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_CANCELLED = "agent.cancelled"
    # Job events
    JOB_SUBMITTED = "job.submitted"
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_PROGRESS = "job.progress"
    # Cluster events
    CLUSTER_CREATED = "cluster.created"
    CLUSTER_SCALED = "cluster.scaled"
    CLUSTER_DELETED = "cluster.deleted"
    NODE_FAILED = "node.failed"
    # Deployment events
    DEPLOYMENT_STARTED = "deployment.started"
    DEPLOYMENT_COMPLETED = "deployment.completed"
    DEPLOYMENT_FAILED = "deployment.failed"
    DEPLOYMENT_ROLLED_BACK = "deployment.rolled_back"
    # Storage events
    BUCKET_CREATED = "storage.bucket_created"
    OBJECT_UPLOADED = "storage.object_uploaded"
    BACKUP_COMPLETED = "storage.backup_completed"
    ARCHIVE_COMPLETED = "storage.archive_completed"
    # Alert events
    ALERT_FIRED = "alert.fired"
    ALERT_RESOLVED = "alert.resolved"
    # Security events
    SECRET_ROTATED = "security.secret_rotated"
    CERTIFICATE_RENEWED = "security.certificate_renewed"
    VULNERABILITY_DETECTED = "security.vulnerability_detected"
    # Region events
    REGION_DEPLOYED = "region.deployed"
    FAILOVER_INITIATED = "region.failover_initiated"
    FAILOVER_COMPLETED = "region.failover_completed"


@dataclass
class WorkflowEvent:
    """A standardized engineering workflow event."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: WorkflowEventType = WorkflowEventType.AGENT_SUBMITTED
    source_service: str = ""
    tenant_id: str = "default"
    project_id: Optional[str] = None
    entity_id: str = ""
    entity_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    version: str = "1.0"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "source_service": self.source_service,
            "tenant_id": self.tenant_id,
            "project_id": self.project_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "payload": self.payload,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def agent_submitted(cls, agent_id: str, agent_name: str, tenant_id: str, **payload) -> "WorkflowEvent":
        return cls(
            event_type=WorkflowEventType.AGENT_SUBMITTED,
            source_service="agent_scheduler",
            tenant_id=tenant_id,
            entity_id=agent_id,
            entity_type="agent",
            payload={"agent_name": agent_name, **payload},
        )

    @classmethod
    def job_completed(cls, job_id: str, job_name: str, tenant_id: str, result_path: str = "", **payload) -> "WorkflowEvent":
        return cls(
            event_type=WorkflowEventType.JOB_COMPLETED,
            source_service="hpc_scheduler",
            tenant_id=tenant_id,
            entity_id=job_id,
            entity_type="hpc_job",
            payload={"job_name": job_name, "result_path": result_path, **payload},
        )

    @classmethod
    def deployment_completed(cls, deployment_id: str, service: str, tenant_id: str, **payload) -> "WorkflowEvent":
        return cls(
            event_type=WorkflowEventType.DEPLOYMENT_COMPLETED,
            source_service="deployment_manager",
            tenant_id=tenant_id,
            entity_id=deployment_id,
            entity_type="deployment",
            payload={"service": service, **payload},
        )

    @classmethod
    def alert_fired(cls, alert_id: str, alert_name: str, severity: str, tenant_id: str, **payload) -> "WorkflowEvent":
        return cls(
            event_type=WorkflowEventType.ALERT_FIRED,
            source_service="alert_manager",
            tenant_id=tenant_id,
            entity_id=alert_id,
            entity_type="alert",
            payload={"alert_name": alert_name, "severity": severity, **payload},
        )


class WorkflowEventRegistry:
    """Registry of workflow event schemas and event factory."""

    TOPIC_MAP: Dict[WorkflowEventType, str] = {
        WorkflowEventType.AGENT_SUBMITTED: "engineering.agents",
        WorkflowEventType.AGENT_COMPLETED: "engineering.agents",
        WorkflowEventType.AGENT_FAILED: "engineering.agents.dlq",
        WorkflowEventType.JOB_SUBMITTED: "engineering.hpc.jobs",
        WorkflowEventType.JOB_COMPLETED: "engineering.hpc.jobs",
        WorkflowEventType.JOB_FAILED: "engineering.hpc.jobs.dlq",
        WorkflowEventType.DEPLOYMENT_STARTED: "engineering.deployments",
        WorkflowEventType.DEPLOYMENT_COMPLETED: "engineering.deployments",
        WorkflowEventType.ALERT_FIRED: "engineering.alerts",
        WorkflowEventType.ALERT_RESOLVED: "engineering.alerts",
        WorkflowEventType.CLUSTER_CREATED: "engineering.infrastructure",
        WorkflowEventType.NODE_FAILED: "engineering.infrastructure.failures",
        WorkflowEventType.BACKUP_COMPLETED: "engineering.storage",
        WorkflowEventType.VULNERABILITY_DETECTED: "engineering.security",
        WorkflowEventType.FAILOVER_INITIATED: "engineering.dr",
        WorkflowEventType.FAILOVER_COMPLETED: "engineering.dr",
    }

    def __init__(self):
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self._event_log: List[WorkflowEvent] = []
        self._register_default_schemas()

    def _register_default_schemas(self) -> None:
        """Register default event schemas."""
        self._schemas[WorkflowEventType.AGENT_SUBMITTED.value] = {
            "required": ["agent_id", "agent_name", "tenant_id"],
            "optional": ["priority", "capability", "payload"],
        }
        self._schemas[WorkflowEventType.JOB_COMPLETED.value] = {
            "required": ["job_id", "job_name", "result_path"],
            "optional": ["duration_seconds", "cpu_hours"],
        }
        self._schemas[WorkflowEventType.ALERT_FIRED.value] = {
            "required": ["alert_id", "alert_name", "severity"],
            "optional": ["metric_value", "threshold"],
        }

    def get_topic_for_event(self, event_type: WorkflowEventType) -> str:
        """Get the Kafka/NATS topic for an event type."""
        return self.TOPIC_MAP.get(event_type, "engineering.events.generic")

    def all_topics(self) -> List[str]:
        """Get all unique topics used by workflow events."""
        return list(set(self.TOPIC_MAP.values()))

    def register_event(self, event: WorkflowEvent) -> None:
        """Record an event in the log."""
        self._event_log.append(event)

    def get_event_log(
        self,
        event_type: Optional[WorkflowEventType] = None,
        tenant_id: Optional[str] = None,
        limit: int = 200,
    ) -> List[WorkflowEvent]:
        events = self._event_log[-limit:]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]
        return events

    def get_schema(self, event_type: str) -> Optional[Dict[str, Any]]:
        return self._schemas.get(event_type)

    def get_registry_summary(self) -> Dict[str, Any]:
        return {
            "registered_schemas": len(self._schemas),
            "event_types": len(WorkflowEventType),
            "topics": len(self.all_topics()),
            "events_logged": len(self._event_log),
        }
