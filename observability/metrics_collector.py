"""
Sprint 12 — Metrics Collector
Prometheus metrics exposition with custom engineering metrics.
"""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricSample:
    """A single metric observation."""
    name: str = ""
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "labels": self.labels,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
        }


@dataclass
class MetricDefinition:
    """Defines a metric including type, help text, and buckets."""
    name: str = ""
    metric_type: MetricType = MetricType.GAUGE
    help_text: str = ""
    unit: str = ""
    label_names: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
    samples: List[MetricSample] = field(default_factory=list)
    current_value: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "help": self.help_text,
            "unit": self.unit,
            "label_names": self.label_names,
            "current_value": self.current_value,
            "sample_count": len(self.samples),
        }


class MetricsCollector:
    """
    Prometheus-compatible metrics collector for the Engineering OS.
    Exposes counters, gauges, histograms for cloud infrastructure and agents.
    """

    def __init__(self, namespace: str = "engineering_os"):
        self._namespace = namespace
        self._metrics: Dict[str, MetricDefinition] = {}
        self._scrape_endpoint = "/metrics"
        self._register_default_metrics()

    def _register_default_metrics(self) -> None:
        """Register standard engineering OS metrics."""
        defaults = [
            ("cluster_nodes_total", MetricType.GAUGE, "Total Kubernetes nodes", ["cluster", "region"]),
            ("cluster_cpu_utilization", MetricType.GAUGE, "CPU utilization per cluster", ["cluster"]),
            ("cluster_memory_utilization", MetricType.GAUGE, "Memory utilization per cluster", ["cluster"]),
            ("agent_tasks_total", MetricType.COUNTER, "Total agent tasks submitted", ["tenant", "capability"]),
            ("agent_tasks_running", MetricType.GAUGE, "Currently running agent tasks", ["tenant"]),
            ("hpc_jobs_total", MetricType.COUNTER, "Total HPC jobs submitted", ["job_type", "partition"]),
            ("hpc_job_duration_seconds", MetricType.HISTOGRAM, "HPC job duration", ["job_type"]),
            ("gpu_utilization", MetricType.GAUGE, "GPU utilization percent", ["node", "gpu_model"]),
            ("storage_bytes_total", MetricType.GAUGE, "Total storage used", ["tenant", "bucket_purpose"]),
            ("event_messages_total", MetricType.COUNTER, "Total messages published", ["topic"]),
            ("api_requests_total", MetricType.COUNTER, "Total API requests", ["endpoint", "method", "status"]),
            ("api_request_duration_seconds", MetricType.HISTOGRAM, "API request duration", ["endpoint"]),
            ("deployment_total", MetricType.COUNTER, "Total deployments", ["strategy", "status"]),
            ("backup_size_bytes", MetricType.GAUGE, "Backup size in bytes", ["tenant", "target"]),
            ("active_regions", MetricType.GAUGE, "Number of active regions", []),
        ]
        for name, mtype, help_text, labels in defaults:
            self._register_metric(name, mtype, help_text, labels)

    def _register_metric(
        self, name: str, metric_type: MetricType, help_text: str, label_names: List[str] = None
    ) -> MetricDefinition:
        full_name = f"{self._namespace}_{name}"
        metric = MetricDefinition(
            name=full_name,
            metric_type=metric_type,
            help_text=help_text,
            label_names=label_names or [],
        )
        self._metrics[full_name] = metric
        return metric

    def counter_inc(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
        tenant_id: str = "default",
    ) -> None:
        """Increment a counter metric."""
        full_name = f"{self._namespace}_{name}" if not name.startswith(self._namespace) else name
        if full_name not in self._metrics:
            self._register_metric(name, MetricType.COUNTER, f"Auto-registered: {name}")
        metric = self._metrics[full_name]
        metric.current_value += value
        metric.samples.append(MetricSample(
            name=full_name, value=metric.current_value, labels=labels or {}, tenant_id=tenant_id
        ))

    def gauge_set(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        tenant_id: str = "default",
    ) -> None:
        """Set a gauge metric value."""
        full_name = f"{self._namespace}_{name}" if not name.startswith(self._namespace) else name
        if full_name not in self._metrics:
            self._register_metric(name, MetricType.GAUGE, f"Auto-registered: {name}")
        metric = self._metrics[full_name]
        metric.current_value = value
        metric.samples.append(MetricSample(
            name=full_name, value=value, labels=labels or {}, tenant_id=tenant_id
        ))

    def histogram_observe(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        tenant_id: str = "default",
    ) -> None:
        """Record a histogram observation."""
        full_name = f"{self._namespace}_{name}" if not name.startswith(self._namespace) else name
        if full_name not in self._metrics:
            self._register_metric(name, MetricType.HISTOGRAM, f"Auto-registered: {name}")
        metric = self._metrics[full_name]
        metric.samples.append(MetricSample(
            name=full_name, value=value, labels=labels or {}, tenant_id=tenant_id
        ))

    def get_metric(self, name: str) -> Optional[MetricDefinition]:
        full_name = f"{self._namespace}_{name}" if not name.startswith(self._namespace) else name
        return self._metrics.get(full_name)

    def get_all_metrics(self) -> List[MetricDefinition]:
        return list(self._metrics.values())

    def render_prometheus_text(self) -> str:
        """Render metrics in Prometheus text format."""
        lines = []
        for metric in self._metrics.values():
            lines.append(f"# HELP {metric.name} {metric.help_text}")
            lines.append(f"# TYPE {metric.name} {metric.metric_type.value}")
            if metric.samples:
                latest = metric.samples[-1]
                label_str = ",".join(f'{k}="{v}"' for k, v in latest.labels.items())
                label_suffix = f"{{{label_str}}}" if label_str else ""
                lines.append(f"{metric.name}{label_suffix} {latest.value}")
            else:
                lines.append(f"{metric.name} {metric.current_value}")
        return "\n".join(lines)

    def get_metrics_snapshot(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current metric values as a JSON snapshot."""
        snapshot = {}
        for name, metric in self._metrics.items():
            samples = metric.samples
            if tenant_id:
                samples = [s for s in samples if s.tenant_id == tenant_id]
            if samples:
                snapshot[name] = {
                    "type": metric.metric_type.value,
                    "current": samples[-1].value,
                    "samples": len(samples),
                }
            else:
                snapshot[name] = {"type": metric.metric_type.value, "current": 0.0, "samples": 0}
        return snapshot

    def get_collector_summary(self) -> Dict[str, Any]:
        return {
            "namespace": self._namespace,
            "total_metrics": len(self._metrics),
            "total_samples": sum(len(m.samples) for m in self._metrics.values()),
            "by_type": {t.value: sum(1 for m in self._metrics.values() if m.metric_type == t) for t in MetricType},
        }
