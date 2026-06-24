"""
Sprint 12 — Database Models
SQLAlchemy models for Personal Infrastructure Platform
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database.models import Base, TimestampMixin


# ─── Module 1: Personal Infrastructure ───────────────────────────────────────

class DockerHostModel(Base, TimestampMixin):
    __tablename__ = "sprint12_docker_hosts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="running")
    docker_version = Column(String(50), nullable=False, default="24.0.7")
    host_endpoint = Column(String(500), default="unix:///var/run/docker.sock")
    container_count = Column(Integer, default=0)
    total_cpu_cores = Column(Integer, default=8)
    total_memory_gb = Column(Float, default=32.0)
    host_metadata = Column(JSON, default=dict)
    labels = Column(JSON, default=dict)
    tags = Column(JSON, default=dict)

    deployments = relationship("DeploymentRecordModel", back_populates="docker_host", cascade="all, delete-orphan")


class DeploymentRecordModel(Base, TimestampMixin):
    __tablename__ = "sprint12_deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    service_name = Column(String(255), nullable=False)
    image = Column(String(500), nullable=False)
    image_tag = Column(String(100), nullable=False, default="latest")
    replicas = Column(Integer, default=1)
    strategy = Column(String(50), default="recreate")
    status = Column(String(50), nullable=False, default="pending")
    container_name = Column(String(255))
    docker_host_id = Column(UUID(as_uuid=True), ForeignKey("sprint12_docker_hosts.id", ondelete="CASCADE"))
    project_id = Column(String(255))
    config = Column(JSON, default=dict)
    resource_limits = Column(JSON, default=dict)
    health_check_url = Column(String(500))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    docker_host = relationship("DockerHostModel", back_populates="deployments")


# ─── Module 3: HPC (Local Simulation Queue) ───────────────────────────────────

class SimulationJobModel(Base, TimestampMixin):
    __tablename__ = "sprint12_simulation_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    job_type = Column(String(50), nullable=False, default="fea")
    priority = Column(String(20), nullable=False, default="NORMAL")
    status = Column(String(50), nullable=False, default="pending")
    project_id = Column(String(255))
    cpu_cores = Column(Integer, default=4)
    memory_gb = Column(Float, default=16.0)
    gpu_count = Column(Integer, default=0)
    parameters = Column(JSON, default=dict)
    dependencies = Column(JSON, default=list)
    worker_id = Column(String(255))
    progress_percent = Column(Float, default=0.0)
    result_path = Column(String(1000))
    error_message = Column(Text)
    queued_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    tags = Column(JSON, default=dict)


class GPUAllocationModel(Base, TimestampMixin):
    __tablename__ = "sprint12_gpu_allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(255), nullable=False, index=True)
    gpu_ids = Column(JSON, default=list)
    gpu_count = Column(Integer, nullable=False)
    gpu_model = Column(String(100), default="NVIDIA GeForce RTX 4090")
    status = Column(String(50), default="allocated")
    allocated_at = Column(DateTime(timezone=True))
    released_at = Column(DateTime(timezone=True))


# ─── Module 4: Data Platform (Local Object Storage) ──────────────────────────

class StorageBucketModel(Base, TimestampMixin):
    __tablename__ = "sprint12_storage_buckets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    purpose = Column(String(50), default="generic")
    versioning_enabled = Column(Boolean, default=True)
    encryption_enabled = Column(Boolean, default=False)
    lifecycle_rules = Column(JSON, default=list)
    object_count = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    tags = Column(JSON, default=dict)


class DatasetModel(Base, TimestampMixin):
    __tablename__ = "sprint12_datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    dataset_type = Column(String(50), default="generic")
    status = Column(String(50), default="draft")
    owner = Column(String(255), nullable=False)
    project_id = Column(String(255))
    bucket_name = Column(String(255), nullable=False)
    key_prefix = Column(String(500))
    tags = Column(JSON, default=list)
    labels = Column(JSON, default=dict)
    schema_definition = Column(JSON, default=dict)
    lineage_parents = Column(JSON, default=list)
    lineage_children = Column(JSON, default=list)
    version_count = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True))


class BackupRecordModel(Base, TimestampMixin):
    __tablename__ = "sprint12_backup_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    backup_type = Column(String(50), default="full")
    target = Column(String(50), default="database")
    status = Column(String(50), default="pending")
    source_location = Column(String(500))
    destination_bucket = Column(String(255))
    destination_key = Column(String(1000))
    size_bytes = Column(Integer, default=0)
    checksum = Column(String(255))
    retention_days = Column(Integer, default=30)
    encrypted = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    schedule_id = Column(String(255))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    error_message = Column(Text)


# ─── Module 5: Streaming (Local NATS Messaging) ───────────────────────────────

class EventTopicModel(Base, TimestampMixin):
    __tablename__ = "sprint12_event_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    backend = Column(String(50), default="nats")
    partitions = Column(Integer, default=1)
    replication_factor = Column(Integer, default=1)
    retention_hours = Column(Integer, default=24)
    compaction_enabled = Column(Boolean, default=False)
    message_count = Column(Integer, default=0)


# ─── Module 6: Observability (Local Stack) ────────────────────────────────────

class AlertRuleModel(Base, TimestampMixin):
    __tablename__ = "sprint12_alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    metric_name = Column(String(255), nullable=False)
    condition_type = Column(String(50), default="threshold")
    threshold = Column(Float, nullable=False)
    operator = Column(String(10), default=">")
    duration_minutes = Column(Integer, default=5)
    severity = Column(String(20), default="warning")
    enabled = Column(Boolean, default=True)
    notification_channels = Column(JSON, default=list)
    labels = Column(JSON, default=dict)
    annotations = Column(JSON, default=dict)


class AlertEventModel(Base, TimestampMixin):
    __tablename__ = "sprint12_alert_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("sprint12_alert_rules.id"))
    rule_name = Column(String(255), nullable=False)
    status = Column(String(50), default="firing")
    severity = Column(String(20), nullable=False)
    metric_name = Column(String(255))
    current_value = Column(Float)
    threshold = Column(Float)
    fingerprint = Column(String(255))
    fired_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True))
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime(timezone=True))


# ─── Module 7: Local Security ──────────────────────────────────────────────────

class SecretRecordModel(Base, TimestampMixin):
    __tablename__ = "sprint12_secrets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    secret_type = Column(String(50), default="generic")
    version = Column(Integer, default=1)
    status = Column(String(50), default="active")
    last_rotated_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    tags = Column(JSON, default=dict)
    vault_path = Column(String(500))


class CertificateModel(Base, TimestampMixin):
    __tablename__ = "sprint12_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    common_name = Column(String(255), nullable=False, index=True)
    san_domains = Column(JSON, default=list)
    certificate_type = Column(String(50), default="tls")
    status = Column(String(50), default="issued")
    issuer = Column(String(255), default="Local CA")
    serial_number = Column(String(255))
    fingerprint = Column(String(255))
    auto_renew = Column(Boolean, default=True)
    renewal_threshold_days = Column(Integer, default=30)
    issued_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))


# ─── Module 9: Local Workstation Platforms ────────────────────────────────────

class EnvironmentModel(Base, TimestampMixin):
    __tablename__ = "sprint12_environments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    env_type = Column(String(50), default="development")
    status = Column(String(50), default="running")
    services = Column(JSON, default=dict)
    config = Column(JSON, default=dict)
    ttl_hours = Column(Integer)
    created_by = Column(String(255))
    last_accessed = Column(DateTime(timezone=True))


class ProvisioningRequestModel(Base, TimestampMixin):
    __tablename__ = "sprint12_provisioning_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    catalog_item_id = Column(String(255), nullable=False)
    catalog_item_name = Column(String(255), nullable=False)
    requested_by = Column(String(255), nullable=False)
    parameters = Column(JSON, default=dict)
    status = Column(String(50), default="completed")
    provisioned_resource_id = Column(String(255))
    completed_at = Column(DateTime(timezone=True))
