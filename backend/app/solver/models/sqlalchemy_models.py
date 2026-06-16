"""
Troy — Solver SQLAlchemy ORM Models
Relational models for persisting solver sessions, runs, requirements,
assumptions, constraints, variables, and recommendations.

Tables are created via raw SQL in app/main.py (consistent with the rest
of the codebase which uses raw-SQL DDL + async sessions).  These ORM
models exist so that the repository layer can use relationship-aware
queries when needed, but day-to-day persistence uses ``sqlalchemy.text``.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ── Session ──────────────────────────────────────────────────────
class SolverSessionORM(Base):
    """A user-initiated solver session (may contain multiple runs)."""

    __tablename__ = "solver_sessions"

    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    user_query = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    runs = relationship(
        "SolverRunORM", back_populates="session", cascade="all, delete-orphan"
    )


# ── Run ──────────────────────────────────────────────────────────
class SolverRunORM(Base):
    """A single execution of the full solver pipeline."""

    __tablename__ = "solver_runs"

    id = Column(String, primary_key=True)
    session_id = Column(
        String,
        ForeignKey("solver_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    domain = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    execution_time_ms = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SolverSessionORM", back_populates="runs")
    requirements = relationship(
        "SolverRequirementORM",
        back_populates="run",
        uselist=False,
        cascade="all, delete-orphan",
    )
    assumptions = relationship(
        "SolverAssumptionORM", back_populates="run", cascade="all, delete-orphan"
    )
    constraints = relationship(
        "SolverConstraintORM", back_populates="run", cascade="all, delete-orphan"
    )
    variables = relationship(
        "SolverVariableORM", back_populates="run", cascade="all, delete-orphan"
    )
    recommendations = relationship(
        "SolverRecommendationORM", back_populates="run", cascade="all, delete-orphan"
    )


# ── Requirement ──────────────────────────────────────────────────
class SolverRequirementORM(Base):
    """Extracted requirements for a single solver run."""

    __tablename__ = "solver_requirements"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("solver_runs.id", ondelete="CASCADE"), nullable=False
    )
    project_type = Column(String, nullable=True)
    mission_type = Column(String, nullable=True)
    payload = Column(String, nullable=True)
    flight_time = Column(String, nullable=True)
    missing_requirements = Column(String, nullable=True)  # JSON list
    raw_extracted = Column(String, nullable=True)  # JSON dict

    run = relationship("SolverRunORM", back_populates="requirements")


# ── Assumption ───────────────────────────────────────────────────
class SolverAssumptionORM(Base):
    """A generated assumption for a solver run."""

    __tablename__ = "solver_assumptions"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("solver_runs.id", ondelete="CASCADE"), nullable=False
    )
    missing_information = Column(String, nullable=False)
    assumption = Column(String, nullable=False)
    reasoning = Column(String, nullable=False)
    confidence_score = Column(String, nullable=False)
    editable = Column(Boolean, default=True)
    user_override = Column(String, nullable=True)

    run = relationship("SolverRunORM", back_populates="assumptions")


# ── Constraint ───────────────────────────────────────────────────
class SolverConstraintORM(Base):
    """An identified engineering constraint for a solver run."""

    __tablename__ = "solver_constraints"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("solver_runs.id", ondelete="CASCADE"), nullable=False
    )
    category = Column(String, nullable=False)
    limit_value = Column(String, nullable=False)
    source = Column(String, nullable=False)

    run = relationship("SolverRunORM", back_populates="constraints")


# ── Variable ─────────────────────────────────────────────────────
class SolverVariableORM(Base):
    """A single engineering variable extracted for a solver run."""

    __tablename__ = "solver_variables"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("solver_runs.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    description = Column(String, nullable=True)
    var_type = Column(String, nullable=False)  # known | unknown | derived | constant

    run = relationship("SolverRunORM", back_populates="variables")


# ── Recommendation ───────────────────────────────────────────────
class SolverRecommendationORM(Base):
    """An engineering recommendation produced by a solver run."""

    __tablename__ = "solver_recommendations"

    id = Column(String, primary_key=True)
    run_id = Column(
        String, ForeignKey("solver_runs.id", ondelete="CASCADE"), nullable=False
    )
    recommendation = Column(String, nullable=False)
    reasoning = Column(String, nullable=False)
    expected_benefits = Column(String, nullable=True)
    potential_risks = Column(String, nullable=True)

    run = relationship("SolverRunORM", back_populates="recommendations")
