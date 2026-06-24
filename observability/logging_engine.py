"""
Sprint 12 — Logging Engine
Structured JSON logging with correlation IDs, log levels, and filtering.
"""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEntry:
    """A structured log entry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: LogLevel = LogLevel.INFO
    message: str = ""
    service: str = ""
    component: str = ""
    tenant_id: str = "default"
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    fields: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[str] = None
    stack_trace: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        entry = {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "service": self.service,
            "component": self.component,
            "tenant_id": self.tenant_id,
        }
        if self.trace_id:
            entry["trace_id"] = self.trace_id
        if self.span_id:
            entry["span_id"] = self.span_id
        if self.correlation_id:
            entry["correlation_id"] = self.correlation_id
        if self.user_id:
            entry["user_id"] = self.user_id
        if self.fields:
            entry["fields"] = self.fields
        if self.exception:
            entry["exception"] = self.exception
        return entry

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


class LoggingEngine:
    """
    Centralized structured logging engine with JSON output,
    correlation ID tracking, and multi-level filtering.
    """

    def __init__(
        self,
        service_name: str = "engineering-os",
        min_level: LogLevel = LogLevel.INFO,
        max_buffer_size: int = 10_000,
    ):
        self._service_name = service_name
        self._min_level = min_level
        self._log_buffer: List[LogEntry] = []
        self._max_buffer = max_buffer_size
        self._forwarded_loggers: List[logging.Logger] = []

        # Level ordering for filtering
        self._level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4,
        }

    def _should_log(self, level: LogLevel) -> bool:
        return self._level_order[level] >= self._level_order[self._min_level]

    def _write(
        self,
        level: LogLevel,
        message: str,
        component: str = "",
        tenant_id: str = "default",
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        fields: Optional[Dict[str, Any]] = None,
        exception: Optional[str] = None,
    ) -> Optional[LogEntry]:
        if not self._should_log(level):
            return None

        entry = LogEntry(
            level=level,
            message=message,
            service=self._service_name,
            component=component,
            tenant_id=tenant_id,
            trace_id=trace_id,
            span_id=span_id,
            correlation_id=correlation_id,
            user_id=user_id,
            fields=fields or {},
            exception=exception,
        )

        if len(self._log_buffer) >= self._max_buffer:
            self._log_buffer.pop(0)
        self._log_buffer.append(entry)

        # Forward to Python logger
        python_level = getattr(logging, level.value, logging.INFO)
        logging.getLogger(self._service_name).log(python_level, entry.to_json())
        return entry

    def debug(self, message: str, **kwargs) -> Optional[LogEntry]:
        return self._write(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> Optional[LogEntry]:
        return self._write(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> Optional[LogEntry]:
        return self._write(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> Optional[LogEntry]:
        return self._write(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> Optional[LogEntry]:
        return self._write(LogLevel.CRITICAL, message, **kwargs)

    def query_logs(
        self,
        level: Optional[LogLevel] = None,
        service: Optional[str] = None,
        component: Optional[str] = None,
        tenant_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        search_text: Optional[str] = None,
        limit: int = 100,
    ) -> List[LogEntry]:
        """Query the log buffer with filters."""
        logs = list(self._log_buffer)

        if level:
            logs = [e for e in logs if self._level_order[e.level] >= self._level_order[level]]
        if service:
            logs = [e for e in logs if e.service == service]
        if component:
            logs = [e for e in logs if e.component == component]
        if tenant_id:
            logs = [e for e in logs if e.tenant_id == tenant_id]
        if trace_id:
            logs = [e for e in logs if e.trace_id == trace_id]
        if search_text:
            sl = search_text.lower()
            logs = [e for e in logs if sl in e.message.lower()]

        return sorted(logs, key=lambda e: e.timestamp, reverse=True)[:limit]

    def get_log_summary(self) -> Dict[str, Any]:
        entries = self._log_buffer
        return {
            "total_entries": len(entries),
            "buffer_capacity": self._max_buffer,
            "by_level": {l.value: sum(1 for e in entries if e.level == l) for l in LogLevel},
            "services": list({e.service for e in entries}),
            "min_level": self._min_level.value,
        }

    def set_min_level(self, level: LogLevel) -> None:
        """Dynamically change the minimum log level."""
        self._min_level = level
        logger.info(f"Log level set to {level.value}")

    def clear_buffer(self) -> int:
        count = len(self._log_buffer)
        self._log_buffer.clear()
        return count
