"""
Sprint 12 — Notification Engine
Push notification dispatch via WebSocket, webhook, and email with throttling.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    IN_APP = "in_app"


class NotificationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    THROTTLED = "throttled"


@dataclass
class NotificationRecord:
    """A notification that was sent or attempted."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    message: str = ""
    severity: NotificationSeverity = NotificationSeverity.INFO
    channel: NotificationChannel = NotificationChannel.IN_APP
    recipient: str = ""
    tenant_id: str = "default"
    status: NotificationStatus = NotificationStatus.PENDING
    payload: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    sent_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "channel": self.channel.value,
            "recipient": self.recipient,
            "tenant_id": self.tenant_id,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "created_at": self.created_at.isoformat(),
        }


class NotificationEngine:
    """
    Notification dispatch engine supporting multiple channels with throttling.
    """

    def __init__(self, throttle_per_minute: int = 60):
        self._notifications: Dict[str, NotificationRecord] = {}
        self._throttle_per_minute = throttle_per_minute
        self._sent_timestamps: Dict[str, List[datetime]] = {}  # recipient -> timestamps
        self._templates: Dict[str, str] = {}
        self._subscriptions: Dict[str, List[Dict[str, Any]]] = {}

    def _is_throttled(self, recipient: str) -> bool:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        history = [t for t in self._sent_timestamps.get(recipient, []) if t > cutoff]
        self._sent_timestamps[recipient] = history
        return len(history) >= self._throttle_per_minute

    async def send(
        self,
        title: str,
        message: str,
        recipient: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        severity: NotificationSeverity = NotificationSeverity.INFO,
        tenant_id: str = "default",
        payload: Optional[Dict[str, Any]] = None,
        force: bool = False,
    ) -> NotificationRecord:
        """Send a notification to a recipient via specified channel."""
        record = NotificationRecord(
            title=title,
            message=message,
            severity=severity,
            channel=channel,
            recipient=recipient,
            tenant_id=tenant_id,
            payload=payload or {},
        )

        if not force and self._is_throttled(recipient):
            record.status = NotificationStatus.THROTTLED
            self._notifications[record.id] = record
            logger.warning(f"Notification throttled for recipient '{recipient}'")
            return record

        # Simulate channel delivery
        await asyncio.sleep(0)
        record.status = NotificationStatus.SENT
        record.sent_at = datetime.now(timezone.utc)

        if recipient not in self._sent_timestamps:
            self._sent_timestamps[recipient] = []
        self._sent_timestamps[recipient].append(record.sent_at)

        self._notifications[record.id] = record
        logger.info(f"Notification sent [{channel.value}] to '{recipient}': {title}")
        return record

    async def broadcast(
        self,
        title: str,
        message: str,
        tenant_id: str,
        severity: NotificationSeverity = NotificationSeverity.INFO,
        channels: Optional[List[NotificationChannel]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> List[NotificationRecord]:
        """Broadcast notification to all subscribers in a tenant."""
        channels = channels or [NotificationChannel.IN_APP]
        subs = self._subscriptions.get(tenant_id, [])
        records = []

        for sub in subs:
            for channel in channels:
                if channel.value in sub.get("channels", []):
                    record = await self.send(
                        title=title,
                        message=message,
                        recipient=sub["recipient"],
                        channel=channel,
                        severity=severity,
                        tenant_id=tenant_id,
                        payload=payload,
                    )
                    records.append(record)

        return records

    def register_subscription(
        self,
        tenant_id: str,
        recipient: str,
        channels: List[NotificationChannel],
    ) -> None:
        if tenant_id not in self._subscriptions:
            self._subscriptions[tenant_id] = []
        self._subscriptions[tenant_id].append({
            "recipient": recipient,
            "channels": [c.value for c in channels],
        })

    def register_template(self, template_id: str, template: str) -> None:
        """Register a notification template."""
        self._templates[template_id] = template

    def render_template(self, template_id: str, context: Dict[str, Any]) -> str:
        """Render a template with context variables."""
        template = self._templates.get(template_id, "")
        for key, value in context.items():
            template = template.replace(f"{{{{{key}}}}}", str(value))
        return template

    async def list_notifications(
        self,
        recipient: Optional[str] = None,
        severity: Optional[NotificationSeverity] = None,
        status: Optional[NotificationStatus] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[NotificationRecord]:
        records = list(self._notifications.values())
        if recipient:
            records = [r for r in records if r.recipient == recipient]
        if severity:
            records = [r for r in records if r.severity == severity]
        if status:
            records = [r for r in records if r.status == status]
        if tenant_id:
            records = [r for r in records if r.tenant_id == tenant_id]
        return sorted(records, key=lambda r: r.created_at, reverse=True)[:limit]

    def get_stats(self) -> Dict[str, Any]:
        records = list(self._notifications.values())
        return {
            "total_notifications": len(records),
            "sent": sum(1 for r in records if r.status == NotificationStatus.SENT),
            "failed": sum(1 for r in records if r.status == NotificationStatus.FAILED),
            "throttled": sum(1 for r in records if r.status == NotificationStatus.THROTTLED),
            "by_channel": {c.value: sum(1 for r in records if r.channel == c) for c in NotificationChannel},
            "by_severity": {s.value: sum(1 for r in records if r.severity == s) for s in NotificationSeverity},
        }
