"""
Troy — Base Validator
Abstract class for all modular validators.
"""
from __future__ import annotations
from typing import List
import logging

from app.solver.models import SolverState
from app.validation.models import ValidationIssue

class AsyncBaseValidator:
    name: str = "BaseValidator"
    
    def __init__(self):
        self.logger = logging.getLogger(f"validation.validators.{self.name.lower()}")
        
    async def validate(self, state: SolverState) -> List[ValidationIssue]:
        """
        Evaluate the SolverState and return a list of ValidationIssues.
        Override this method in concrete validators.
        """
        raise NotImplementedError
