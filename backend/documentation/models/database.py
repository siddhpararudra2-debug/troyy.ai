from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class ReportType(str, enum.Enum):
    CALCULATION = "CALCULATION"
    DESIGN = "DESIGN"
    VALIDATION = "VALIDATION"
    RISK = "RISK"
    PROJECT_SUMMARY = "PROJECT_SUMMARY"

class KnowledgeCategory(str, enum.Enum):
    LESSON_LEARNED = "LESSON_LEARNED"
    BEST_PRACTICE = "BEST_PRACTICE"
    COMMON_FAILURE = "COMMON_FAILURE"
    SUCCESSFUL_DESIGN = "SUCCESSFUL_DESIGN"
    ENGINEERING_INSIGHT = "ENGINEERING_INSIGHT"

class ProjectReport(Base):
    __tablename__ = "project_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType))
    title: Mapped[str] = mapped_column(String)
    content: Mapped[dict] = mapped_column(JSON) # Structured report data
    generated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relationships
    calculations: Mapped[List["CalculationReport"]] = relationship(back_populates="project_report")
    decisions: Mapped[List["DecisionLog"]] = relationship(back_populates="project_report")

class CalculationReport(Base):
    __tablename__ = "calculation_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_report_id: Mapped[int] = mapped_column(Integer, ForeignKey("project_reports.id"))
    problem_statement: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str] = mapped_column(Text)
    known_variables: Mapped[dict] = mapped_column(JSON)
    unknown_variables: Mapped[dict] = mapped_column(JSON)
    assumptions: Mapped[str] = mapped_column(Text)
    formula_selection: Mapped[str] = mapped_column(Text)
    formula_explanation: Mapped[str] = mapped_column(Text)
    unit_analysis: Mapped[str] = mapped_column(Text)
    substitution_steps: Mapped[str] = mapped_column(Text)
    intermediate_calculations: Mapped[dict] = mapped_column(JSON)
    final_results: Mapped[dict] = mapped_column(JSON)
    verification_results: Mapped[str] = mapped_column(Text)
    engineering_interpretation: Mapped[str] = mapped_column(Text)
    recommendations: Mapped[str] = mapped_column(Text)
    
    project_report: Mapped["ProjectReport"] = relationship(back_populates="calculations")

class DesignReport(Base):
    __tablename__ = "design_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_report_id: Mapped[int] = mapped_column(Integer, ForeignKey("project_reports.id"))
    design_objective: Mapped[str] = mapped_column(Text)
    system_architecture: Mapped[str] = mapped_column(Text)
    design_decisions: Mapped[dict] = mapped_column(JSON)
    component_selections: Mapped[dict] = mapped_column(JSON)
    subsystems: Mapped[dict] = mapped_column(JSON)
    constraints: Mapped[str] = mapped_column(Text)
    engineering_tradeoffs: Mapped[str] = mapped_column(Text)
    final_design_summary: Mapped[str] = mapped_column(Text)

class DecisionLog(Base):
    __tablename__ = "decision_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_report_id: Mapped[int] = mapped_column(Integer, ForeignKey("project_reports.id"))
    project_id: Mapped[str] = mapped_column(String, index=True)
    decision_title: Mapped[str] = mapped_column(String)
    decision_description: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str] = mapped_column(Text)
    benefits: Mapped[str] = mapped_column(Text)
    risks: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    project_report: Mapped["ProjectReport"] = relationship(back_populates="decisions")

class ProjectHistory(Base):
    __tablename__ = "project_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, default=datetime.utcnow)
    event_type: Mapped[str] = mapped_column(String) # e.g., "REQUIREMENT_CHANGE", "CALCULATION_UPDATE"
    details: Mapped[dict] = mapped_column(JSON)
    actor: Mapped[str] = mapped_column(String, default="SYSTEM")

class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[KnowledgeCategory] = mapped_column(Enum(KnowledgeCategory))
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(Text)
    tags: Mapped[List[str]] = mapped_column(JSON)
    source_project_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class DocumentTemplate(Base):
    __tablename__ = "document_templates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain: Mapped[str] = mapped_column(String, index=True) # AEROSPACE, UAV, ROBOTICS, etc.
    template_type: Mapped[str] = mapped_column(String) # CALCULATION, DESIGN, etc.
    content: Mapped[str] = mapped_column(Text) # Jinja2 template string
    version: Mapped[str] = mapped_column(String, default="1.0")
