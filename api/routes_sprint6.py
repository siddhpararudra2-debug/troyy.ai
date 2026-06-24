"""
Sprint 6 FastAPI Routes - Systems Engineering, MBSE, Mission, Risk, Workflows, Reviews Platform.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/sprint6", tags=["Systems Engineering (Sprint 6)"])

# Initialize engines
from requirements.requirement_manager import RequirementManager, RequirementType, RequirementPriority
from requirements.requirement_parser import RequirementParser
from requirements.traceability_engine import TraceabilityEngine, TraceLinkType
from requirements.requirement_validator import RequirementValidator
from mbse.system_model import SystemModel, ModelElementType, ModelRelationType
from mbse.architecture_builder import ArchitectureBuilder
from mbse.behavior_model import BehaviorModel, BehaviorType, ActivityModel
from mbse.interface_model import InterfaceModel, InterfaceType
from architecture.architecture_generator import ArchitectureGenerator
from architecture.dependency_mapper import DependencyMapper
from mission.mission_planner import MissionPlanner, MissionType
from mission.mission_analyzer import MissionAnalyzer
from mission.mission_validator import MissionValidator
from trade_studies.tradeoff_engine import TradeoffEngine
from trade_studies.decision_matrix import DecisionMatrixBuilder
from trade_studies.alternative_evaluator import AlternativeEvaluator
from risk.risk_engine import RiskEngine, RiskCategory
from risk.failure_analysis import FailureAnalysis
from risk.mitigation_engine import MitigationEngine
from workflows.workflow_orchestrator import WorkflowOrchestrator
from workflows.engineering_pipeline import EngineeringPipeline
from workflows.task_decomposer import TaskDecomposer
from reviews.design_review import DesignReviewPlatform, ReviewType, FindingSeverity, Finding, ActionItem
from reviews.compliance_checker import ComplianceChecker
from knowledge_graph.graph_builder import GraphBuilder
from knowledge_graph.dependency_graph import DependencyGraph
from knowledge_graph.traceability_graph import TraceabilityGraph
from systems_core.systems_orchestrator import SystemsOrchestrator
from systems_core.lifecycle_manager import LifecycleManager

req_manager = RequirementManager()
req_parser = RequirementParser()
trace_engine = TraceabilityEngine(req_manager)
req_validator = RequirementValidator(req_manager)
system_model = SystemModel()
arch_builder = ArchitectureBuilder(system_model)
behavior_model = BehaviorModel()
interface_model = InterfaceModel()
arch_generator = ArchitectureGenerator()
dep_mapper = DependencyMapper()
mission_planner = MissionPlanner()
mission_analyzer = MissionAnalyzer()
mission_validator = MissionValidator()
tradeoff_engine = TradeoffEngine()
decision_matrix_builder = DecisionMatrixBuilder()
alt_evaluator = AlternativeEvaluator()
risk_engine = RiskEngine()
failure_analysis = FailureAnalysis()
mitigation_engine = MitigationEngine()
workflow_orch = WorkflowOrchestrator()
eng_pipeline = EngineeringPipeline()
task_decomposer = TaskDecomposer()
review_platform = DesignReviewPlatform()
compliance_checker = ComplianceChecker()
graph_builder = GraphBuilder()
systems_orch = SystemsOrchestrator()
lifecycle_mgr = LifecycleManager()


# ============= Pydantic Models =============

class CreateRequirementRequest(BaseModel):
    title: str
    description: str
    req_type: str = "functional"
    priority: str = "medium"
    parent_id: Optional[str] = None

class ParseRequirementRequest(BaseModel):
    text: str

class CreateMissionRequest(BaseModel):
    name: str
    mission_type: str = "general"
    description: Optional[str] = None

class CreateRiskRequest(BaseModel):
    title: str
    description: str
    category: str = "technical"
    probability: float = 0.5
    impact: float = 0.5

class CreateReviewRequest(BaseModel):
    title: str
    review_type: str = "preliminary_design_review"
    description: Optional[str] = None

class CreateWorkflowRequest(BaseModel):
    name: str
    description: Optional[str] = None

class GenerateArchitectureRequest(BaseModel):
    system_name: str
    requirements: List[Dict[str, Any]] = []

class RunTradeStudyRequest(BaseModel):
    title: str
    criteria: List[Dict[str, Any]]
    alternatives: List[Dict[str, Any]]


# ============= REQUIREMENTS ENDPOINTS =============

@router.post("/requirements/create")
async def create_requirement(req: CreateRequirementRequest):
    try:
        r = req_manager.create_requirement(
            title=req.title,
            description=req.description,
            req_type=RequirementType(req.req_type),
            priority=RequirementPriority(req.priority),
            parent_id=req.parent_id,
        )
        return {"id": r.id, "title": r.title, "req_type": r.req_type.value, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/requirements/parse")
async def parse_requirement(req: ParseRequirementRequest):
    try:
        parsed = req_parser.parse(req.text)
        return {
            "title": parsed.title,
            "req_type": parsed.req_type.value if parsed.req_type else None,
            "priority": parsed.priority.value if parsed.priority else None,
            "confidence": parsed.confidence,
            "is_valid": parsed.is_valid,
            "validation_errors": parsed.validation_errors,
            "keywords": parsed.keywords,
            "entities": parsed.extracted_entities,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/requirements/validate")
async def validate_requirements():
    try:
        report = req_validator.generate_validation_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/requirements/{req_id}")
async def get_requirement(req_id: str):
    req = req_manager.get_requirement(req_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req.to_dict()

@router.get("/requirements")
async def list_requirements(req_type: Optional[str] = None):
    reqs = req_manager.get_requirements_by_type(RequirementType(req_type)) if req_type else req_manager.get_all_requirements()
    return {"requirements": [r.to_dict() for r in reqs], "total": len(reqs)}

@router.post("/requirements/trace")
async def trace_requirement(source_id: str = Body(...), target_id: str = Body(...)):
    result = trace_engine.impact_analysis(source_id)
    return result

@router.get("/requirements/traceability/matrix")
async def traceability_matrix():
    return trace_engine.generate_traceability_matrix()

@router.get("/requirements/tree")
async def requirement_tree():
    return req_manager.generate_tree_report()


# ============= MBSE ENDPOINTS =============

@router.post("/mbse/system-model")
async def create_system_model(name: str = Body(...), description: Optional[str] = Body(None)):
    model = system_model
    model.name = name
    model.description = description
    return {"id": model.id, "name": model.name}

@router.post("/mbse/element")
async def create_element(name: str = Body(...), element_type: str = Body("component"),
                         parent_id: Optional[str] = Body(None)):
    el = system_model.create_element(
        name=name,
        element_type=ModelElementType(element_type),
        parent_id=parent_id,
    )
    return {"id": el.id, "name": el.name, "type": el.element_type.value}

@router.post("/mbse/relation")
async def create_relation(source_id: str = Body(...), target_id: str = Body(...),
                          relation_type: str = Body("association")):
    rel = system_model.create_relation(source_id, target_id, ModelRelationType(relation_type))
    if not rel:
        raise HTTPException(status_code=400, detail="Could not create relation")
    return {"id": rel.id, "source": rel.source_id, "target": rel.target_id}

@router.get("/mbse/model")
async def get_system_model():
    return system_model.export_model()

@router.get("/mbse/architecture/diagram")
async def get_architecture_diagram():
    bdd = arch_builder.generate_block_definition_diagram()
    ibd = arch_builder.generate_internal_block_diagram()
    return {"block_definition": bdd, "internal_block": ibd}

@router.post("/mbse/behavior")
async def create_behavior(name: str = Body(...), behavior_type: str = Body("function")):
    b = behavior_model.create_behavior(name, BehaviorType(behavior_type))
    return {"id": b.id, "name": b.name, "type": b.behavior_type.value}


# ============= ARCHITECTURE ENDPOINTS =============

@router.post("/architecture/generate")
async def generate_architecture(req: GenerateArchitectureRequest):
    try:
        tree = arch_generator.generate_from_requirements(req.system_name, req.requirements)
        interfaces = arch_generator.generate_interface_map(tree.id)
        return {
            "tree_id": tree.id,
            "architecture": tree.to_dict(),
            "interfaces": interfaces,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/architecture/{tree_id}")
async def get_architecture(tree_id: str):
    tree = arch_generator.get_architecture(tree_id)
    if not tree:
        raise HTTPException(status_code=404, detail="Architecture not found")
    return tree.to_dict()


# ============= MISSION ENDPOINTS =============

@router.post("/mission/create")
async def create_mission(req: CreateMissionRequest):
    mission = mission_planner.create_mission(
        name=req.name,
        mission_type=MissionType(req.mission_type),
        description=req.description,
    )
    return {"id": mission.id, "name": mission.name, "phase": mission.phase.value}

@router.get("/mission/{mission_id}")
async def get_mission(mission_id: str):
    mission = mission_planner.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission.to_dict()

@router.post("/mission/{mission_id}/analyze")
async def analyze_mission(mission_id: str):
    mission = mission_planner.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission_analyzer.analyze_feasibility(mission)

@router.post("/mission/{mission_id}/validate")
async def validate_mission(mission_id: str):
    mission = mission_planner.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission_validator.validate(mission)

@router.get("/missions")
async def list_missions():
    missions = mission_planner.get_all_missions()
    return {"missions": [m.to_dict() for m in missions], "total": len(missions)}


# ============= TRADE STUDY ENDPOINTS =============

@router.post("/trade-study/run")
async def run_trade_study(req: RunTradeStudyRequest):
    try:
        engine = TradeoffEngine()
        for c in req.criteria:
            engine.add_criterion(c["name"], c.get("weight", 1.0), c.get("is_benefit", True))
        for alt_data in req.alternatives:
            alt = engine.add_alternative(alt_data["name"], alt_data.get("description"))
            for cname, score in alt_data.get("scores", {}).items():
                alt.set_score(cname, score)
            alt.risks = alt_data.get("risks", [])
            alt.costs = alt_data.get("costs", {})
        engine.normalize_scores()
        result = engine.evaluate()

        dm = decision_matrix_builder.create_matrix(req.title)
        for c in req.criteria:
            dm.add_criterion(c["name"], c.get("weight", 1.0))
        for alt_data in req.alternatives:
            dm.add_alternative(alt_data["name"])
            for cname, score in alt_data.get("scores", {}).items():
                dm.set_score(alt_data["name"], cname, score)

        return {"trade_study": result, "decision_matrix": dm.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============= RISK ENDPOINTS =============

@router.post("/risk/analyze")
async def create_risk(req: CreateRiskRequest):
    risk = risk_engine.create_risk(
        title=req.title,
        description=req.description,
        category=RiskCategory(req.category),
        probability=req.probability,
        impact=req.impact,
    )
    return {"id": risk.id, "score": risk.risk_score, "level": risk.risk_level.value}

@router.get("/risk/register")
async def risk_register():
    return risk_engine.generate_risk_register()

@router.post("/risk/fmea")
async def add_fmea_mode(component: str = Body(...), failure_mode: str = Body(...),
                         effects: str = Body(...), cause: str = Body(...)):
    mode = failure_analysis.add_failure_mode(component, failure_mode, effects, cause)
    return {"id": mode.id, "rpn": mode.rpn}

@router.get("/risk/fmea/report")
async def fmea_report():
    return failure_analysis.generate_fmea_report()


# ============= WORKFLOW ENDPOINTS =============

@router.post("/workflow/generate")
async def generate_workflow(req: CreateWorkflowRequest):
    wf = workflow_orch.create_workflow(req.name, req.description)
    eng_wf = workflow_orch.generate_engineering_workflow(req.name)
    return {"id": eng_wf.id, "tasks": len(eng_wf.tasks), "status": eng_wf.status.value}

@router.post("/workflow/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    result = workflow_orch.execute_workflow(workflow_id)
    return result

@router.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    wf = workflow_orch.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf.to_dict()

@router.post("/workflow/decompose")
async def decompose_task(task_name: str = Body(...)):
    result = task_decomposer.decompose(task_name)
    return result


# ============= REVIEW ENDPOINTS =============

@router.post("/review/run")
async def run_review(req: CreateReviewRequest):
    review = review_platform.create_review(req.title, ReviewType(req.review_type), req.description)
    return {"id": review.id, "title": review.title, "status": review.status.value}

@router.post("/review/{review_id}/finding")
async def add_finding(review_id: str, description: str = Body(...),
                      severity: str = Body("minor"), category: str = Body("general")):
    review = review_platform.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    finding = Finding(str(uuid.uuid4()), description, FindingSeverity(severity), category)
    review.add_finding(finding)
    return {"id": finding.id, "severity": severity}

@router.get("/review/{review_id}/report")
async def review_report(review_id: str):
    return review_platform.generate_review_report(review_id)


# ============= KNOWLEDGE GRAPH ENDPOINTS =============

@router.post("/knowledge-graph/connect")
async def connect_domains(domains: Dict[str, List[Dict[str, Any]]] = Body(...)):
    graph_builder.connect_domains(domains)
    graph = graph_builder.get_graph()
    exported = graph.export_graph()
    return {"nodes": exported["stats"]["nodes"], "edges": exported["stats"]["edges"]}

@router.get("/knowledge-graph")
async def get_knowledge_graph():
    return graph_builder.get_graph().export_graph()

@router.get("/knowledge-graph/traceability")
async def knowledge_graph_traceability():
    tg = TraceabilityGraph(graph_builder.get_graph())
    return tg.coverage_report()


# ============= LIFECYCLE ENDPOINTS =============

@router.post("/lifecycle/execute")
async def execute_lifecycle(mission_name: str = Body(...), system_name: str = Body(...)):
    return systems_orch.execute_full_lifecycle(mission_name, system_name)

@router.get("/lifecycle/status")
async def lifecycle_status():
    return systems_orch.get_lifecycle_status()

@router.get("/system/overview")
async def system_overview():
    return systems_orch.get_system_overview()


# ============= HEALTH =============

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "6.0",
        "modules": {
            "requirements": "ready",
            "mbse": "ready",
            "architecture": "ready",
            "mission": "ready",
            "trade_studies": "ready",
            "risk": "ready",
            "workflows": "ready",
            "reviews": "ready",
            "knowledge_graph": "ready",
            "systems_core": "ready",
        },
        "timestamp": datetime.utcnow().isoformat(),
    }