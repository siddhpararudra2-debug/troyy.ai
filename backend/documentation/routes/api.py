from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from documentation.schemas.documentation import (
    CalculationReportCreate, DecisionLogCreate, ExportRequest, ExportResponse,
    ProjectHistoryResponse, KnowledgeEntryResponse
)
from documentation.services.calculation_report_service import CalculationReportService
from documentation.services.decision_log_service import DecisionLogService
from documentation.services.project_history_service import ProjectHistoryService
from documentation.services.knowledge_capture_service import KnowledgeCaptureService
from documentation.services.export_service import ExportService

# Mock DB dependency
def get_db():
    class MockSession:
        def add(self, obj): obj.id = 1
        def commit(self): pass
        def flush(self): pass
        def query(self, model): 
            class MockQuery:
                def filter(self, *args): return self
                def order_by(self, *args): return self
                def limit(self, *args): return self
                def all(self): 
                    return [type('obj', (object,), {
                        'id': 1, 'project_id': 'P-001', 'timestamp': '2026-06-16T10:00:00',
                        'event_type': 'INIT', 'details': {}, 'actor': 'SYSTEM',
                        'category': 'LESSON_LEARNED', 'title': 'Test', 'content': 'Test', 'tags': [], 'source_project_id': None
                    })()]
                def first(self): 
                    return type('obj', (object,), {
                        'id': 1, 'title': 'Test Report', 'generated_at': '2026-06-16T10:00:00'
                    })()
            return MockQuery()
    return MockSession()

router = APIRouter(prefix="/documentation", tags=["Documentation Engine"])

@router.post("/generate-calculation-report")
async def generate_calculation_report(project_id: str, data: CalculationReportCreate, db: Session = Depends(get_db)):
    service = CalculationReportService(db)
    report_id = service.create_report(project_id, data)
    
    # Log to history
    history_service = ProjectHistoryService(db)
    history_service.log_event(project_id, "CALCULATION_REPORT_GENERATED", {"report_id": report_id})
    
    return {"report_id": report_id, "status": "GENERATED"}

@router.post("/log-decision")
async def log_decision(data: DecisionLogCreate, db: Session = Depends(get_db)):
    service = DecisionLogService(db)
    decision_id = service.log_decision(data)
    return {"decision_id": decision_id, "status": "LOGGED"}

@router.get("/project-history/{project_id}", response_model=list[ProjectHistoryResponse])
async def get_project_history(project_id: str, db: Session = Depends(get_db)):
    service = ProjectHistoryService(db)
    return service.get_timeline(project_id)

@router.get("/knowledge-base", response_model=list[KnowledgeEntryResponse])
async def search_knowledge(query: str = "", category: str = None, db: Session = Depends(get_db)):
    service = KnowledgeCaptureService(db)
    return service.search_knowledge(query, category)

@router.post("/export", response_model=ExportResponse)
async def export_document(request: ExportRequest, db: Session = Depends(get_db)):
    service = ExportService(db)
    try:
        result = service.export_report(request.report_id, request.format)
        return ExportResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
