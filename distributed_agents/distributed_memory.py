"""
Sprint 12 — Distributed Memory
Redis-backed distributed shared memory with Qdrant vector memory
for semantic agent context sharing across the cluster.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A single entry in distributed memory."""
    key: str = ""
    value: Any = None
    namespace: str = "default"
    tenant_id: str = "default"
    ttl_seconds: Optional[int] = None
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)
    content_hash: str = ""

    def compute_hash(self) -> str:
        content = json.dumps(self.value, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "namespace": self.namespace,
            "tenant_id": self.tenant_id,
            "ttl_seconds": self.ttl_seconds,
            "version": self.version,
            "content_hash": self.content_hash,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class VectorMemoryEntry:
    """A semantic memory entry with vector embedding."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    embedding: List[float] = field(default_factory=list)
    namespace: str = "agents"
    tenant_id: str = "default"
    agent_id: Optional[str] = None
    project_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    similarity_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "namespace": self.namespace,
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "project_id": self.project_id,
            "metadata": self.metadata,
            "similarity_score": self.similarity_score,
            "created_at": self.created_at.isoformat(),
        }


class DistributedMemory:
    """
    Distributed shared memory system combining:
    - Redis-like key-value store (simulated) for fast state sharing
    - Qdrant-like vector store (simulated) for semantic agent context

    In production: connects to Redis cluster and Qdrant deployment.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", qdrant_url: str = "http://localhost:6333"):
        self._redis_url = redis_url
        self._qdrant_url = qdrant_url
        # In-memory simulation (replace with actual Redis/Qdrant clients)
        self._kv_store: Dict[str, MemoryEntry] = {}
        self._vector_store: Dict[str, VectorMemoryEntry] = {}
        self._pub_sub_channels: Dict[str, List[Any]] = {}
        self._locks: Dict[str, str] = {}  # key -> lock_holder_id

    # ===== Key-Value Store (Redis-backed) =====

    async def set(
        self,
        key: str,
        value: Any,
        namespace: str = "default",
        tenant_id: str = "default",
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> MemoryEntry:
        """Store a value in distributed KV memory."""
        namespaced_key = f"{tenant_id}:{namespace}:{key}"
        entry = MemoryEntry(
            key=key,
            value=value,
            namespace=namespace,
            tenant_id=tenant_id,
            ttl_seconds=ttl_seconds,
            tags=tags or [],
        )
        entry.content_hash = entry.compute_hash()
        if namespaced_key in self._kv_store:
            entry.version = self._kv_store[namespaced_key].version + 1
        self._kv_store[namespaced_key] = entry
        logger.debug(f"Memory SET {namespaced_key} (version {entry.version})")
        return entry

    async def get(
        self, key: str, namespace: str = "default", tenant_id: str = "default"
    ) -> Optional[Any]:
        """Retrieve a value from distributed KV memory."""
        namespaced_key = f"{tenant_id}:{namespace}:{key}"
        entry = self._kv_store.get(namespaced_key)
        if not entry:
            return None
        return entry.value

    async def get_entry(
        self, key: str, namespace: str = "default", tenant_id: str = "default"
    ) -> Optional[MemoryEntry]:
        """Retrieve full memory entry with metadata."""
        namespaced_key = f"{tenant_id}:{namespace}:{key}"
        return self._kv_store.get(namespaced_key)

    async def delete(
        self, key: str, namespace: str = "default", tenant_id: str = "default"
    ) -> bool:
        """Delete a key from distributed memory."""
        namespaced_key = f"{tenant_id}:{namespace}:{key}"
        if namespaced_key in self._kv_store:
            del self._kv_store[namespaced_key]
            return True
        return False

    async def list_keys(
        self, namespace: str = "default", tenant_id: str = "default", tag: Optional[str] = None
    ) -> List[str]:
        """List all keys in a namespace."""
        prefix = f"{tenant_id}:{namespace}:"
        keys = [
            e.key
            for k, e in self._kv_store.items()
            if k.startswith(prefix) and (tag is None or tag in e.tags)
        ]
        return keys

    async def acquire_lock(self, key: str, holder_id: str, ttl_seconds: int = 30) -> bool:
        """Acquire a distributed lock on a key."""
        lock_key = f"__lock__:{key}"
        if lock_key in self._locks:
            return False
        self._locks[lock_key] = holder_id
        logger.debug(f"Lock acquired on '{key}' by {holder_id}")
        return True

    async def release_lock(self, key: str, holder_id: str) -> bool:
        """Release a distributed lock."""
        lock_key = f"__lock__:{key}"
        if self._locks.get(lock_key) == holder_id:
            del self._locks[lock_key]
            return True
        return False

    async def publish(self, channel: str, message: Any) -> int:
        """Publish a message to a pub/sub channel."""
        if channel not in self._pub_sub_channels:
            self._pub_sub_channels[channel] = []
        self._pub_sub_channels[channel].append({
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return len(self._pub_sub_channels[channel])

    async def get_messages(self, channel: str, last_n: int = 100) -> List[Any]:
        """Get recent messages from a channel."""
        return self._pub_sub_channels.get(channel, [])[-last_n:]

    # ===== Vector Memory Store (Qdrant-backed) =====

    async def store_vector_memory(
        self,
        content: str,
        embedding: Optional[List[float]] = None,
        namespace: str = "agents",
        tenant_id: str = "default",
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VectorMemoryEntry:
        """Store a semantic memory with vector embedding."""
        # Simulate embedding if not provided (in production: call embedding API)
        if embedding is None:
            embedding = [float(ord(c) % 100) / 100.0 for c in content[:256]]
            embedding = embedding + [0.0] * (256 - len(embedding))

        entry = VectorMemoryEntry(
            content=content,
            embedding=embedding,
            namespace=namespace,
            tenant_id=tenant_id,
            agent_id=agent_id,
            project_id=project_id,
            metadata=metadata or {},
        )
        self._vector_store[entry.id] = entry
        logger.debug(f"Vector memory stored [{entry.id}] in namespace '{namespace}'")
        return entry

    async def semantic_search(
        self,
        query_embedding: List[float],
        namespace: str = "agents",
        tenant_id: str = "default",
        top_k: int = 10,
        score_threshold: float = 0.5,
    ) -> List[VectorMemoryEntry]:
        """Cosine similarity search over vector memories (simulated)."""
        candidates = [
            v for v in self._vector_store.values()
            if v.namespace == namespace and v.tenant_id == tenant_id
        ]

        def cosine_sim(a: List[float], b: List[float]) -> float:
            if len(a) != len(b):
                min_len = min(len(a), len(b))
                a, b = a[:min_len], b[:min_len]
            dot = sum(x * y for x, y in zip(a, b))
            mag_a = sum(x**2 for x in a) ** 0.5
            mag_b = sum(x**2 for x in b) ** 0.5
            return dot / (mag_a * mag_b + 1e-9)

        for entry in candidates:
            entry.similarity_score = cosine_sim(query_embedding, entry.embedding)

        results = sorted(candidates, key=lambda e: e.similarity_score, reverse=True)
        return [r for r in results[:top_k] if r.similarity_score >= score_threshold]

    async def search_by_agent(
        self, agent_id: str, tenant_id: str = "default", limit: int = 50
    ) -> List[VectorMemoryEntry]:
        """Retrieve all vector memories for a specific agent."""
        return [
            v for v in self._vector_store.values()
            if v.agent_id == agent_id and v.tenant_id == tenant_id
        ][:limit]

    async def delete_vector_memory(self, memory_id: str) -> bool:
        if memory_id in self._vector_store:
            del self._vector_store[memory_id]
            return True
        return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """Summary of distributed memory usage."""
        return {
            "kv_entries": len(self._kv_store),
            "vector_entries": len(self._vector_store),
            "active_locks": len(self._locks),
            "pub_sub_channels": len(self._pub_sub_channels),
            "redis_url": self._redis_url,
            "qdrant_url": self._qdrant_url,
        }
