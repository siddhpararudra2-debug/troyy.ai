"""
Troy — Base Engine
Abstract base class for all solver engines in the pipeline.
"""
from __future__ import annotations

import time
import logging
from app.solver.models import SolverState

class BaseEngine:
    name: str = "BaseEngine"

    def __init__(self):
        self.logger = logging.getLogger(f"solver.engines.{self.name.lower()}")

    async def process(self, state: SolverState) -> SolverState:
        """Process the state through this engine."""
        self.logger.info(f"[{self.name}] Starting execution...")
        start_time = time.perf_counter()
        
        try:
            state = await self._execute(state)
        except Exception as e:
            self.logger.error(f"[{self.name}] Failed: {str(e)}")
            state.errors.append(f"[{self.name}] {str(e)}")
            
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        state.step_latencies_ms[self.name] = elapsed_ms
        self.logger.info(f"[{self.name}] Completed in {elapsed_ms:.2f}ms")
        
        return state

    async def _execute(self, state: SolverState) -> SolverState:
        """Override this method in subclasses."""
        raise NotImplementedError
