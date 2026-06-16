"""
Troy — Validation Service
Orchestrates execution of the modular engineering validators.
"""

from __future__ import annotations

import asyncio
import logging
from typing import List

from app.solver.models.domain_models import SolverState
from app.validation.schemas.validation_schemas import ValidationReportResponse, ValidationIssueSchema
from app.validation.services.base import AsyncBaseValidator
from app.validation.services.requirements_validator import RequirementsValidator
from app.validation.services.assumptions_validator import AssumptionsValidator
from app.validation.services.formula_validator import FormulaValidator
from app.validation.services.unit_validator import UnitValidator
from app.validation.services.calculation_validator import CalculationValidator
from app.validation.services.safety_factor_validator import SafetyFactorValidator

logger = logging.getLogger("validation.service")


class ValidationService:
    """Orchestrator for running all automated engineering verification checks."""

    def __init__(self, validators: List[AsyncBaseValidator] = None) -> None:
        if validators is not None:
            self.validators = list(validators)
        else:
            self.validators = [
                RequirementsValidator(),
                AssumptionsValidator(),
                FormulaValidator(),
                UnitValidator(),
                CalculationValidator(),
                SafetyFactorValidator(),
            ]

    def register_validator(self, validator: AsyncBaseValidator) -> None:
        """Register a new validator to the service pool."""
        self.validators.append(validator)
        logger.info(f"Registered validator: {validator.name}")

    async def validate(self, state: SolverState) -> List[ValidationIssueSchema]:
        """Execute all validators concurrently and gather the list of issues."""
        logger.info(f"Starting concurrent validation run of {len(self.validators)} validators")
        
        tasks = [validator.validate(state) for validator in self.validators]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_issues: List[ValidationIssueSchema] = []
        
        for idx, result in enumerate(results):
            validator_name = self.validators[idx].name
            if isinstance(result, Exception):
                logger.error(f"Validator {validator_name} failed with exception: {result}", exc_info=True)
                all_issues.append(
                    ValidationIssueSchema(
                        severity="error",
                        category="System",
                        message=f"Validator {validator_name} crashed during execution: {str(result)}",
                        validator_name=validator_name,
                        engineering_reasoning="Internal software exception occurred.",
                        recommendation="Check logs to debug internal code error.",
                    )
                )
            else:
                all_issues.extend(result)
                
        return all_issues
