import pytest
from verification.services.test_generation_service import TestGenerationService
from verification.services.sil_service import SILService
from verification.services.coverage_analysis_service import CoverageAnalysisService

def test_test_generation():
    svc = TestGenerationService()
    reqs = [{"id": "REQ-001", "text": "System shall lift 5kg payload", "domain": "MECHANICAL", 
             "verification_method": "TEST", "acceptance_criteria": ["Lifts 5kg"]}]
    report = svc.generate_tests(reqs, "STATEMENT")
    assert report.final_results['total_tests'] >= 1

def test_sil_execution():
    svc = SILService()
    tests = [{"id": "TC-001", "requirement_id": "REQ-001", "title": "Test", "test_type": "SYSTEM",
              "preconditions": [], "steps": [], "expected_results": [], "environment": "SIL", "priority": 3}]
    report = svc.execute_tests(tests, "MODEL-001", seed=42)
    assert report.final_results['total_tests'] == 1
    assert report.final_results['pass_rate_pct'] >= 0

def test_coverage_analysis():
    svc = CoverageAnalysisService()
    results = [{"test_id": "TC-001", "status": "PASSED"}, {"test_id": "TC-002", "status": "PASSED"}]
    report = svc.analyze_coverage(results, "C")
    assert report.final_results['metrics']['statement_pct'] > 0
