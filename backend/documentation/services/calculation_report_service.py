from typing import Dict, Any
from documentation.models.database import CalculationReport, ProjectReport, ReportType
from documentation.schemas.documentation import CalculationReportCreate
from sqlalchemy.orm import Session

class CalculationReportService:
    def __init__(self, db: Session):
        self.db = db

    def create_report(self, project_id: str, data: CalculationReportCreate) -> int:
        # Create or get parent ProjectReport
        report = ProjectReport(
            project_id=project_id,
            report_type=ReportType.CALCULATION,
            title="Calculation Report",
            content={"summary": data.problem_statement[:100]}
        )
        self.db.add(report)
        self.db.flush() # Get report.id

        calc_report = CalculationReport(
            project_report_id=report.id,
            **data.model_dump()
        )
        self.db.add(calc_report)
        self.db.commit()
        return report.id
