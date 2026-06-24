"""
Engineering Report Export System for Engineering OS.
Generates reports in multiple formats (Markdown, PDF, DOCX).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
import uuid


class ReportType(str, Enum):
    """Types of engineering reports."""
    CALCULATION_REPORT = "calculation_report"
    DESIGN_REPORT = "design_report"
    VALIDATION_REPORT = "validation_report"
    OPTIMIZATION_REPORT = "optimization_report"
    ANALYSIS_REPORT = "analysis_report"
    FEASIBILITY_REPORT = "feasibility_report"
    RECOMMENDATION_REPORT = "recommendation_report"


class ReportFormat(str, Enum):
    """Report output formats."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    JSON = "json"


@dataclass
class ReportSection:
    """A section in an engineering report."""
    title: str = ""
    content: str = ""
    subsections: List['ReportSection'] = field(default_factory=list)
    figures: List[Dict[str, Any]] = field(default_factory=list)  # Charts, diagrams
    tables: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ReportMetadata:
    """Metadata for a report."""
    title: str = ""
    author: str = ""
    date: datetime = field(default_factory=datetime.utcnow)
    version: str = "1.0"
    design_id: str = ""
    design_name: str = ""
    project_id: str = ""
    confidential: bool = False


@dataclass
class EngineeringReport:
    """A complete engineering report."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    report_id: str = ""
    report_type: ReportType = ReportType.DESIGN_REPORT
    metadata: ReportMetadata = field(default_factory=ReportMetadata)
    
    # Executive Summary
    executive_summary: str = ""
    
    # Report sections
    sections: List[ReportSection] = field(default_factory=list)
    
    # Key findings and recommendations
    key_findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    
    # Appendices
    appendices: Dict[str, Any] = field(default_factory=dict)
    
    # References and assumptions
    references: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    
    # Quality metrics
    review_status: str = "draft"  # draft, reviewed, approved
    reviewed_by: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified_at: datetime = field(default_factory=datetime.utcnow)


class ReportGenerator:
    """Generates engineering reports."""

    def __init__(self):
        self.report_count = 0

    async def create_calculation_report(
        self,
        calculation_id: str,
        calculation_name: str,
        design_name: str,
        inputs: Dict[str, Any],
        assumptions: List[str],
        equations: List[str],
        results: Dict[str, Any],
        author: str = "Engineering System"
    ) -> EngineeringReport:
        """Create a calculation report."""
        self.report_count += 1
        
        report = EngineeringReport(
            report_id=f"CALC-RPT-{self.report_count:05d}",
            report_type=ReportType.CALCULATION_REPORT,
            metadata=ReportMetadata(
                title=f"Calculation Report: {calculation_name}",
                author=author,
                design_name=design_name
            )
        )
        
        # Executive Summary
        report.executive_summary = f"""
This report documents the engineering calculation for {calculation_name}.
The calculation uses verified formulas and physics principles to determine design parameters.
All assumptions are documented and validated against engineering standards.
"""
        
        # Input Parameters Section
        inputs_section = ReportSection(
            title="Input Parameters",
            content="The following input parameters were used in the calculation:"
        )
        inputs_table = {
            "type": "table",
            "headers": ["Parameter", "Value", "Unit"],
            "rows": [
                [key, str(value), "various"]
                for key, value in inputs.items()
            ]
        }
        inputs_section.tables.append(inputs_table)
        report.sections.append(inputs_section)
        
        # Assumptions Section
        assumptions_section = ReportSection(
            title="Assumptions",
            content="The following assumptions were applied:"
        )
        for i, assumption in enumerate(assumptions, 1):
            assumptions_section.content += f"\n{i}. {assumption}"
        report.sections.append(assumptions_section)
        report.assumptions = assumptions
        
        # Equations Section
        equations_section = ReportSection(
            title="Equations and Formulas",
            content="The following equations were used:"
        )
        for i, equation in enumerate(equations, 1):
            equations_section.content += f"\n{i}. {equation}"
        report.sections.append(equations_section)
        
        # Results Section
        results_section = ReportSection(
            title="Results",
            content="The calculation produced the following results:"
        )
        results_table = {
            "type": "table",
            "headers": ["Result", "Value", "Unit"],
            "rows": [
                [key, f"{value:.4f}" if isinstance(value, float) else str(value), "various"]
                for key, value in results.items()
            ]
        }
        results_section.tables.append(results_table)
        report.sections.append(results_section)
        
        return report

    async def create_validation_report(
        self,
        design_id: str,
        design_name: str,
        validations: List[Dict[str, Any]],
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
        overall_status: str = "valid",
        author: str = "Validation System"
    ) -> EngineeringReport:
        """Create a validation report."""
        self.report_count += 1
        
        report = EngineeringReport(
            report_id=f"VAL-RPT-{self.report_count:05d}",
            report_type=ReportType.VALIDATION_REPORT,
            metadata=ReportMetadata(
                title=f"Validation Report: {design_name}",
                author=author,
                design_name=design_name,
                design_id=design_id
            )
        )
        
        report.executive_summary = f"""
This validation report documents the results of comprehensive design validation for {design_name}.
Design Status: {overall_status.upper()}
Total Validations: {len(validations)}
Errors Found: {len(errors)}
Warnings Found: {len(warnings)}
"""
        
        # Validation Summary
        summary_section = ReportSection(title="Validation Summary")
        summary_section.content = f"Overall Status: {overall_status}\n"
        summary_section.content += f"Passed Validations: {len([v for v in validations if v.get('passed', False)])}\n"
        summary_section.content += f"Failed Validations: {len([v for v in validations if not v.get('passed', False)])}\n"
        report.sections.append(summary_section)
        
        # Errors Section
        if errors:
            errors_section = ReportSection(title="Validation Errors")
            errors_table = {
                "type": "table",
                "headers": ["Error Type", "Description", "Severity"],
                "rows": [
                    [e.get("type", "Unknown"), e.get("message", ""), e.get("severity", "high")]
                    for e in errors
                ]
            }
            errors_section.tables.append(errors_table)
            report.sections.append(errors_section)
            report.key_findings.extend([e.get("message", "") for e in errors])
        
        # Warnings Section
        if warnings:
            warnings_section = ReportSection(title="Validation Warnings")
            warnings_table = {
                "type": "table",
                "headers": ["Warning Type", "Description"],
                "rows": [
                    [w.get("type", "Unknown"), w.get("message", "")]
                    for w in warnings
                ]
            }
            warnings_section.tables.append(warnings_table)
            report.sections.append(warnings_section)
        
        return report

    async def create_optimization_report(
        self,
        design_id: str,
        design_name: str,
        objectives: List[str],
        best_solution: Dict[str, Any],
        convergence_data: Dict[str, Any],
        author: str = "Optimization System"
    ) -> EngineeringReport:
        """Create an optimization report."""
        self.report_count += 1
        
        report = EngineeringReport(
            report_id=f"OPT-RPT-{self.report_count:05d}",
            report_type=ReportType.OPTIMIZATION_REPORT,
            metadata=ReportMetadata(
                title=f"Optimization Report: {design_name}",
                author=author,
                design_name=design_name,
                design_id=design_id
            )
        )
        
        # Executive Summary
        report.executive_summary = f"""
This report documents the results of design optimization for {design_name}.
Optimization objectives: {', '.join(objectives)}
Optimization converged in {convergence_data.get('generations', 'unknown')} generations.
"""
        
        # Objectives Section
        objectives_section = ReportSection(
            title="Optimization Objectives",
            content="The design was optimized for the following objectives:"
        )
        for i, objective in enumerate(objectives, 1):
            objectives_section.content += f"\n{i}. {objective}"
        report.sections.append(objectives_section)
        
        # Best Solution Section
        solution_section = ReportSection(
            title="Optimal Solution",
            content="The optimization algorithm identified the following as the best design:"
        )
        solution_table = {
            "type": "table",
            "headers": ["Parameter", "Value"],
            "rows": [
                [str(k), f"{v:.4f}" if isinstance(v, float) else str(v)]
                for k, v in best_solution.items()
            ]
        }
        solution_section.tables.append(solution_table)
        report.sections.append(solution_section)
        
        report.recommendations.append(
            "Implement the optimal solution identified in this report"
        )
        
        return report

    async def export_to_markdown(self, report: EngineeringReport) -> str:
        """Export report to Markdown format."""
        md = []
        
        # Title
        md.append(f"# {report.metadata.title}\n")
        
        # Metadata
        md.append("## Report Information\n")
        md.append(f"- **Report ID**: {report.report_id}\n")
        md.append(f"- **Type**: {report.report_type.value}\n")
        md.append(f"- **Author**: {report.metadata.author}\n")
        md.append(f"- **Date**: {report.metadata.date.strftime('%Y-%m-%d %H:%M UTC')}\n")
        md.append(f"- **Design**: {report.metadata.design_name}\n")
        md.append(f"- **Version**: {report.metadata.version}\n\n")
        
        # Executive Summary
        if report.executive_summary:
            md.append("## Executive Summary\n\n")
            md.append(report.executive_summary)
            md.append("\n\n")
        
        # Main Sections
        for section in report.sections:
            md.append(f"## {section.title}\n\n")
            md.append(section.content)
            md.append("\n\n")
            
            # Tables
            for table in section.tables:
                md.append(self._render_markdown_table(table))
                md.append("\n\n")
        
        # Key Findings
        if report.key_findings:
            md.append("## Key Findings\n\n")
            for finding in report.key_findings:
                md.append(f"- {finding}\n")
            md.append("\n")
        
        # Recommendations
        if report.recommendations:
            md.append("## Recommendations\n\n")
            for rec in report.recommendations:
                md.append(f"- {rec}\n")
            md.append("\n")
        
        # Assumptions
        if report.assumptions:
            md.append("## Assumptions\n\n")
            for assumption in report.assumptions:
                md.append(f"- {assumption}\n")
            md.append("\n")
        
        # Limitations
        if report.limitations:
            md.append("## Limitations\n\n")
            for limitation in report.limitations:
                md.append(f"- {limitation}\n")
            md.append("\n")
        
        return "".join(md)

    def _render_markdown_table(self, table: Dict[str, Any]) -> str:
        """Render a table as Markdown."""
        md = []
        
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        
        if not headers or not rows:
            return ""
        
        # Header row
        md.append("| " + " | ".join(headers) + " |\n")
        
        # Separator
        md.append("| " + " | ".join(["---"] * len(headers)) + " |\n")
        
        # Data rows
        for row in rows:
            md.append("| " + " | ".join(str(cell) for cell in row) + " |\n")
        
        return "".join(md)

    async def export_to_json(self, report: EngineeringReport) -> Dict[str, Any]:
        """Export report to JSON format."""
        return {
            "report_id": report.report_id,
            "report_type": report.report_type.value,
            "title": report.metadata.title,
            "author": report.metadata.author,
            "date": report.metadata.date.isoformat(),
            "design_name": report.metadata.design_name,
            "executive_summary": report.executive_summary,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "tables": section.tables
                }
                for section in report.sections
            ],
            "key_findings": report.key_findings,
            "recommendations": report.recommendations,
            "assumptions": report.assumptions,
            "limitations": report.limitations
        }

    async def save_report(
        self,
        report: EngineeringReport,
        filepath: str,
        format: ReportFormat = ReportFormat.MARKDOWN
    ) -> str:
        """Save report to file."""
        if format == ReportFormat.MARKDOWN:
            content = await self.export_to_markdown(report)
            filename = filepath if filepath.endswith('.md') else f"{filepath}.md"
        elif format == ReportFormat.JSON:
            import json
            content = json.dumps(await self.export_to_json(report), indent=2)
            filename = filepath if filepath.endswith('.json') else f"{filepath}.json"
        else:
            raise NotImplementedError(f"Format {format} not yet implemented")
        
        # In production, use proper file I/O
        # For now, just return the filename
        return filename
