"""
Sprint 12 — Event Router
Content-based event routing with filters, transformations, and dead-letter handling.
"""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RoutingRule:
    """Defines content-based routing rule."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    source_topic: str = ""
    target_topic: str = ""
    filter_expression: str = ""  # JSONPath-like expression
    transform_function: Optional[str] = None
    enabled: bool = True
    priority: int = 0
    tenant_id: str = "default"
    match_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def matches(self, event_data: Dict[str, Any]) -> bool:
        """Evaluate filter expression against event data."""
        if not self.filter_expression:
            return True
        try:
            # Simple key=value filter evaluation
            parts = self.filter_expression.split("AND")
            for part in parts:
                part = part.strip()
                if "==" in part:
                    key, val = part.split("==", 1)
                    key, val = key.strip().strip("$."), val.strip().strip("'\"")
                    actual = str(event_data.get(key, ""))
                    if actual != val:
                        return False
                elif "contains" in part:
                    m = re.match(r"contains\((.+),\s*'(.+)'\)", part)
                    if m:
                        key = m.group(1).strip("$.")
                        val = m.group(2)
                        if val not in str(event_data.get(key, "")):
                            return False
            return True
        except Exception as exc:
            logger.warning(f"Filter evaluation error: {exc}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "source_topic": self.source_topic,
            "target_topic": self.target_topic,
            "filter_expression": self.filter_expression,
            "enabled": self.enabled,
            "priority": self.priority,
            "match_count": self.match_count,
        }


class EventRouter:
    """
    Content-based event router that routes messages between topics based on configurable rules.
    """

    def __init__(self):
        self._rules: Dict[str, List[RoutingRule]] = {}  # source_topic -> rules
        self._all_rules: Dict[str, RoutingRule] = {}
        self._routing_log: List[Dict[str, Any]] = []
        self._stats = {"routed": 0, "dropped": 0, "errors": 0}

    async def create_rule(
        self,
        name: str,
        source_topic: str,
        target_topic: str,
        filter_expression: str = "",
        priority: int = 0,
        tenant_id: str = "default",
    ) -> RoutingRule:
        """Create a content-based routing rule."""
        rule = RoutingRule(
            name=name,
            source_topic=source_topic,
            target_topic=target_topic,
            filter_expression=filter_expression,
            priority=priority,
            tenant_id=tenant_id,
        )
        self._all_rules[rule.id] = rule
        if source_topic not in self._rules:
            self._rules[source_topic] = []
        self._rules[source_topic].append(rule)
        # Sort by priority
        self._rules[source_topic].sort(key=lambda r: r.priority)
        logger.info(f"Routing rule '{name}': {source_topic} -> {target_topic} (filter: {filter_expression or 'any'})")
        return rule

    async def route_event(
        self,
        source_topic: str,
        event_data: Dict[str, Any],
        event_id: Optional[str] = None,
    ) -> List[str]:
        """Route an event and return list of target topics it was routed to."""
        rules = self._rules.get(source_topic, [])
        target_topics = []

        for rule in rules:
            if not rule.enabled:
                continue
            if rule.matches(event_data):
                target_topics.append(rule.target_topic)
                rule.match_count += 1
                self._stats["routed"] += 1
                self._routing_log.append({
                    "event_id": event_id or str(uuid.uuid4()),
                    "source": source_topic,
                    "target": rule.target_topic,
                    "rule_id": rule.id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

        if not target_topics:
            self._stats["dropped"] += 1

        return target_topics

    async def disable_rule(self, rule_id: str) -> RoutingRule:
        rule = self._all_rules.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")
        rule.enabled = False
        return rule

    async def enable_rule(self, rule_id: str) -> RoutingRule:
        rule = self._all_rules.get(rule_id)
        if not rule:
            raise ValueError(f"Rule {rule_id} not found")
        rule.enabled = True
        return rule

    async def list_rules(
        self, source_topic: Optional[str] = None, enabled_only: bool = False
    ) -> List[RoutingRule]:
        if source_topic:
            rules = self._rules.get(source_topic, [])
        else:
            rules = list(self._all_rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return rules

    def get_routing_stats(self) -> Dict[str, Any]:
        return {
            "total_rules": len(self._all_rules),
            "enabled_rules": sum(1 for r in self._all_rules.values() if r.enabled),
            "source_topics_covered": len(self._rules),
            **self._stats,
        }

    def get_routing_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._routing_log[-limit:]
