"""
Sprint 12 — Alert Manager
Alert rule engine with severity levels, routing, suppression, and escalation.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    PAGE = "page"


class AlertStatus(str, Enum):
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"
    SILENCED = "silenced"


class AlertConditionType(str, Enum):
    THRESHOLD = "threshold"           # value > threshold
    RATE_OF_CHANGE = "rate_of_change"
    ANOMALY = "anomaly"
    ABSENCE = "absence"               # metric absent for N minutes


@dataclass
class AlertRule:
    """Defines an alerting rule."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    metric_name: str = ""
    condition_type: AlertConditionType = AlertConditionType.THRESHOLD
    threshold: float = 0.0
    operator: str = ">"  # >, <, >=, <=, ==
    duration_minutes: int = 5
    severity: AlertSeverity = AlertSeverity.WARNING
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    tenant_id: str = "default"
    notification_channels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def evaluate(self, metric_value: float) -> bool:
        """Evaluate if the alert condition is met."""
        ops = {
            ">": metric_value > self.threshold,
            "<": metric_value < self.threshold,
            ">=": metric_value >= self.threshold,
            "<=": metric_value <= self.threshold,
            "==": abs(metric_value - self.threshold) < 1e-9,
        }
        return ops.get(self.operator, False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "metric_name": self.metric_name,
            "condition": f"{self.metric_name} {self.operator} {self.threshold}",
            "severity": self.severity.value,
            "duration_minutes": self.duration_minutes,
            "enabled": self.enabled,
            "tenant_id": self.tenant_id,
        }


@dataclass
class Alert:
    """A fired alert instance."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    rule_name: str = ""
    status: AlertStatus = AlertStatus.FIRING
    severity: AlertSeverity = AlertSeverity.WARNING
    metric_name: str = ""
    current_value: float = 0.0
    threshold: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    tenant_id: str = "default"
    fingerprint: str = ""
    fired_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    silenced_until: Optional[datetime] = None
    escalation_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_name": self.rule_name,
            "status": self.status.value,
            "severity": self.severity.value,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "threshold": self.threshold,
            "labels": self.labels,
            "tenant_id": self.tenant_id,
            "fired_at": self.fired_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "acknowledged_by": self.acknowledged_by,
            "duration_minutes": round((datetime.now(timezone.utc) - self.fired_at).total_seconds() / 60, 1),
        }


class AlertManager:
    """
    Alert rule engine with firing, routing, suppression, and acknowledgment.
    Integrates with Prometheus AlertManager patterns.
    """

    def __init__(self):
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: Dict[str, Alert] = {}
        self._silences: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[AlertSeverity, List[Callable]] = {s: [] for s in AlertSeverity}
        self._stats = {"fired": 0, "resolved": 0, "suppressed": 0}

    async def create_rule(
        self,
        name: str,
        metric_name: str,
        threshold: float,
        operator: str = ">",
        severity: AlertSeverity = AlertSeverity.WARNING,
        duration_minutes: int = 5,
        description: str = "",
        labels: Optional[Dict[str, str]] = None,
        notification_channels: Optional[List[str]] = None,
        tenant_id: str = "default",
    ) -> AlertRule:
        """Create an alerting rule."""
        rule = AlertRule(
            name=name,
            description=description,
            metric_name=metric_name,
            threshold=threshold,
            operator=operator,
            severity=severity,
            duration_minutes=duration_minutes,
            labels=labels or {},
            notification_channels=notification_channels or [],
            tenant_id=tenant_id,
        )
        self._rules[rule.id] = rule
        logger.info(f"Alert rule '{name}' created: {metric_name} {operator} {threshold}")
        return rule

    def _generate_fingerprint(self, rule: AlertRule, labels: Dict[str, str]) -> str:
        """Generate unique fingerprint for an alert (deduplication)."""
        parts = sorted(f"{k}={v}" for k, v in {**rule.labels, **labels}.items())
        return f"{rule.id}:{':'.join(parts)}"

    async def evaluate_metric(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        tenant_id: str = "default",
    ) -> List[Alert]:
        """Evaluate all rules matching this metric and fire/resolve alerts."""
        labels = labels or {}
        matching_rules = [
            r for r in self._rules.values()
            if r.metric_name == metric_name and r.enabled and r.tenant_id == tenant_id
        ]
        fired_alerts = []

        for rule in matching_rules:
            fingerprint = self._generate_fingerprint(rule, labels)
            existing = next(
                (a for a in self._alerts.values() if a.fingerprint == fingerprint and a.status == AlertStatus.FIRING),
                None,
            )

            if rule.evaluate(value):
                if existing:
                    existing.current_value = value
                    continue

                # Check silences
                silence = self._silences.get(fingerprint)
                if silence and silence["until"] > datetime.now(timezone.utc):
                    self._stats["suppressed"] += 1
                    continue

                alert = Alert(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    status=AlertStatus.FIRING,
                    severity=rule.severity,
                    metric_name=metric_name,
                    current_value=value,
                    threshold=rule.threshold,
                    labels={**rule.labels, **labels},
                    annotations=rule.annotations,
                    tenant_id=tenant_id,
                    fingerprint=fingerprint,
                )
                self._alerts[alert.id] = alert
                self._stats["fired"] += 1
                fired_alerts.append(alert)
                logger.warning(f"Alert FIRED: {rule.name} | {metric_name}={value} {rule.operator} {rule.threshold}")

                # Dispatch handlers
                for handler in self._handlers.get(rule.severity, []):
                    try:
                        await asyncio.ensure_future(
                            handler(alert) if asyncio.iscoroutinefunction(handler) else asyncio.coroutine(handler)(alert)
                        )
                    except Exception as exc:
                        logger.error(f"Alert handler error: {exc}")
            else:
                # Resolve any existing alerts for this rule
                if existing:
                    existing.status = AlertStatus.RESOLVED
                    existing.resolved_at = datetime.now(timezone.utc)
                    self._stats["resolved"] += 1
                    logger.info(f"Alert RESOLVED: {rule.name}")

        return fired_alerts

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Alert:
        """Acknowledge an alert."""
        alert = self._alerts.get(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now(timezone.utc)
        return alert

    async def silence_alert(
        self, fingerprint: str, duration_minutes: int = 60, reason: str = ""
    ) -> Dict[str, Any]:
        """Silence an alert by fingerprint for a duration."""
        until = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        self._silences[fingerprint] = {"until": until, "reason": reason}
        logger.info(f"Alert silenced: {fingerprint} until {until.isoformat()}")
        return {"fingerprint": fingerprint, "silenced_until": until.isoformat(), "reason": reason}

    def register_handler(self, severity: AlertSeverity, handler: Callable) -> None:
        """Register a notification handler for a specific severity."""
        self._handlers[severity].append(handler)

    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        return self._alerts.get(alert_id)

    async def list_alerts(
        self,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Alert]:
        alerts = list(self._alerts.values())
        if status:
            alerts = [a for a in alerts if a.status == status]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if tenant_id:
            alerts = [a for a in alerts if a.tenant_id == tenant_id]
        return sorted(alerts, key=lambda a: a.fired_at, reverse=True)

    async def list_rules(self, tenant_id: Optional[str] = None) -> List[AlertRule]:
        rules = list(self._rules.values())
        if tenant_id:
            rules = [r for r in rules if r.tenant_id == tenant_id]
        return rules

    async def generate_alert_report(self) -> Dict[str, Any]:
        alerts = list(self._alerts.values())
        firing = [a for a in alerts if a.status == AlertStatus.FIRING]
        return {
            "report_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_rules": len(self._rules),
                "total_alerts": len(alerts),
                "currently_firing": len(firing),
                **self._stats,
            },
            "firing_by_severity": {
                s.value: sum(1 for a in firing if a.severity == s) for s in AlertSeverity
            },
            "top_firing_rules": [
                {"rule_name": a.rule_name, "severity": a.severity.value, "fired_at": a.fired_at.isoformat()}
                for a in sorted(firing, key=lambda a: a.fired_at)[:10]
            ],
        }
