"""
Sprint 12 — Execution Router
Intelligent routing of agent tasks based on capability, load, and locality.
Supports failover and retry with circuit breaker pattern.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RoutingStrategy(str, Enum):
    CAPABILITY = "capability"      # Route by agent capability match
    LEAST_LOADED = "least_loaded"  # Route to least busy worker
    LOCALITY = "locality"          # Route to closest region
    ROUND_ROBIN = "round_robin"    # Equal distribution
    STICKY = "sticky"              # Affinity to same worker for session


class CircuitState(str, Enum):
    CLOSED = "closed"    # Normal operation
    OPEN = "open"        # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """Circuit breaker for worker failure isolation."""
    worker_id: str = ""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    last_failure_time: Optional[float] = None

    def record_success(self) -> None:
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(f"Circuit breaker for worker {self.worker_id} CLOSED (recovered)")

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker for worker {self.worker_id} OPEN ({self.failure_count} failures)")

    def can_attempt(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker for worker {self.worker_id} HALF_OPEN (testing recovery)")
                return True
            return False
        return True  # HALF_OPEN: allow one attempt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
        }


@dataclass
class RouteRecord:
    """Records a routing decision."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    target_worker_id: str = ""
    strategy_used: RoutingStrategy = RoutingStrategy.CAPABILITY
    latency_estimate_ms: float = 0.0
    region: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    success: bool = True
    retry_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "target_worker_id": self.target_worker_id,
            "strategy_used": self.strategy_used.value,
            "latency_estimate_ms": self.latency_estimate_ms,
            "region": self.region,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "retry_count": self.retry_count,
        }


class ExecutionRouter:
    """
    Routes agent execution requests to optimal workers using configurable
    strategies with circuit breaker protection and retry logic.
    """

    def __init__(self, default_strategy: RoutingStrategy = RoutingStrategy.LEAST_LOADED):
        self._workers: Dict[str, Dict[str, Any]] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._routes: List[RouteRecord] = []
        self._round_robin_index: int = 0
        self._sticky_sessions: Dict[str, str] = {}  # session_id -> worker_id
        self._default_strategy = default_strategy
        self._region_latency: Dict[str, float] = {
            "us-east-1": 10.0,
            "us-west-2": 70.0,
            "eu-west-1": 100.0,
            "ap-southeast-1": 150.0,
        }

    def register_worker(
        self,
        worker_id: str,
        capabilities: List[str],
        load_factor: float = 0.0,
        region: str = "us-east-1",
        is_healthy: bool = True,
    ) -> None:
        """Register a worker with the router."""
        self._workers[worker_id] = {
            "id": worker_id,
            "capabilities": set(capabilities),
            "load_factor": load_factor,
            "region": region,
            "is_healthy": is_healthy,
        }
        self._circuit_breakers[worker_id] = CircuitBreaker(worker_id=worker_id)
        logger.debug(f"Worker {worker_id} registered with router in {region}")

    def update_worker_load(self, worker_id: str, load_factor: float) -> None:
        """Update worker load factor for routing decisions."""
        if worker_id in self._workers:
            self._workers[worker_id]["load_factor"] = load_factor

    def _get_available_workers(self, capability: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get workers that are healthy and pass circuit breaker check."""
        workers = []
        for wid, info in self._workers.items():
            if not info["is_healthy"]:
                continue
            cb = self._circuit_breakers.get(wid)
            if cb and not cb.can_attempt():
                continue
            if capability and capability not in info["capabilities"]:
                continue
            workers.append(info)
        return workers

    def _route_least_loaded(self, workers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not workers:
            return None
        return min(workers, key=lambda w: w["load_factor"])

    def _route_round_robin(self, workers: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not workers:
            return None
        worker = workers[self._round_robin_index % len(workers)]
        self._round_robin_index += 1
        return worker

    def _route_locality(self, workers: List[Dict[str, Any]], preferred_region: str) -> Optional[Dict[str, Any]]:
        if not workers:
            return None
        # Prefer same region, then lowest latency
        same_region = [w for w in workers if w["region"] == preferred_region]
        if same_region:
            return min(same_region, key=lambda w: w["load_factor"])
        return min(workers, key=lambda w: self._region_latency.get(w["region"], 999.0))

    async def route(
        self,
        agent_id: str,
        capability: Optional[str] = None,
        strategy: Optional[RoutingStrategy] = None,
        preferred_region: str = "us-east-1",
        session_id: Optional[str] = None,
        max_retries: int = 3,
    ) -> RouteRecord:
        """Route an agent to the best available worker."""
        strategy = strategy or self._default_strategy
        retry_count = 0

        while retry_count <= max_retries:
            available = self._get_available_workers(capability)
            if not available:
                raise RuntimeError(f"No available workers for capability '{capability}'")

            # Sticky session routing
            if strategy == RoutingStrategy.STICKY and session_id:
                sticky_worker_id = self._sticky_sessions.get(session_id)
                if sticky_worker_id and sticky_worker_id in {w["id"] for w in available}:
                    worker = next(w for w in available if w["id"] == sticky_worker_id)
                else:
                    worker = self._route_least_loaded(available)
                    if worker and session_id:
                        self._sticky_sessions[session_id] = worker["id"]
            elif strategy == RoutingStrategy.LEAST_LOADED:
                worker = self._route_least_loaded(available)
            elif strategy == RoutingStrategy.ROUND_ROBIN:
                worker = self._route_round_robin(available)
            elif strategy == RoutingStrategy.LOCALITY:
                worker = self._route_locality(available, preferred_region)
            else:
                worker = self._route_least_loaded(available)

            if worker:
                latency = self._region_latency.get(worker["region"], 50.0)
                route = RouteRecord(
                    agent_id=agent_id,
                    target_worker_id=worker["id"],
                    strategy_used=strategy,
                    latency_estimate_ms=latency,
                    region=worker["region"],
                    retry_count=retry_count,
                )
                self._routes.append(route)
                logger.debug(f"Agent {agent_id} routed to worker {worker['id']} via {strategy.value}")
                return route

            retry_count += 1
            await asyncio.sleep(0.01 * retry_count)

        raise RuntimeError(f"Routing failed after {max_retries} retries for agent {agent_id}")

    def record_execution_result(self, worker_id: str, success: bool) -> None:
        """Record execution result for circuit breaker tracking."""
        cb = self._circuit_breakers.get(worker_id)
        if cb:
            if success:
                cb.record_success()
            else:
                cb.record_failure()

    def get_circuit_breaker_status(self) -> List[Dict[str, Any]]:
        return [cb.to_dict() for cb in self._circuit_breakers.values()]

    def get_routing_stats(self) -> Dict[str, Any]:
        successful = sum(1 for r in self._routes if r.success)
        failed = len(self._routes) - successful
        avg_latency = (
            sum(r.latency_estimate_ms for r in self._routes) / len(self._routes)
            if self._routes else 0.0
        )
        return {
            "total_routes": len(self._routes),
            "successful_routes": successful,
            "failed_routes": failed,
            "average_latency_ms": round(avg_latency, 2),
            "active_workers": len(self._workers),
            "circuit_breakers_open": sum(
                1 for cb in self._circuit_breakers.values() if cb.state == CircuitState.OPEN
            ),
        }

    def get_routing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._routes[-limit:]]
