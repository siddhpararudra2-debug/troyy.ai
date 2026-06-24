"""
Tests for Requirements Management Module.
"""
import pytest
from requirements.requirement_manager import RequirementManager, RequirementType, RequirementPriority, RequirementStatus
from requirements.requirement_parser import RequirementParser
from requirements.traceability_engine import TraceabilityEngine, TraceLinkType
from requirements.requirement_validator import RequirementValidator


class TestRequirementManager:
    def setup_method(self):
        self.manager = RequirementManager()

    def test_create_requirement(self):
        req = self.manager.create_requirement(
            title="Test Requirement",
            description="The system shall perform test function within 100ms",
            req_type=RequirementType.PERFORMANCE,
            priority=RequirementPriority.HIGH,
        )
        assert req.id is not None
        assert req.title == "Test Requirement"
        assert req.req_type == RequirementType.PERFORMANCE
        assert req.priority == RequirementPriority.HIGH

    def test_get_requirement(self):
        req = self.manager.create_requirement("Test", "Description")
        found = self.manager.get_requirement(req.id)
        assert found is not None
        assert found.id == req.id

    def test_update_requirement(self):
        req = self.manager.create_requirement("Test", "Description")
        updated = self.manager.update_requirement(req.id, title="Updated Test")
        assert updated is not None
        assert updated.title == "Updated Test"
        assert updated.version == 2

    def test_build_tree(self):
        parent = self.manager.create_requirement("Parent", "Parent description")
        child = self.manager.create_requirement("Child", "Child description", parent_id=parent.id)
        trees = self.manager.build_tree([parent.id])
        assert len(trees) == 1
        assert trees[0].requirement.id == parent.id
        assert len(trees[0].children) == 1

    def test_traceability_links(self):
        r1 = self.manager.create_requirement("Req1", "Description 1")
        r2 = self.manager.create_requirement("Req2", "Description 2")
        result = self.manager.add_traceability_link(r1.id, r2.id)
        assert result is True
        chain = self.manager.get_traceability_chain(r1.id)
        assert len(chain) == 2

    def test_search(self):
        self.manager.create_requirement("Flight Controller", "Controls flight operation")
        self.manager.create_requirement("Power System", "Provides electrical power")
        results = self.manager.search_requirements("flight")
        assert len(results) == 1
        assert "Flight" in results[0].title

    def test_count_by_type(self):
        self.manager.create_requirement("F1", "Functional", req_type=RequirementType.FUNCTIONAL)
        self.manager.create_requirement("P1", "Safety", req_type=RequirementType.SAFETY)
        counts = self.manager.count_by_type()
        assert counts.get("functional", 0) == 1
        assert counts.get("safety", 0) == 1

    def test_generate_tree_report(self):
        self.manager.create_requirement("Root", "Root requirement")
        report = self.manager.generate_tree_report()
        assert report["total_requirements"] >= 1


class TestRequirementParser:
    def setup_method(self):
        self.parser = RequirementParser()

    def test_parse_functional(self):
        text = "The system shall provide autonomous navigation capability"
        parsed = self.parser.parse(text)
        assert parsed.req_type == RequirementType.FUNCTIONAL
        assert parsed.is_valid is True

    def test_parse_performance(self):
        text = "The system must achieve 95% accuracy within 100ms response time"
        parsed = self.parser.parse(text)
        assert parsed.req_type == RequirementType.PERFORMANCE

    def test_parse_safety(self):
        text = "The system shall implement fail-safe shutdown upon hazard detection"
        parsed = self.parser.parse(text)
        assert parsed.req_type == RequirementType.SAFETY

    def test_parse_empty(self):
        parsed = self.parser.parse("")
        assert parsed.is_valid is False

    def test_batch_parse(self):
        texts = ["Req one", "Req two"]
        results = self.parser.parse_batch(texts)
        assert len(results) == 2


class TestTraceabilityEngine:
    def setup_method(self):
        self.req_manager = RequirementManager()
        self.engine = TraceabilityEngine(self.req_manager)

    def test_add_link(self):
        link = self.engine.add_link("src_id", "tgt_id", TraceLinkType.DERIVES)
        assert link.id is not None
        assert link.link_type == TraceLinkType.DERIVES

    def test_get_links(self):
        self.engine.add_link("src", "tgt")
        links = self.engine.get_links_for("src")
        assert len(links) >= 1

    def test_impact_analysis(self):
        r1 = self.req_manager.create_requirement("R1", "Desc 1")
        r2 = self.req_manager.create_requirement("R2", "Desc 2")
        self.engine.add_link(r1.id, r2.id)
        analysis = self.engine.impact_analysis(r1.id)
        assert analysis["affected_count"] >= 0

    def test_coverage_analysis(self):
        r1 = self.req_manager.create_requirement("R1", "Desc")
        self.engine.add_link(r1.id, "ext_id")
        coverage = self.engine.coverage_analysis()
        assert coverage["total_requirements"] >= 1

    def test_traceability_matrix(self):
        r1 = self.req_manager.create_requirement("R1", "Desc")
        self.engine.add_link(r1.id, "ext_id")
        matrix = self.engine.generate_traceability_matrix()
        assert "matrix" in matrix


class TestRequirementValidator:
    def setup_method(self):
        self.manager = RequirementManager()
        self.validator = RequirementValidator(self.manager)

    def test_validate_requirement(self):
        req = self.manager.create_requirement(
            "Test", "The system shall do X with accuracy of 99.9%",
        )
        issues = self.validator.validate(req)
        assert isinstance(issues, list)

    def test_validate_all(self):
        self.manager.create_requirement("R1", "The system shall fly")
        result = self.validator.validate_all()
        assert result["total_requirements"] >= 1
        assert "by_severity" in result

    def test_generate_validation_report(self):
        self.manager.create_requirement("R1", "A requirement description")
        report = self.validator.generate_validation_report()
        assert report["summary"]["total_requirements"] >= 1
        assert "recommendations" in report

    def test_check_completeness(self):
        req = self.manager.create_requirement("R1", "Desc")
        missing = self.validator.check_completeness(req)
        assert "Owner is not assigned" in missing