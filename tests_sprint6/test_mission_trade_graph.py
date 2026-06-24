"""
Tests for Mission, Trade Studies, Knowledge Graph, and Systems Core Modules.
"""
from mission.mission_planner import MissionPlanner, MissionType, MissionConstraint, PerformanceTarget
from mission.mission_analyzer import MissionAnalyzer
from mission.mission_validator import MissionValidator
from trade_studies.tradeoff_engine import TradeoffEngine
from trade_studies.decision_matrix import DecisionMatrixBuilder
from trade_studies.alternative_evaluator import AlternativeEvaluator
from knowledge_graph.graph_builder import GraphBuilder, KnowledgeGraph
from knowledge_graph.dependency_graph import DependencyGraph
from knowledge_graph.traceability_graph import TraceabilityGraph
from systems_core.systems_orchestrator import SystemsOrchestrator
from systems_core.lifecycle_manager import LifecycleManager


class TestMissionPlanner:
    def setup_method(self):
        self.planner = MissionPlanner()

    def test_create_mission(self):
        mission = self.planner.create_mission("UAV Survey", MissionType.UAV)
        assert mission.id is not None
        assert mission.mission_type == MissionType.UAV

    def test_add_constraints(self):
        mission = self.planner.create_mission("Test")
        mission.add_constraint(MissionConstraint("Max Altitude", "altitude", 100, "m"))
        assert len(mission.constraints) == 1

    def test_add_performance_target(self):
        mission = self.planner.create_mission("Test")
        mission.add_performance_target(PerformanceTarget("Payload", "mass", 5.0, "kg"))
        assert len(mission.performance_targets) == 1

    def test_uav_mission_params(self):
        mission = self.planner.create_mission("UAV", MissionType.UAV)
        self.planner.add_uav_mission_params(mission, {"max_altitude": 400, "endurance": 30})
        assert len(mission.constraints) >= 2

    def test_generate_mission_profile(self):
        mission = self.planner.create_mission("Test")
        mission.add_objective("Survey area")
        profile = self.planner.generate_mission_profile(mission.id)
        assert profile["profile"]["objective_count"] >= 1


class TestMissionAnalyzer:
    def setup_method(self):
        self.planner = MissionPlanner()
        self.analyzer = MissionAnalyzer()

    def test_analyze_feasibility(self):
        mission = self.planner.create_mission("Test")
        result = self.analyzer.analyze_feasibility(mission)
        assert "feasible" in result

    def test_verify_performance(self):
        mission = self.planner.create_mission("Test")
        mission.add_performance_target(PerformanceTarget("Speed", "velocity", 100, "m/s"))
        result = self.analyzer.verify_performance(mission, {"Speed": 95})
        assert result["all_targets_met"] is False


class TestMissionValidator:
    def setup_method(self):
        self.planner = MissionPlanner()
        self.validator = MissionValidator()

    def test_validate(self):
        mission = self.planner.create_mission("Test")
        mission.add_objective("Objective")
        result = self.validator.validate(mission)
        assert "valid" in result


class TestTradeoffEngine:
    def setup_method(self):
        self.engine = TradeoffEngine()

    def test_add_criterion(self):
        c = self.engine.add_criterion("Performance", 0.5)
        assert c.name == "Performance"

    def test_evaluate(self):
        self.engine.add_criterion("Cost", 0.4, is_benefit=False)
        self.engine.add_criterion("Performance", 0.6)
        a1 = self.engine.add_alternative("Design A")
        a1.set_score("Cost", 8)
        a1.set_score("Performance", 7)
        a2 = self.engine.add_alternative("Design B")
        a2.set_score("Cost", 5)
        a2.set_score("Performance", 9)
        self.engine.normalize_scores()
        result = self.engine.evaluate()
        assert result["recommendation"] is not None

    def test_normalize(self):
        self.engine.add_criterion("Weight", 1.0, is_benefit=False)
        a1 = self.engine.add_alternative("A")
        a1.set_score("Weight", 100)
        a2 = self.engine.add_alternative("B")
        a2.set_score("Weight", 200)
        self.engine.normalize_scores()
        assert a1.scores["Weight"] > a2.scores["Weight"]


class TestDecisionMatrix:
    def setup_method(self):
        self.builder = DecisionMatrixBuilder()

    def test_create_matrix(self):
        dm = self.builder.create_matrix("Material Selection")
        dm.add_alternative("Aluminum")
        dm.add_alternative("Carbon Fiber")
        dm.add_criterion("Weight", 0.5)
        dm.add_criterion("Cost", 0.5)
        dm.set_score("Aluminum", "Weight", 6)
        dm.set_score("Aluminum", "Cost", 8)
        dm.set_score("Carbon Fiber", "Weight", 9)
        dm.set_score("Carbon Fiber", "Cost", 4)
        d = dm.to_dict()
        assert d["recommended"] is not None
        assert "weighted_scores" in d


class TestKnowledgeGraph:
    def setup_method(self):
        self.builder = GraphBuilder()

    def test_add_nodes(self):
        kg = self.builder.graph
        n1 = kg.add_node("Requirement-1", "requirement", "requirements")
        n2 = kg.add_node("Architecture-1", "architecture", "architecture")
        edge = kg.add_edge(n1.id, n2.id, "traces_to")
        assert edge is not None

    def test_connect_domains(self):
        domains = {
            "requirements": [{"name": "High speed", "type": "requirement"}],
            "architecture": [{"name": "High Speed Motor", "type": "component"}],
        }
        self.builder.connect_domains(domains)
        graph = self.builder.get_graph()
        exported = graph.export_graph()
        assert exported["stats"]["nodes"] >= 2

    def test_find_path(self):
        kg = KnowledgeGraph()
        a = kg.add_node("A", "test")
        b = kg.add_node("B", "test")
        c = kg.add_node("C", "test")
        kg.add_edge(a.id, b.id, "rel")
        kg.add_edge(b.id, c.id, "rel")
        path = kg.find_path(a.id, c.id)
        assert len(path) == 3

    def test_traceability_coverage(self):
        kg = KnowledgeGraph()
        a = kg.add_node("R1", "requirement", "requirements")
        b = kg.add_node("D1", "design", "design")
        kg.add_edge(a.id, b.id, "traces")
        tg = TraceabilityGraph(kg)
        report = tg.coverage_report()
        assert "report" in report


class TestSystemsOrchestrator:
    def setup_method(self):
        self.orch = SystemsOrchestrator()

    def test_execute_lifecycle(self):
        result = self.orch.execute_full_lifecycle("UAV Mission", "Survey Drone")
        assert result["success"] is True

    def test_get_lifecycle_status(self):
        status = self.orch.get_lifecycle_status()
        assert "lifecycle_state" in status

    def test_get_system_overview(self):
        overview = self.orch.get_system_overview()
        assert "requirements" in overview
        assert "architecture" in overview


class TestLifecycleManager:
    def setup_method(self):
        self.mgr = LifecycleManager()

    def test_initialize(self):
        report = self.mgr.get_lifecycle_report()
        assert len(report["phases"]) == 7

    def test_gate_control(self):
        assert self.mgr.open_gate("Mission Definition") is True
        assert self.mgr.close_gate("Mission Definition") is True