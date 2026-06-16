"""
Troy — Base Validator Service
Abstract base class for all validation service modules.
"""

from __future__ import annotations

import logging
from typing import List
from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationIssueSchema


class AsyncBaseValidator:
    """Base interface for all domain and calculation verification modules."""

    name: str = "BaseValidator"

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"validation.services.{self.name.lower()}")

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        """
        Evaluate the SolverState and return a list of Pydantic validation issues.
        Override this method in concrete validation sub-classes.
        """
        raise NotImplementedError
