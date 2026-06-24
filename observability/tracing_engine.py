"""
Sprint 12 — Tracing Engine
OpenTelemetry distributed tracing with span management and trace propagation.
"""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

logger = logging.getLogger(__name__)


class SpanStatus(str, Enum):
    OK = "ok"
    ERROR = "error"
    UNSET = "unset"


class SpanKind(str, Enum):
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


@dataclass
class Span:
    """Represents an OpenTelemetry span."""
    trace_id: str = ""
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: Optional[str] = None
    name: str = ""
    service_name: str = ""
    kind: SpanKind = SpanKind.INTERNAL
    status: SpanStatus = SpanStatus.UNSET
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    tenant_id: str = "default"

    @property
    def duration_ms(self) -> Optional[float]:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None

    @property
    def is_root(self) -> bool:
        return self.parent_span_id is None

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        self.events.append({
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attributes": attributes or {},
        })

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def finish(self, status: SpanStatus = SpanStatus.OK, error: Optional[str] = None) -> None:
        self.end_time = time.time()
        self.status = status
        if error:
            self.error_message = error
            self.status = SpanStatus.ERROR

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "service_name": self.service_name,
            "kind": self.kind.value,
            "status": self.status.value,
            "start_time": datetime.fromtimestamp(self.start_time, tz=timezone.utc).isoformat(),
            "end_time": datetime.fromtimestamp(self.end_time, tz=timezone.utc).isoformat() if self.end_time else None,
            "duration_ms": round(self.duration_ms, 3) if self.duration_ms else None,
            "attributes": self.attributes,
            "events": self.events,
            "error_message": self.error_message,
            "tenant_id": self.tenant_id,
        }


@dataclass
class Trace:
    """A complete distributed trace containing multiple spans."""
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    spans: List[Span] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def root_span(self) -> Optional[Span]:
        return next((s for s in self.spans if s.is_root), None)

    @property
    def total_duration_ms(self) -> Optional[float]:
        root = self.root_span
        return root.duration_ms if root else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_count": len(self.spans),
            "total_duration_ms": round(self.total_duration_ms, 3) if self.total_duration_ms else None,
            "services": list({s.service_name for s in self.spans}),
            "has_errors": any(s.status == SpanStatus.ERROR for s in self.spans),
            "spans": [s.to_dict() for s in self.spans],
            "created_at": self.created_at.isoformat(),
        }


class TracingEngine:
    """
    OpenTelemetry-compatible distributed tracing engine.
    Manages span creation, propagation, and trace collection.
    """

    def __init__(self, service_name: str = "engineering-os", exporter_endpoint: str = "http://localhost:4317"):
        self._service_name = service_name
        self._exporter_endpoint = exporter_endpoint
        self._traces: Dict[str, Trace] = {}
        self._active_spans: Dict[str, Span] = {}
        self._sampling_rate: float = 1.0  # 100% sampling

    def start_trace(self, name: str, tenant_id: str = "default") -> Span:
        """Start a new root trace."""
        trace_id = uuid.uuid4().hex
        trace = Trace(trace_id=trace_id)
        self._traces[trace_id] = trace

        span = Span(
            trace_id=trace_id,
            name=name,
            service_name=self._service_name,
            kind=SpanKind.SERVER,
            tenant_id=tenant_id,
        )
        trace.spans.append(span)
        self._active_spans[span.span_id] = span
        return span

    def start_span(
        self,
        name: str,
        trace_id: str,
        parent_span_id: Optional[str] = None,
        service_name: Optional[str] = None,
        kind: SpanKind = SpanKind.INTERNAL,
        tenant_id: str = "default",
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Span:
        """Start a child span within an existing trace."""
        trace = self._traces.get(trace_id)
        if not trace:
            trace = Trace(trace_id=trace_id)
            self._traces[trace_id] = trace

        span = Span(
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=name,
            service_name=service_name or self._service_name,
            kind=kind,
            tenant_id=tenant_id,
            attributes=attributes or {},
        )
        trace.spans.append(span)
        self._active_spans[span.span_id] = span
        return span

    def finish_span(
        self,
        span: Span,
        status: SpanStatus = SpanStatus.OK,
        error: Optional[str] = None,
    ) -> Span:
        """Finish a span."""
        span.finish(status=status, error=error)
        self._active_spans.pop(span.span_id, None)
        if error:
            logger.warning(f"Span '{span.name}' [{span.trace_id}] failed: {error}")
        return span

    @asynccontextmanager
    async def trace_context(
        self,
        name: str,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        tenant_id: str = "default",
        attributes: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Span, None]:
        """Async context manager for automatic span lifecycle management."""
        if trace_id:
            span = self.start_span(
                name=name,
                trace_id=trace_id,
                parent_span_id=parent_span_id,
                tenant_id=tenant_id,
                attributes=attributes,
            )
        else:
            span = self.start_trace(name=name, tenant_id=tenant_id)
        try:
            yield span
            self.finish_span(span, SpanStatus.OK)
        except Exception as exc:
            self.finish_span(span, SpanStatus.ERROR, str(exc))
            raise

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        return self._traces.get(trace_id)

    def get_span(self, span_id: str) -> Optional[Span]:
        return self._active_spans.get(span_id)

    def search_traces(
        self,
        service_name: Optional[str] = None,
        has_errors: bool = False,
        tenant_id: Optional[str] = None,
        min_duration_ms: Optional[float] = None,
        limit: int = 50,
    ) -> List[Trace]:
        traces = list(self._traces.values())

        if service_name:
            traces = [t for t in traces if any(s.service_name == service_name for s in t.spans)]
        if has_errors:
            traces = [t for t in traces if any(s.status == SpanStatus.ERROR for s in t.spans)]
        if tenant_id:
            traces = [t for t in traces if any(s.tenant_id == tenant_id for s in t.spans)]
        if min_duration_ms is not None:
            traces = [t for t in traces if t.total_duration_ms and t.total_duration_ms >= min_duration_ms]

        return sorted(traces, key=lambda t: t.created_at, reverse=True)[:limit]

    def get_tracing_stats(self) -> Dict[str, Any]:
        all_spans = [s for t in self._traces.values() for s in t.spans]
        durations = [s.duration_ms for s in all_spans if s.duration_ms is not None]
        error_spans = [s for s in all_spans if s.status == SpanStatus.ERROR]
        return {
            "total_traces": len(self._traces),
            "total_spans": len(all_spans),
            "active_spans": len(self._active_spans),
            "error_rate": round(len(error_spans) / len(all_spans), 4) if all_spans else 0.0,
            "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0.0,
            "p99_duration_ms": round(sorted(durations)[int(len(durations) * 0.99)], 2) if durations else 0.0,
            "sampling_rate": self._sampling_rate,
        }
