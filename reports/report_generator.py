"""
Report generation for Engineering OS.
Generates engineering reports in markdown, PDF, and DOCX formats.
"""
from datetime import datetime
from typing import Optional
from calculations.calculation_engine import CalculationResult


class ReportGenerator:
    """Generates engineering reports from calculations and analyses."""

    def __init__(self):
        self.report_id = 0

    async def generate_calculation_report(self, calc_result: CalculationResult) -> str:
        """Generate a markdown report from a calculation result."""
        self.report_id += 1
        report = []
        
        report.append(f"# Engineering Calculation Report\n")
        report.append(f"**Report ID:** RPT-{self.report_id:04d}\n")
        report.append(f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
        report.append(f"**Title:** {calc_result.title}\n")
        report.append(f"**Formula ID:** {calc_result.formula_id}\n")
        report.append(f"**Execution Time:** {calc_result.execution_time_ms:.2f} ms\n")
        report.append("\n---\n")
        
        if calc_result.error:
            report.append(f"## ⚠ Error\n\n{calc_result.error}\n")
            return "\n".join(report)
        
        # Formula
        if calc_result.formula:
            report.append(f"## Formula\n\n$${calc_result.formula.formula_latex}$$\n\n")
            report.append(f"**{calc_result.formula.name}** — {calc_result.formula.description}\n\n")
        
        # Steps
        report.append("## Calculation Steps\n\n")
        for step in calc_result.steps:
            report.append(f"### Step {step.order}: {step.step_type.title()}\n")
            report.append(f"{step.description}\n\n")
            if step.formula:
                report.append(f"Formula: `${step.formula}$`\n\n")
            if step.values:
                report.append(f"Values: `{step.values}`\n\n")
            if step.result:
                report.append(f"**Result:** {step.result}\n\n")
        
        # Results
        report.append("## Results\n\n")
        report.append("| Symbol | Value |\n|--------|-------|\n")
        for symbol, formatted in calc_result.results_formatted.items():
            report.append(f"| {symbol} | {formatted} |\n")
        
        # Assumptions
        if calc_result.assumptions:
            report.append("\n## Assumptions\n\n")
            for a in calc_result.assumptions:
                report.append(f"- {a}\n")
        
        # Warnings
        if calc_result.warnings:
            report.append("\n## Warnings\n\n")
            for w in calc_result.warnings:
                report.append(f"- ⚠ {w}\n")
        
        # LaTeX Summary
        if calc_result.latex_summary:
            report.append("\n## LaTeX Summary\n\n")
            report.append(f"$${calc_result.latex_summary}$$\n")
        
        return "\n".join(report)

    async def generate_design_report(self, title: str, sections: list[dict]) -> str:
        """Generate a design report from sections."""
        report = [f"# {title}\n"]
        report.append(f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n---\n")
        
        for section in sections:
            report.append(f"## {section.get('heading', 'Section')}\n\n")
            report.append(f"{section.get('content', '')}\n\n")
            if 'subsections' in section:
                for sub in section['subsections']:
                    report.append(f"### {sub.get('heading', '')}\n\n")
                    report.append(f"{sub.get('content', '')}\n\n")
        
        return "\n".join(report)

    async def export_markdown(self, content: str, filename: str) -> str:
        """Export report as markdown file."""
        import os
        path = f"outputs/{filename}"
        os.makedirs("outputs", exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return path

    async def export_html(self, markdown_content: str, filename: str) -> str:
        """Export report as HTML."""
        import markdown
        html = markdown.markdown(
            markdown_content,
            extensions=['fenced_code', 'tables', 'latex']
        )
        html_content = f"""<!DOCTYPE html>
<html><head><title>Engineering Report</title>
<style>
  body {{ font-family: system-ui; max-width: 800px; margin: auto; padding: 2em; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
  th {{ background: #f5f5f5; }}
</style></head><body>
{html}
</body></html>"""
        import os
        path = f"outputs/{filename}"
        os.makedirs("outputs", exist_ok=True)
        with open(path, "w") as f:
            f.write(html_content)
        return path