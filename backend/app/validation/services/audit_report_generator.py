"""
Troy — Audit Report Generator
Compiles validation reports, engineering reviews, risk assessments, and approvals into multiple formats.
"""

from __future__ import annotations

import json
from typing import Dict, Any, List
from app.validation.services.pdf_generator import generate_pdf


class AuditReportGenerator:
    """Formats engineering audits into Markdown, HTML, JSON, and PDF compliant formats."""

    @staticmethod
    def generate_report(
        report: Dict[str, Any],
        review: Dict[str, Any],
        risks: Dict[str, Any],
        approval: Dict[str, Any],
        fmt: str,
    ) -> str | bytes:
        fmt = fmt.lower()
        
        if fmt == "json":
            return json.dumps(
                {
                    "validation_report": report,
                    "engineering_review": review,
                    "risk_assessment": risks,
                    "approval_decision": approval,
                },
                indent=2,
            )

        if fmt == "markdown":
            return AuditReportGenerator._to_markdown(report, review, risks, approval)

        if fmt == "html":
            return AuditReportGenerator._to_html(report, review, risks, approval)

        if fmt == "pdf":
            return AuditReportGenerator._to_pdf(report, review, risks, approval)

        raise ValueError(f"Unsupported report format: {fmt}")

    @staticmethod
    def _to_markdown(
        report: Dict[str, Any],
        review: Dict[str, Any],
        risks: Dict[str, Any],
        approval: Dict[str, Any],
    ) -> str:
        md = []
        md.append(f"# ENGINEERING COMPLIANCE & GATEKEEPER AUDIT REPORT")
        md.append(f"**Domain:** {report.get('domain', 'multi').upper()}")
        md.append(f"**Status:** {approval.get('status', 'PENDING')}")
        md.append(f"**Date:** {report.get('created_at', '')}")
        md.append("\n" + "─" * 40 + "\n")

        # ── GATEKEEPER APPROVAL ──
        md.append(f"## 1. GATEKEEPER DECISION: {approval.get('status')}")
        md.append(f"**Engineering Reasoning:** {approval.get('engineering_reasoning')}")
        md.append(f"**Validation Summary:** {approval.get('validation_summary')}")
        md.append(f"**Risk Summary:** {approval.get('risk_summary')}")
        md.append("\n" + "─" * 40 + "\n")

        # ── VALIDATION REPORT ──
        md.append("## 2. MODULAR VALIDATION REPORT")
        md.append(f"- **Total Errors:** {report.get('total_errors')}")
        md.append(f"- **Total Warnings:** {report.get('total_warnings')}")
        md.append(f"- **Execution Time:** {report.get('execution_time_ms', 0):.1f} ms")
        md.append("\n### ISSUES LIST:")
        
        issues: List[Dict[str, Any]] = report.get("issues", [])
        if not issues:
            md.append("✓ No validation issues found.")
        else:
            for idx, issue in enumerate(issues):
                md.append(f"#### [{issue.get('severity').upper()}] {issue.get('message')} (Validator: {issue.get('validator_name')})")
                if issue.get("engineering_reasoning"):
                    md.append(f"  - *Engineering Reasoning:* {issue.get('engineering_reasoning')}")
                if issue.get("recommendation"):
                    md.append(f"  - *Recommendation:* {issue.get('recommendation')}")
        md.append("\n" + "─" * 40 + "\n")

        # ── ENGINEERING REVIEW ──
        md.append("## 3. SENIOR DESIGN REVIEW BOARD CRITIQUE")
        checks = review.get("checks", {})
        md.append(f"- **Design Decisions Check:** {checks.get('design_decisions_check')}")
        md.append(f"- **Component Choices Check:** {checks.get('component_choices_check')}")
        md.append(f"- **Structural Choices Check:** {checks.get('structural_choices_check')}")
        md.append(f"- **Electrical Choices Check:** {checks.get('electrical_choices_check')}")
        md.append(f"- **Weight Budgets Check:** {checks.get('weight_budgets_check')}")
        md.append(f"- **Power Budgets Check:** {checks.get('power_budgets_check')}")
        md.append(f"- **Thermal Assumptions Check:** {checks.get('thermal_assumptions_check')}")
        md.append(f"\n**Overall Assessment:** {review.get('overall_assessment')}")
        md.append("\n" + "─" * 40 + "\n")

        # ── RISK ASSESSMENT ──
        md.append("## 4. HAZARD RISK LOG")
        md.append(f"**Overall Risk Rating:** {risks.get('overall_risk_level')}")
        
        risk_items: List[Dict[str, Any]] = risks.get("risks", [])
        if not risk_items:
            md.append("✓ No significant hazard risk items identified.")
        else:
            for idx, r in enumerate(risk_items):
                md.append(f"### Hazard {idx+1}: {r.get('description')}")
                md.append(f"- **Cause:** {r.get('cause')}")
                md.append(f"- **Severity:** {r.get('severity')} | **Probability:** {r.get('probability')} | **Impact:** {r.get('impact')}")
                md.append(f"- **Recommended Fix:** {r.get('recommended_fix')}")

        return "\n".join(md)

    @staticmethod
    def _to_html(
        report: Dict[str, Any],
        review: Dict[str, Any],
        risks: Dict[str, Any],
        approval: Dict[str, Any],
    ) -> str:
        # Generate rich, modern glassmorphism/dark mode aesthetics HTML matching Guidelines
        status = approval.get("status", "PENDING")
        status_color = "#10b981" if status == "APPROVED" else "#f59e0b" if status == "APPROVED WITH CONCERNS" else "#ef4444"
        
        issues_html = []
        for issue in report.get("issues", []):
            sev = issue.get("severity", "info").upper()
            color = "#ef4444" if sev == "ERROR" else "#f59e0b" if sev == "WARNING" else "#3b82f6"
            issues_html.append(f"""
            <div class="issue-card" style="border-left: 4px solid {color}; margin-bottom: 12px; padding: 10px; background: rgba(255,255,255,0.05); border-radius: 4px;">
                <div style="font-weight: bold; color: {color};">{sev}: {issue.get('message')}</div>
                <div style="font-size: 0.9em; margin-top: 5px; color: #ccc;"><strong>Reasoning:</strong> {issue.get('engineering_reasoning')}</div>
                <div style="font-size: 0.9em; margin-top: 5px; color: #10b981;"><strong>Recommendation:</strong> {issue.get('recommendation')}</div>
            </div>
            """)

        checks_html = []
        for k, v in review.get("checks", {}).items():
            color = "#10b981" if "Passed" in v else "#ef4444" if "Failed" in v else "#f59e0b"
            checks_html.append(f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);">{k.replace('_', ' ').title()}</td>
                <td style="padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); font-weight: bold; color: {color};">{v}</td>
            </tr>
            """)

        risks_html = []
        for idx, r in enumerate(risks.get("risks", [])):
            sev = r.get("severity")
            color = "#ef4444" if sev in ["CRITICAL", "HIGH"] else "#f59e0b" if sev == "MEDIUM" else "#10b981"
            risks_html.append(f"""
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 10px;"><strong>Hazard {idx+1}:</strong> {r.get('description')}<br><span style="font-size: 0.85em; color: #aaa;">Cause: {r.get('cause')}</span></td>
                <td style="padding: 10px; color: {color}; font-weight: bold;">{sev}</td>
                <td style="padding: 10px;">{r.get('probability')}</td>
                <td style="padding: 10px;">{r.get('impact')}</td>
                <td style="padding: 10px; color: #10b981; font-size: 0.9em;">{r.get('recommended_fix')}</td>
            </tr>
            """)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Engineering Compliance Audit Report</title>
    <style>
        body {{
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: rgba(30, 41, 59, 0.7);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        h1, h2, h3 {{
            color: #f1f5f9;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid rgba(255,255,255,0.1);
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .badge {{
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .section {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: rgba(0,0,0,0.2);
            border-radius: 6px;
            overflow: hidden;
        }}
        th {{
            background: rgba(255,255,255,0.05);
            text-align: left;
            padding: 10px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 style="margin:0; font-size: 2em; letter-spacing: -0.5px;">ENGINEERING REVIEW BOARD AUDIT</h1>
                <span style="color: #94a3b8; font-size: 0.9em;">Domain: {report.get('domain', 'multi').upper()} | Date: {report.get('created_at', '')}</span>
            </div>
            <div class="badge" style="background-color: {status_color}; color: #fff;">
                {status}
            </div>
        </div>

        <div class="section">
            <h2>1. Gatekeeper Decision & Logic</h2>
            <p style="font-size: 1.1em; line-height: 1.5; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 6px; border-left: 4px solid {status_color};">
                <strong>Decision Reason:</strong> {approval.get('engineering_reasoning')}<br><br>
                <span style="font-size: 0.9em; color: #cbd5e1;"><strong>Validation:</strong> {approval.get('validation_summary')}</span><br>
                <span style="font-size: 0.9em; color: #cbd5e1;"><strong>Risk Summary:</strong> {approval.get('risk_summary')}</span>
            </p>
        </div>

        <div class="section">
            <h2>2. Validation Report ({report.get('total_errors')} Errors, {report.get('total_warnings')} Warnings)</h2>
            {"".join(issues_html) if issues_html else "<p style='color: #10b981;'>✓ All automated verification checks passed.</p>"}
        </div>

        <div class="section">
            <h2>3. Senior Design Review Ratings</h2>
            <table style="width: 100%;">
                <thead>
                    <tr>
                        <th style="padding: 10px;">Verification Check</th>
                        <th style="padding: 10px;">Board Rating</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(checks_html)}
                </tbody>
            </table>
            <p style="margin-top: 15px; font-style: italic; color: #cbd5e1;"><strong>Overall Critique:</strong> {review.get('overall_assessment')}</p>
        </div>

        <div class="section" style="border-bottom: none; margin-bottom: 0;">
            <h2>4. Hazard Risk Log (Overall Risk: {risks.get('overall_risk_level')})</h2>
            <table>
                <thead>
                    <tr style="background: rgba(255,255,255,0.05);">
                        <th style="padding: 10px;">Hazard Description</th>
                        <th style="padding: 10px;">Severity</th>
                        <th style="padding: 10px;">Probability</th>
                        <th style="padding: 10px;">Impact</th>
                        <th style="padding: 10px;">Actionable Fix</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(risks_html) if risks_html else "<tr><td colspan='5' style='padding: 15px; text-align: center; color: #10b981;'>✓ No risks identified. Design satisfies compliance.</td></tr>"}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
        return html

    @staticmethod
    def _to_pdf(
        report: Dict[str, Any],
        review: Dict[str, Any],
        risks: Dict[str, Any],
        approval: Dict[str, Any],
    ) -> bytes:
        title = "Engineering Compliance Audit Report"
        
        sections = []
        
        # 1. Gatekeeper Approval
        sections.append({
            "heading": "1. Gatekeeper Decision & Logic",
            "text": (
                f"Status: {approval.get('status', 'PENDING')}\n"
                f"Engineering Reasoning: {approval.get('engineering_reasoning')}\n"
                f"Validation Summary: {approval.get('validation_summary')}\n"
                f"Risk Summary: {approval.get('risk_summary')}"
            )
        })

        # 2. Validation Issues
        issues_text = []
        for idx, issue in enumerate(report.get("issues", [])):
            issues_text.append(
                f"- [{issue.get('severity').upper()}] {issue.get('message')}\n"
                f"  Reasoning: {issue.get('engineering_reasoning')}\n"
                f"  Recommendation: {issue.get('recommendation')}\n"
            )
        sections.append({
            "heading": f"2. Validation Report ({report.get('total_errors')} Errors, {report.get('total_warnings')} Warnings)",
            "text": "\n".join(issues_text) if issues_text else "All verification checks passed successfully."
        })

        # 3. Design Review
        review_text = []
        for k, v in review.get("checks", {}).items():
            review_text.append(f"- {k.replace('_', ' ').title()}: {v}")
        review_text.append(f"\nOverall Assessment: {review.get('overall_assessment')}")
        sections.append({
            "heading": "3. Senior Design Review Ratings",
            "text": "\n".join(review_text)
        })

        # 4. Risk Assessment
        risk_text = []
        for idx, r in enumerate(risks.get("risks", [])):
            risk_text.append(
                f"Hazard {idx+1}: {r.get('description')}\n"
                f"Severity: {r.get('severity')} | Probability: {r.get('probability')} | Impact: {r.get('impact')}\n"
                f"Fix: {r.get('recommended_fix')}\n"
            )
        sections.append({
            "heading": f"4. Hazard Risk Log (Overall Risk: {risks.get('overall_risk_level')})",
            "text": "\n".join(risk_text) if risk_text else "No hazards identified."
        })

        return generate_pdf(title, sections)
