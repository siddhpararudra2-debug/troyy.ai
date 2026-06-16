"""
Troy — Validation Models
Schemas for the ValidationService.
"""
from pydantic import BaseModel, Field
from typing import List

class ValidationIssue(BaseModel):
    severity: str  # "warning", "error", "info"
    category: str  # e.g., "Assumptions", "Safety", "Requirements", "Values"
    message: str
    validator_name: str

class ValidationReport(BaseModel):
    issues: List[ValidationIssue] = Field(default_factory=list)
    total_errors: int = 0
    total_warnings: int = 0
    is_approved: bool = True
