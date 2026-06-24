"""Sprint 16 API Routes - FastAPI routes for Sprint 16 (Engineering Deep Research)."""

from fastapi import APIRouter
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/sprint16", tags=["Sprint 16 - Deep Research"])


@router.post("/research/start")
async def start_research(question: str, domain: str, name: Optional[str] = None):
    from research_core import ResearchOrchestrator
    orchestrator = ResearchOrchestrator()
    return orchestrator.start_research(question, domain, name)


@router.get("/research/{project_id}")
async def get_research_project(project_id: str):
    from research_core import ResearchOrchestrator
    orchestrator = ResearchOrchestrator()
    project = orchestrator.get_project(project_id)
    if not project:
        return {"error": "Project not found"}
    return project


@router.post("/research/mechanical")
async def mechanical_research(material: str, application: str):
    from mechanical_research import MaterialResearch
    researcher = MaterialResearch()
    return researcher.research(material, application)


@router.post("/research/electrical")
async def electrical_research(component_type: str):
    from electrical_research import ComponentResearch
    researcher = ComponentResearch()
    return researcher.research(component_type, {})


@router.post("/research/patent")
async def patent_search(keyword: Optional[str] = None):
    from patents import PatentSearch
    searcher = PatentSearch()
    return searcher.search(keyword)


@router.post("/research/standards")
async def standards_search(keyword: Optional[str] = None):
    from standards import StandardsEngine
    engine = StandardsEngine()
    return engine.search_standards(keyword)


@router.post("/research/literature")
async def literature_search(keyword: Optional[str] = None):
    from academic import LiteratureSearch
    searcher = LiteratureSearch()
    return searcher.search(keyword)


@router.post("/trade-study/run")
async def run_trade_study(name: str, alternatives: list, criteria: list):
    from trade_studies import DecisionMatrix, WeightingEngine
    matrix = DecisionMatrix()
    dm = matrix.create_matrix(name, alternatives, criteria)
    weights = WeightingEngine().equal_weights(len(criteria))
    results = matrix.calculate_scores(dm["id"], weights)
    return results


@router.post("/technology-scout/run")
async def run_technology_scout():
    from technology_scouting import EmergingTechDetector
    detector = EmergingTechDetector()
    return detector.detect()


@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "sprint16"}
