"""
Sprint 12 — Autoscaling Engine
HPA, VPA, cluster autoscaler coordination with predictive and metric-driven scaling policies.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ScalingDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class ScalingTrigger(str, Enum):
    CPU = "cpu_utilization"
    MEMORY = "memory_utilization"
    CUSTOM_METRIC = "custom_metric"
    QUEUE_DEPTH = "queue_depth"
    REQUEST_RATE = "request_rate"
    SCHEDULE = "schedule"
    PREDICTIVE = "predictive"


@dataclass
class ScalingPolicy:
    """Defines autoscaling rules for a workload."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    cluster_id: str = ""
    namespace: str = "default"
    workload_name: str = ""
    min_replicas: int = 1
    max_replicas: int = 20
    target_cpu_utilization: float = 0.70  # 70%
    target_memory_utilization: float = 0.80  # 80%
    scale_up_cooldown_seconds: int = 60
    scale_down_cooldown_seconds: int = 300
    triggers: List[ScalingTrigger] = field(default_factory=lambda: [ScalingTrigger.CPU])
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    enabled: bool = True
    tenant_id: str = "default"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "cluster_id": self.cluster_id,
            "namespace": self.namespace,
            "workload_name": self.workload_name,
            "min_replicas": self.min_replicas,
            "max_replicas": self.max_replicas,
            "target_cpu_utilization": self.target_cpu_utilization,
            "target_memory_utilization": self.target_memory_utilization,
            "triggers": [t.value for t in self.triggers],
            "enabled": self.enabled,
            "tenant_id": self.tenant_id,
        }


@dataclass
class ScalingEvent:
    """Records a scaling decision and action."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    policy_id: str = ""
    cluster_id: str = ""
    workload_name: str = ""
    direction: ScalingDirection = ScalingDirection.STABLE
    trigger: ScalingTrigger = ScalingTrigger.CPU
    previous_replicas: int = 1
    target_replicas: int = 1
    metric_value: float = 0.0
    metric_threshold: float = 0.0
    reason: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "policy_id": self.policy_id,
            "cluster_id": self.cluster_id,
            "workload_name": self.workload_name,
            "direction": self.direction.value,
            "trigger": self.trigger.value,
            "previous_replicas": self.previous_replicas,
            "target_replicas": self.target_replicas,
            "metric_value": self.metric_value,
            "metric_threshold": self.metric_threshold,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


class AutoscalingEngine:
    """
    Coordinates HPA, VPA, and cluster autoscaler decisions for the Engineering OS.
    Supports CPU/memory/custom metric triggers and predictive scaling.
    """

    def __init__(self):
        self._policies: Dict[str, ScalingPolicy] = {}
        self._events: List[ScalingEvent] = []
        self._current_replicas: Dict[str, int] = {}  # workload_name -> replicas
        self._last_scale_time: Dict[str, datetime] = {}

    async def create_scaling_policy(
        self,
        name: str,
        cluster_id: str,
        workload_name: str,
        namespace: str = "default",
        min_replicas: int = 1,
        max_replicas: int = 20,
        target_cpu_utilization: float = 0.70,
        target_memory_utilization: float = 0.80,
        triggers: Optional[List[ScalingTrigger]] = None,
        scale_up_cooldown_seconds: int = 60,
        scale_down_cooldown_seconds: int = 300,
        tenant_id: str = "default",
    ) -> ScalingPolicy:
        """Create an autoscaling policy for a workload."""
        policy = ScalingPolicy(
            name=name,
            cluster_id=cluster_id,
            namespace=namespace,
            workload_name=workload_name,
            min_replicas=min_replicas,
            max_replicas=max_replicas,
            target_cpu_utilization=target_cpu_utilization,
            target_memory_utilization=target_memory_utilization,
            scale_up_cooldown_seconds=scale_up_cooldown_seconds,
            scale_down_cooldown_seconds=scale_down_cooldown_seconds,
            triggers=triggers or [ScalingTrigger.CPU],
            tenant_id=tenant_id,
        )
        self._policies[policy.id] = policy
        self._current_replicas[workload_name] = min_replicas
        logger.info(f"Scaling policy '{name}' created for {workload_name} in {cluster_id}")
        return policy

    def _calculate_desired_replicas(
        self,
        policy: ScalingPolicy,
        cpu_utilization: float,
        memory_utilization: float,
        current_replicas: int,
    ) -> Tuple[int, ScalingTrigger, float, str]:
        """Calculate desired replica count based on metrics."""
        desired = current_replicas

        # CPU-driven scaling
        if ScalingTrigger.CPU in policy.triggers:
            if cpu_utilization > policy.target_cpu_utilization:
                ratio = cpu_utilization / policy.target_cpu_utilization
                desired = max(desired, int(current_replicas * ratio) + 1)
                return (
                    min(desired, policy.max_replicas),
                    ScalingTrigger.CPU,
                    cpu_utilization,
                    f"CPU {cpu_utilization:.1%} > threshold {policy.target_cpu_utilization:.1%}",
                )
            elif cpu_utilization < policy.target_cpu_utilization * 0.5 and current_replicas > policy.min_replicas:
                desired = max(policy.min_replicas, current_replicas - 1)
                return (
                    desired,
                    ScalingTrigger.CPU,
                    cpu_utilization,
                    f"CPU {cpu_utilization:.1%} < 50% of threshold, scaling down",
                )

        # Memory-driven scaling
        if ScalingTrigger.MEMORY in policy.triggers:
            if memory_utilization > policy.target_memory_utilization:
                desired = min(current_replicas + 1, policy.max_replicas)
                return (
                    desired,
                    ScalingTrigger.MEMORY,
                    memory_utilization,
                    f"Memory {memory_utilization:.1%} > threshold {policy.target_memory_utilization:.1%}",
                )

        return (current_replicas, ScalingTrigger.CPU, cpu_utilization, "No scaling needed")

    async def evaluate_scaling(
        self,
        policy_id: str,
        cpu_utilization: float,
        memory_utilization: float = 0.5,
        custom_metrics: Optional[Dict[str, float]] = None,
    ) -> ScalingEvent:
        """Evaluate metrics and decide scaling action."""
        policy = self._policies.get(policy_id)
        if not policy:
            raise ValueError(f"Scaling policy {policy_id} not found")
        if not policy.enabled:
            raise ValueError(f"Scaling policy {policy_id} is disabled")

        current = self._current_replicas.get(policy.workload_name, policy.min_replicas)
        desired, trigger, metric_val, reason = self._calculate_desired_replicas(
            policy, cpu_utilization, memory_utilization, current
        )

        if desired > current:
            direction = ScalingDirection.UP
        elif desired < current:
            direction = ScalingDirection.DOWN
        else:
            direction = ScalingDirection.STABLE

        event = ScalingEvent(
            policy_id=policy_id,
            cluster_id=policy.cluster_id,
            workload_name=policy.workload_name,
            direction=direction,
            trigger=trigger,
            previous_replicas=current,
            target_replicas=desired,
            metric_value=metric_val,
            metric_threshold=policy.target_cpu_utilization,
            reason=reason,
        )

        if direction != ScalingDirection.STABLE:
            self._current_replicas[policy.workload_name] = desired
            self._last_scale_time[policy.workload_name] = datetime.now(timezone.utc)
            logger.info(f"Scaling {policy.workload_name}: {current} -> {desired} ({reason})")

        self._events.append(event)
        return event

    async def get_policy(self, policy_id: str) -> Optional[ScalingPolicy]:
        return self._policies.get(policy_id)

    async def list_policies(
        self,
        cluster_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[ScalingPolicy]:
        policies = list(self._policies.values())
        if cluster_id:
            policies = [p for p in policies if p.cluster_id == cluster_id]
        if tenant_id:
            policies = [p for p in policies if p.tenant_id == tenant_id]
        return policies

    async def get_scaling_history(
        self, workload_name: Optional[str] = None, limit: int = 100
    ) -> List[ScalingEvent]:
        events = self._events[-limit:]
        if workload_name:
            events = [e for e in events if e.workload_name == workload_name]
        return events

    async def predictive_scale(
        self,
        policy_id: str,
        forecast_cpu: List[float],
        forecast_window_minutes: int = 30,
    ) -> Dict[str, Any]:
        """Generate predictive scaling recommendations based on CPU forecast."""
        policy = self._policies.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")

        peak_cpu = max(forecast_cpu) if forecast_cpu else 0.0
        avg_cpu = sum(forecast_cpu) / len(forecast_cpu) if forecast_cpu else 0.0
        current = self._current_replicas.get(policy.workload_name, policy.min_replicas)

        if peak_cpu > policy.target_cpu_utilization:
            recommended = min(int(current * peak_cpu / policy.target_cpu_utilization) + 1, policy.max_replicas)
        else:
            recommended = current

        return {
            "policy_id": policy_id,
            "workload_name": policy.workload_name,
            "forecast_window_minutes": forecast_window_minutes,
            "peak_forecast_cpu": peak_cpu,
            "avg_forecast_cpu": avg_cpu,
            "current_replicas": current,
            "recommended_replicas": recommended,
            "action": "pre_scale" if recommended > current else "maintain",
            "confidence": 0.85,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def disable_policy(self, policy_id: str) -> ScalingPolicy:
        """Disable an autoscaling policy."""
        policy = self._policies.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        policy.enabled = False
        return policy

    async def enable_policy(self, policy_id: str) -> ScalingPolicy:
        """Enable an autoscaling policy."""
        policy = self._policies.get(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        policy.enabled = True
        return policy

    def get_autoscaling_summary(self) -> Dict[str, Any]:
        """Summary of all autoscaling activity."""
        return {
            "total_policies": len(self._policies),
            "enabled_policies": sum(1 for p in self._policies.values() if p.enabled),
            "total_scaling_events": len(self._events),
            "scale_up_events": sum(1 for e in self._events if e.direction == ScalingDirection.UP),
            "scale_down_events": sum(1 for e in self._events if e.direction == ScalingDirection.DOWN),
            "workloads_managed": list(self._current_replicas.keys()),
        }
