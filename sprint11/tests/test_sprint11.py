import pytest
from datetime import datetime
from sprint11.schemas.enums import ExperimentState, HypothesisStatus, AgentCapabilityLevel
from sprint11.schemas.models import Experiment, ResearchProject, Hypothesis, AgentCapability
from sprint11.research_core.experiment_manager import ExperimentManager
from sprint11.research_core.evaluation_engine import EvaluationEngine
from sprint11.research_core.research_orchestrator import ResearchOrchestrator
from sprint11.self_improvement.capability_analyzer import CapabilityAnalyzer
from sprint11.self_improvement.self_evaluator import SelfEvaluator
from sprint11.self_improvement.improvement_planner import ImprovementPlanner
from sprint11.scientist.hypothesis_generator import HypothesisGenerator

def test_experiment_manager():
    mgr = ExperimentManager()
    exp = mgr.create_experiment(project_id="p1", name="TestExp", config={"lr": 0.01})
    assert exp.name == "TestExp"
    assert exp.state == ExperimentState.CREATED.value
    
    mgr.start_experiment(exp.id)
    assert exp.state == ExperimentState.RUNNING.value
    assert exp.started_at is not None
    
    mgr.log_metric(exp.id, "loss", 0.5)
    mgr.log_parameter(exp.id, "epochs", 10)
    assert exp.metrics["loss"] == 0.5
    assert exp.parameters["epochs"] == 10
    
    mgr.complete_experiment(exp.id, {"loss": 0.1})
    assert exp.state == ExperimentState.COMPLETED.value
    assert exp.metrics["loss"] == 0.1

def test_evaluation_engine():
    engine = EvaluationEngine()
    engine.register_rubric("test_rubric", {
        "criteria": [
            {"name": "accuracy", "weight": 0.5, "target": 1.0},
            {"name": "latency", "weight": 0.5, "target": 10.0}
        ],
        "pass_threshold": 0.8
    })
    
    eval_res = engine.evaluate("test_rubric", {"accuracy": 0.9, "latency": 10.0})
    assert eval_res["passed"] is True
    assert eval_res["overall_score"] == 0.95
    
    eval_res_fail = engine.evaluate("test_rubric", {"accuracy": 0.5, "latency": 20.0})
    assert eval_res_fail["passed"] is False

def test_research_orchestrator():
    orch = ResearchOrchestrator()
    project = orch.create_project(name="ProjectX", domain="ROBOTICS", objective="Optimize kinematics")
    assert project.name == "ProjectX"
    
    def dummy_runner(params):
        return {"metrics": {"feasibility": 0.95, "performance": 0.98, "cost_efficiency": 0.8, "safety_margin": 1.6, "manufacturability": 0.85}}
        
    res = orch.run_experiment(project.id, "KinematicsExp", dummy_runner, rubric="engineering_design")
    assert res["status"] == "COMPLETED"
    assert res["evaluation"]["passed"] is True

def test_capability_analyzer():
    analyzer = CapabilityAnalyzer()
    cap = analyzer.record_capability(agent_id="a1", capability_name="coding", score=0.85)
    assert cap.level == AgentCapabilityLevel.EXPERT.value
    assert cap.score == 0.85
    
    profile = analyzer.get_agent_profile("a1")
    assert profile["strongest"] == "coding"

def test_self_evaluator_and_improvement_planner():
    analyzer = CapabilityAnalyzer()
    evaluator = SelfEvaluator(analyzer)
    planner = ImprovementPlanner(analyzer)
    
    evaluator.evaluate_output(agent_id="a1", task_type="coding", output="def test(): pass")
    
    plan = planner.create_improvement_plan(agent_id="a1", target_overall=0.9)
    assert plan.agent_id == "a1"
    assert len(plan.actions) > 0
    
    timeline = planner.estimate_improvement_timeline(plan)
    assert timeline["total_days"] > 0

def test_hypothesis_generator():
    gen = HypothesisGenerator()
    hypotheses = gen.generate(project_id="p1", domain="electronics", count=2)
    assert len(hypotheses) == 2
    assert hypotheses[0].project_id == "p1"
    assert any(term in hypotheses[0].statement for term in ["efficiency", "noise", "EMI", "hotspot"])
