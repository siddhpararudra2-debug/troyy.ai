"""
Sprint 2 Database Models - Engineering Intelligence Core
Extends database/models.py with validation, reasoning, optimization, and reporting models.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, Float, Integer,
    ForeignKey, JSON, Enum as SAEnum, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class TimestampMixin:
    """Mixin for timestamp and audit fields."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)


class ValidationResult(Base, TimestampMixin):
    """Validation result for designs, formulas, and calculations."""
    __tablename__ = "validation_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    validation_type = Column(String(100), nullable=False, index=True)  # formula, physics, design
    target_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Target entity
    is_valid = Column(Boolean, nullable=False, default=True)
    severity = Column(String(50), nullable=False)  # error, warning, info
    
    # Results
    errors = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    metadata = Column(JSONB, default=dict)
    validation_time_ms = Column(Float, nullable=True)
    
    __table_args__ = (
        Index("ix_validation_type_target", "validation_type", "target_id"),
        Index("ix_validation_is_valid", "is_valid"),
    )


class EngineeringReview(Base, TimestampMixin):
    """Engineering design review record."""
    __tablename__ = "engineering_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(String(50), unique=True, nullable=False, index=True)
    design_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    category = Column(String(100), nullable=False)  # design, calculation, safety
    status = Column(String(50), nullable=False, index=True)  # draft, submitted, approved, rejected
    priority = Column(String(50), nullable=False)
    
    # Review content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    design_name = Column(String(255), nullable=True)
    design_version = Column(String(50), nullable=True)
    
    # Reviewers
    primary_reviewer_id = Column(UUID(as_uuid=True), nullable=True)
    primary_reviewer_name = Column(String(255), nullable=True)
    secondary_reviewers = Column(JSON, default=list)
    
    # Results
    overall_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=False, default=False)
    recommendation = Column(Text, nullable=True)
    
    # Comments and feedback
    comments = Column(JSON, default=list)  # Array of comment objects
    comment_count = Column(Integer, default=0)
    
    # Timeline
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_review_design_status", "design_id", "status"),
        Index("ix_review_category_status", "category", "status"),
    )


class Formula(Base, TimestampMixin):
    """Engineering formula in knowledge library."""
    __tablename__ = "formulas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    formula_id = Column(String(50), unique=True, nullable=False, index=True)
    domain = Column(String(100), nullable=False, index=True)  # mechanical, aerospace, thermal
    category = Column(String(100), nullable=False, index=True)
    
    # Formula content
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    formula_latex = Column(Text, nullable=True)
    formula_python = Column(Text, nullable=True)
    
    # Parameters
    input_parameters = Column(JSON, default=list)
    output_parameters = Column(JSON, default=list)
    
    # Metadata
    source = Column(String(255), nullable=True)
    applicability = Column(Text, nullable=True)
    assumptions = Column(JSON, default=list)
    valid_range = Column(JSON, default=dict)
    
    # Quality
    validated = Column(Boolean, default=False)
    accuracy = Column(Float, nullable=True)  # 0-1
    reference = Column(String(500), nullable=True)
    last_verified = Column(DateTime(timezone=True), nullable=True)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_formula_domain_category", "domain", "category"),
        Index("ix_formula_name_domain", "name", "domain"),
    )


class OptimizationRun(Base, TimestampMixin):
    """Record of an optimization run."""
    __tablename__ = "optimization_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = Column(String(50), unique=True, nullable=False, index=True)
    design_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Optimization parameters
    algorithm = Column(String(100), nullable=False)  # genetic, particle_swarm, gradient
    optimization_type = Column(String(100), nullable=False)  # single, multi-objective
    objectives = Column(JSON, default=list)
    variables = Column(JSON, default=list)
    constraints = Column(JSON, default=list)
    
    # Configuration
    max_generations = Column(Integer, nullable=True)
    population_size = Column(Integer, nullable=True)
    
    # Results
    best_solution = Column(JSON, nullable=True)
    best_fitness = Column(Float, nullable=True)
    pareto_front = Column(JSON, default=list)
    
    # Statistics
    generations_completed = Column(Integer, default=0)
    fitness_improvement = Column(Float, nullable=True)  # Percent improvement
    convergence_rate = Column(Float, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_time_seconds = Column(Float, nullable=True)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_optimization_design", "design_id"),
        Index("ix_optimization_algorithm", "algorithm"),
    )


class EngineeringReport(Base, TimestampMixin):
    """Generated engineering report."""
    __tablename__ = "engineering_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(String(50), unique=True, nullable=False, index=True)
    design_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    project_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Report content
    title = Column(String(255), nullable=False)
    report_type = Column(String(100), nullable=False, index=True)  # calculation, design, validation, optimization
    executive_summary = Column(Text, nullable=True)
    
    # Metadata
    design_name = Column(String(255), nullable=True)
    author = Column(String(255), nullable=True)
    version = Column(String(50), default="1.0")
    
    # Report data
    sections = Column(JSON, default=list)
    key_findings = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    assumptions = Column(JSON, default=list)
    limitations = Column(JSON, default=list)
    
    # Quality
    review_status = Column(String(50), default="draft")  # draft, reviewed, approved
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    
    # Attachment
    report_content_markdown = Column(Text, nullable=True)
    report_content_json = Column(JSON, nullable=True)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_report_design", "design_id"),
        Index("ix_report_type", "report_type"),
    )


class ConstraintSet(Base, TimestampMixin):
    """Set of design constraints."""
    __tablename__ = "constraint_sets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Constraints
    constraints = Column(JSON, default=list)  # Array of constraint objects
    constraint_count = Column(Integer, default=0)
    
    # Feasibility
    is_feasible = Column(Boolean, nullable=True)
    feasibility_score = Column(Float, nullable=True)  # 0-1
    violated_constraints = Column(JSON, default=list)
    
    # Analysis
    hard_constraints_satisfied = Column(Boolean, nullable=True)
    soft_constraint_satisfaction = Column(Float, nullable=True)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_constraints_design", "design_id"),
        Index("ix_constraints_feasible", "is_feasible"),
    )


class AssumptionSet(Base, TimestampMixin):
    """Set of assumptions for a design."""
    __tablename__ = "assumption_sets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Assumptions
    assumptions = Column(JSON, default=list)  # Array of assumption objects
    assumption_count = Column(Integer, default=0)
    
    # Validation
    validations = Column(JSON, default=list)  # Validation results
    overall_risk = Column(String(50), default="medium")  # low, medium, high, critical
    requires_validation_count = Column(Integer, default=0)
    
    design_name = Column(String(255), nullable=True)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_assumption_design", "design_id"),
        Index("ix_assumption_risk", "overall_risk"),
    )


class EngineringWorkflow(Base, TimestampMixin):
    """Engineering workflow execution record."""
    __tablename__ = "engineering_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(50), unique=True, nullable=False, index=True)
    design_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    project_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Workflow definition
    design_name = Column(String(255), nullable=True)
    stages = Column(JSON, default=list)  # Pipeline stages
    step_count = Column(Integer, default=0)
    
    # Execution
    status = Column(String(50), nullable=False, index=True)  # created, running, completed, failed
    current_stage = Column(Integer, default=0)
    
    # Configuration
    skip_validation = Column(Boolean, default=False)
    skip_optimization = Column(Boolean, default=False)
    parallel_execution = Column(Boolean, default=False)
    
    # Results
    final_design = Column(JSON, nullable=True)
    design_metrics = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    
    # Steps
    steps = Column(JSON, default=list)  # Step details
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_duration_seconds = Column(Float, nullable=True)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_workflow_design_status", "design_id", "status"),
        Index("ix_workflow_status", "status"),
    )


class TradeoffAnalysis(Base, TimestampMixin):
    """Trade-off analysis record."""
    __tablename__ = "tradeoff_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    design_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Trade-off dimensions
    dimensions = Column(JSON, default=list)  # Trade-off dimensions analyzed
    
    # Points and frontier
    points = Column(JSON, default=list)  # All design points
    pareto_frontier = Column(JSON, default=list)  # Pareto-optimal points
    sweet_spot = Column(JSON, nullable=True)  # Recommended balanced solution
    
    # Conflicts
    constraint_conflicts = Column(JSON, default=list)
    conflict_count = Column(Integer, default=0)
    
    # Recommendations
    recommendations = Column(JSON, default=list)
    
    metadata = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index("ix_tradeoff_design", "design_id"),
    )
