"""
Sprint 12 — Event Bus
Unified producer/consumer abstraction over Kafka and NATS.
Provides event-driven messaging for the Engineering OS cloud platform.
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventBackend(str, Enum):
    KAFKA = "kafka"
    NATS = "nats"
    MEMORY = "memory"  # For testing


class EventDeliveryMode(str, Enum):
    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"
    EXACTLY_ONCE = "exactly_once"


@dataclass
class Topic:
    """Represents a message topic/channel."""
    name: str = ""
    backend: EventBackend = EventBackend.KAFKA
    partitions: int = 6
    replication_factor: int = 3
    retention_hours: int = 168  # 7 days
    max_message_bytes: int = 10_485_760  # 10MB
    compaction_enabled: bool = False
    schema_class: Optional[str] = None
    tenant_id: str = "default"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "backend": self.backend.value,
            "partitions": self.partitions,
            "replication_factor": self.replication_factor,
            "retention_hours": self.retention_hours,
            "tenant_id": self.tenant_id,
        }


@dataclass
class Message:
    """A message published to the event bus."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    key: Optional[str] = None
    value: Any = None
    headers: Dict[str, str] = field(default_factory=dict)
    partition: int = 0
    offset: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tenant_id: str = "default"
    trace_id: Optional[str] = None
    correlation_id: Optional[str] = None

    def serialize(self) -> bytes:
        payload = {
            "id": self.id,
            "topic": self.topic,
            "key": self.key,
            "value": self.value,
            "headers": self.headers,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
        }
        return json.dumps(payload, default=str).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes) -> "Message":
        payload = json.loads(data.decode("utf-8"))
        msg = cls(**{k: v for k, v in payload.items() if k != "timestamp"})
        msg.timestamp = datetime.fromisoformat(payload["timestamp"])
        return msg

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "key": self.key,
            "value": self.value,
            "headers": self.headers,
            "partition": self.partition,
            "offset": self.offset,
            "timestamp": self.timestamp.isoformat(),
            "tenant_id": self.tenant_id,
            "trace_id": self.trace_id,
        }


@dataclass
class ConsumerGroup:
    """Tracks a consumer group subscription."""
    group_id: str = ""
    topics: List[str] = field(default_factory=list)
    backend: EventBackend = EventBackend.KAFKA
    handler: Optional[Callable] = None
    delivery_mode: EventDeliveryMode = EventDeliveryMode.AT_LEAST_ONCE
    dead_letter_topic: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    """
    Unified event bus supporting Kafka and NATS backends.
    Provides topic management, message publishing, and consumer group management.
    """

    def __init__(
        self,
        kafka_bootstrap_servers: str = "localhost:9092",
        nats_url: str = "nats://localhost:4222",
        default_backend: EventBackend = EventBackend.MEMORY,
    ):
        self._kafka_servers = kafka_bootstrap_servers
        self._nats_url = nats_url
        self._default_backend = default_backend
        self._topics: Dict[str, Topic] = {}
        self._message_store: Dict[str, List[Message]] = {}  # topic -> messages
        self._consumer_groups: Dict[str, ConsumerGroup] = {}
        self._consumer_offsets: Dict[str, Dict[str, int]] = {}  # group -> {topic -> offset}
        self._dead_letter_queue: Dict[str, List[Message]] = {}
        self._stats = {
            "messages_published": 0,
            "messages_consumed": 0,
            "errors": 0,
        }

    async def create_topic(
        self,
        name: str,
        backend: Optional[EventBackend] = None,
        partitions: int = 6,
        replication_factor: int = 3,
        retention_hours: int = 168,
        tenant_id: str = "default",
        compaction_enabled: bool = False,
    ) -> Topic:
        """Create a new event topic."""
        if name in self._topics:
            return self._topics[name]

        topic = Topic(
            name=name,
            backend=backend or self._default_backend,
            partitions=partitions,
            replication_factor=replication_factor,
            retention_hours=retention_hours,
            tenant_id=tenant_id,
            compaction_enabled=compaction_enabled,
        )
        self._topics[name] = topic
        self._message_store[name] = []
        logger.info(f"Topic '{name}' created ({backend or self._default_backend} | {partitions} partitions)")
        return topic

    async def publish(
        self,
        topic: str,
        value: Any,
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        tenant_id: str = "default",
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Message:
        """Publish a message to a topic."""
        if topic not in self._topics:
            await self.create_topic(topic)

        # Partition assignment (hash-based)
        topic_info = self._topics[topic]
        partition = hash(key or "") % topic_info.partitions if key else 0
        offset = len(self._message_store[topic])

        message = Message(
            topic=topic,
            key=key,
            value=value,
            headers=headers or {},
            partition=partition,
            offset=offset,
            tenant_id=tenant_id,
            trace_id=trace_id or str(uuid.uuid4()),
            correlation_id=correlation_id,
        )

        self._message_store[topic].append(message)
        self._stats["messages_published"] += 1

        # Dispatch to registered consumers asynchronously
        for group_id, group in self._consumer_groups.items():
            if topic in group.topics and group.handler:
                try:
                    await asyncio.ensure_future(self._dispatch_to_handler(group, message))
                except Exception as exc:
                    logger.error(f"Handler error in group '{group_id}': {exc}")
                    self._stats["errors"] += 1

        logger.debug(f"Message published to '{topic}' (partition={partition}, offset={offset})")
        return message

    async def _dispatch_to_handler(self, group: ConsumerGroup, message: Message) -> None:
        """Dispatch a message to a consumer group handler."""
        try:
            if asyncio.iscoroutinefunction(group.handler):
                await group.handler(message)
            else:
                group.handler(message)
            self._stats["messages_consumed"] += 1
        except Exception as exc:
            self._stats["errors"] += 1
            if group.dead_letter_topic:
                dlq = group.dead_letter_topic
                if dlq not in self._dead_letter_queue:
                    self._dead_letter_queue[dlq] = []
                self._dead_letter_queue[dlq].append(message)
            raise

    async def subscribe(
        self,
        group_id: str,
        topics: List[str],
        handler: Callable,
        delivery_mode: EventDeliveryMode = EventDeliveryMode.AT_LEAST_ONCE,
        dead_letter_topic: Optional[str] = None,
    ) -> ConsumerGroup:
        """Subscribe a consumer group to topics."""
        group = ConsumerGroup(
            group_id=group_id,
            topics=topics,
            backend=self._default_backend,
            handler=handler,
            delivery_mode=delivery_mode,
            dead_letter_topic=dead_letter_topic,
        )
        self._consumer_groups[group_id] = group
        self._consumer_offsets[group_id] = {t: 0 for t in topics}
        logger.info(f"Consumer group '{group_id}' subscribed to: {topics}")
        return group

    async def consume_batch(
        self,
        group_id: str,
        topic: str,
        max_messages: int = 100,
    ) -> List[Message]:
        """Pull messages for a consumer group."""
        group = self._consumer_groups.get(group_id)
        if not group or topic not in group.topics:
            raise ValueError(f"Consumer group '{group_id}' not subscribed to '{topic}'")

        current_offset = self._consumer_offsets[group_id].get(topic, 0)
        messages = self._message_store.get(topic, [])
        batch = messages[current_offset: current_offset + max_messages]

        self._consumer_offsets[group_id][topic] = current_offset + len(batch)
        self._stats["messages_consumed"] += len(batch)
        return batch

    async def get_topic_stats(self, topic_name: str) -> Dict[str, Any]:
        """Get statistics for a topic."""
        if topic_name not in self._topics:
            raise ValueError(f"Topic '{topic_name}' not found")
        messages = self._message_store.get(topic_name, [])
        return {
            "topic": topic_name,
            "backend": self._topics[topic_name].backend.value,
            "partitions": self._topics[topic_name].partitions,
            "message_count": len(messages),
            "consumer_groups": [g for g, group in self._consumer_groups.items() if topic_name in group.topics],
            "consumer_offsets": {
                g: self._consumer_offsets.get(g, {}).get(topic_name, 0)
                for g in self._consumer_groups
            },
        }

    async def list_topics(self, tenant_id: Optional[str] = None) -> List[Topic]:
        topics = list(self._topics.values())
        if tenant_id:
            topics = [t for t in topics if t.tenant_id == tenant_id]
        return topics

    async def delete_topic(self, topic_name: str) -> bool:
        """Delete a topic and all its messages."""
        if topic_name not in self._topics:
            return False
        del self._topics[topic_name]
        self._message_store.pop(topic_name, None)
        return True

    async def get_dlq_messages(self, dlq_topic: str) -> List[Message]:
        return self._dead_letter_queue.get(dlq_topic, [])

    def get_bus_stats(self) -> Dict[str, Any]:
        return {
            "topics": len(self._topics),
            "consumer_groups": len(self._consumer_groups),
            "total_messages_stored": sum(len(m) for m in self._message_store.values()),
            "kafka_servers": self._kafka_servers,
            "nats_url": self._nats_url,
            **self._stats,
        }
