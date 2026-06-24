"""
Tests for Risk, Workflows, and Reviews Modules.
"""
from risk.risk_engine import RiskEngine, RiskCategory, RiskLevel
from risk.failure_analysis import FailureAnalysis
from risk.mitigation_engine import MitigationEngine
from workflows.workflow_orchestrator import WorkflowOrchestrator
from workflows.engineering_pipeline import EngineeringPipeline
from workflows.task_decomposer import TaskDecomposer
from reviews.design_review import DesignReviewPlatform, ReviewType, FindingSeverity, Finding, ActionItem
from reviews.compliance_checker import ComplianceChecker


class TestRiskEngine:
    def setup_method(self):
        self.engine = RiskEngine()

    def test_create_risk(self):
        risk = self.engine.create_risk("Motor failure", "Risk of motor failure", RiskCategory.TECHNICAL, 0.6, 0.8)
        assert risk.id is not None
        assert risk.risk_score == 0.48
        assert risk.risk_level == RiskLevel.MEDIUM

    def test_get_risk_by_level(self):
        self.engine.create_risk("Critical risk", "Critical", probability=0.9, impact=0.9)
        self.engine.create_risk("Low risk", "Low", probability=0.1, impact=0.1)
        critical = self.engine.get_risks_by_level(RiskLevel.CRITICAL)
        assert len(critical) >= 1

    def test_generate_risk_register(self):
        self.engine.create_risk("R1", "Desc", RiskCategory.SAFETY)
        register = self.engine.generate_risk_register()
        assert register["total_risks"] >= 1
        assert "critical_risks" in register

    def test_get_top_risks(self):
        self.engine.create_risk("R1", "Desc", probability=0.9, impact=0.9)
        top = self.engine.get_top_risks(5)
        assert len(top) >= 1


class TestFailureAnalysis:
    def setup_method(self):
        self.fa = FailureAnalysis()

    def test_add_failure_mode(self):
        mode = self.fa.add_failure_mode("Motor", "Overheat", "Loss of thrust", "Overcurrent", 8, 4, 6)
        assert mode.rpn == 192

    def test_generate_fmea_report(self):
        self.fa.add_failure_mode("Battery", "Short circuit", "Fire", "Manufacturing defect")
        report = self.fa.generate_fmea_report()
        assert report["total_modes"] >= 1


class TestMitigationEngine:
    def setup_method(self):
        self.engine = MitigationEngine()
        self.risk_engine = RiskEngine()

    def test_create_plan(self):
        risk = self.risk_engine.create_risk("Test Risk", "Desc")
        plan = self.engine.create_mitigation_plan(risk, "Add redundancy")
        assert plan.id is not None
        assert risk.status.value == "mitigating"


class TestWorkflowOrchestrator:
    def setup_method(self):
        self.orch = WorkflowOrchestrator()

    def test_create_workflow(self):
        wf = self.orch.create_workflow("Test Workflow")
        assert wf.id is not None
        assert wf.status.value == "pending"

    def test_generate_engineering_workflow(self):
        wf = self.orch.generate_engineering_workflow("Drone")
        assert len(wf.tasks) >= 6

    def test_execute_workflow(self):
        wf = self.orch.create_workflow("Test")
        result = self.orch.execute_workflow(wf.id)
        assert result["status"] == "completed"

    def test_topological_sort(self):
        wf = self.orch.create_workflow("Test")
        t1 = wf.add_task("Task1", "type1")
        t2 = wf.add_task("Task2", "type2", dependencies=[t1.id])
        result = self.orch.execute_workflow(wf.id)
        assert "Task1" in result["tasks_executed"]


class TestTaskDecomposer:
    def setup_method(self):
        self.decomposer = TaskDecomposer()

    def test_decompose_drone(self):
        result = self.decomposer.decompose("drone_development")
        assert len(result["subtasks"]) >= 3

    def test_decompose_generic(self):
        result = self.decomposer.decompose("custom_system")
        assert len(result["subtasks"]) == 4

    def test_generate_task_graph(self):
        subtasks = [{"name": "A", "type": "analysis", "depends_on": []},
                    {"name": "B", "type": "design", "depends_on": ["A"]}]
        graph = self.decomposer.generate_task_graph(subtasks)
        assert graph["total_tasks"] == 2


class TestDesignReviewPlatform:
    def setup_method(self):
        self.platform = DesignReviewPlatform()

    def test_create_review(self):
        review = self.platform.create_review("PDR Review", ReviewType.PRELIMINARY)
        assert review.id is not None
        assert review.status.value == "planned"

    def test_add_finding(self):
        review = self.platform.create_review("CDR", ReviewType.CRITICAL)
        finding = Finding("f1", "Design issue found", FindingSeverity.MAJOR, "design")
        review.add_finding(finding)
        assert len(review.findings) == 1

    def test_add_action_item(self):
        review = self.platform.create_review("Review", ReviewType.SYSTEM)
        item = ActionItem("a1", "Fix issue", "engineer")
        review.add_action_item(item)
        assert len(review.action_items) == 1

    def test_generate_review_report(self):
        review = self.platform.create_review("Test", ReviewType.ARCHITECTURE)
        report = self.platform.generate_review_report(review.id)
        assert report["total_findings"] >= 0


class TestComplianceChecker:
    def setup_method(self):
        self.checker = ComplianceChecker()

    def test_check_standards(self):
        result = self.checker.check_standards_compliance(
            {"quality": "implemented", "documentation": "done"},
            ["ISO-9001"],
        )
        assert "compliant" in result

    def test_check_traceability(self):
        result = self.checker.check_requirements_traceability(
            ["req1", "req2"], ["design includes req1"]
        )
        assert result["total_requirements"] == 2