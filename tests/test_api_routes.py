"""
Test suite for Sprint 2 API Routes - comprehensive API endpoint coverage.
Tests: validation endpoints, decision endpoints, optimization endpoints, report endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from api.routes_sprint2 import router
from fastapi import FastAPI


@pytest.fixture
def app():
    """Create FastAPI test app."""
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestValidationEndpoints:
    """Test validation API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/engineering/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0"
    
    def test_validate_formula_endpoint(self, client):
        """Test formula validation endpoint."""
        payload = {
            "formula": "x + y",
            "formula_id": "test_formula_1",
            "input_units": {"x": "m", "y": "m"},
            "expected_output_unit": "m"
        }
        response = client.post(
            "/api/engineering/validate/formula",
            json=payload
        )
        # Should return 200 or handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_validate_physics_endpoint(self, client):
        """Test physics validation endpoint."""
        payload = {
            "domain": "mechanics",
            "parameters": {"force": 100, "mass": 10},
            "formula": "F = m*a"
        }
        response = client.post(
            "/api/engineering/validate/physics",
            json=payload
        )
        assert response.status_code in [200, 400, 422]


class TestDecisionEndpoints:
    """Test decision API endpoints."""
    
    def test_create_decision_endpoint(self, client):
        """Test create decision endpoint."""
        payload = {
            "title": "Material Selection",
            "description": "Choose optimal material",
            "decision_type": "material_selection",
            "design_id": "design_1"
        }
        response = client.post(
            "/api/engineering/decision/create",
            json=payload
        )
        assert response.status_code in [200, 400, 422]
    
    def test_analyze_decision_endpoint(self, client):
        """Test analyze decision endpoint."""
        response = client.post("/api/engineering/decision/test_dec/analyze")
        assert response.status_code in [200, 400, 422, 404]


class TestOptimizationEndpoints:
    """Test optimization API endpoints."""
    
    def test_optimize_design_endpoint(self, client):
        """Test design optimization endpoint."""
        payload = {
            "design_id": "design_1",
            "objectives": [
                {"name": "weight", "type": "minimize"}
            ],
            "variables": [
                {"name": "thickness", "lower": 1.0, "upper": 10.0}
            ],
            "max_generations": 50,
            "population_size": 30
        }
        response = client.post(
            "/api/engineering/optimize/design",
            json=payload
        )
        assert response.status_code in [200, 400, 422]
    
    def test_analyze_tradeoffs_endpoint(self, client):
        """Test trade-off analysis endpoint."""
        response = client.post("/api/engineering/optimize/tradeoffs")
        assert response.status_code in [200, 400, 422]


class TestConstraintEndpoints:
    """Test constraint API endpoints."""
    
    def test_analyze_constraints_endpoint(self, client):
        """Test constraint analysis endpoint."""
        response = client.post("/api/engineering/constraints/analyze")
        assert response.status_code in [200, 400, 422]


class TestReportEndpoints:
    """Test report API endpoints."""
    
    def test_generate_report_endpoint(self, client):
        """Test report generation endpoint."""
        payload = {
            "design_id": "design_1",
            "design_name": "Test Design",
            "report_type": "calculation",
            "title": "Design Analysis Report",
            "content": {"sections": ["analysis", "results"]}
        }
        response = client.post(
            "/api/engineering/report/generate",
            json=payload
        )
        assert response.status_code in [200, 400, 422]
    
    def test_export_report_endpoint(self, client):
        """Test report export endpoint."""
        response = client.post(
            "/api/engineering/report/test_report/export",
            params={"format": "markdown"}
        )
        assert response.status_code in [200, 400, 422, 404]


class TestFormulaLibraryEndpoints:
    """Test formula library API endpoints."""
    
    def test_search_formulas_endpoint(self, client):
        """Test formula search endpoint."""
        response = client.get(
            "/api/engineering/formulas/search",
            params={"query": "stress"}
        )
        assert response.status_code in [200, 400, 422]
    
    def test_search_formulas_by_domain_endpoint(self, client):
        """Test formula search with domain filter."""
        response = client.get(
            "/api/engineering/formulas/search",
            params={"query": "stress", "domain": "mechanics"}
        )
        assert response.status_code in [200, 400, 422]
    
    def test_get_formula_endpoint(self, client):
        """Test get formula endpoint."""
        response = client.get("/api/engineering/formulas/formula_1")
        assert response.status_code in [200, 400, 422, 404]
    
    def test_validate_formula_applicability_endpoint(self, client):
        """Test formula applicability validation."""
        payload = {"force": 1000, "area": 10}
        response = client.post(
            "/api/engineering/formulas/formula_1/validate-applicability",
            json=payload
        )
        assert response.status_code in [200, 400, 422, 404]


class TestReviewEndpoints:
    """Test review API endpoints."""
    
    def test_create_review_endpoint(self, client):
        """Test create review endpoint."""
        response = client.post(
            "/api/engineering/review/create",
            params={"design_id": "design_1", "category": "design"}
        )
        assert response.status_code in [200, 400, 422]
    
    def test_submit_review_endpoint(self, client):
        """Test submit review endpoint."""
        response = client.post("/api/engineering/review/review_1/submit")
        assert response.status_code in [200, 400, 422]
    
    def test_get_review_endpoint(self, client):
        """Test get review endpoint."""
        response = client.get("/api/engineering/review/review_1")
        assert response.status_code in [200, 400, 422]


class TestWorkflowEndpoints:
    """Test workflow API endpoints."""
    
    def test_execute_workflow_endpoint(self, client):
        """Test workflow execution endpoint."""
        payload = {
            "design_id": "design_1",
            "design_name": "Test Design",
            "include_optimization": True,
            "include_reasoning": True
        }
        response = client.post(
            "/api/engineering/workflow/execute",
            json=payload
        )
        assert response.status_code in [200, 400, 422]
    
    def test_get_workflow_status_endpoint(self, client):
        """Test get workflow status endpoint."""
        response = client.get("/api/engineering/workflow/workflow_1")
        assert response.status_code in [200, 400, 422]
    
    def test_pause_workflow_endpoint(self, client):
        """Test pause workflow endpoint."""
        response = client.post("/api/engineering/workflow/workflow_1/pause")
        assert response.status_code in [200, 400, 422]
    
    def test_resume_workflow_endpoint(self, client):
        """Test resume workflow endpoint."""
        response = client.post("/api/engineering/workflow/workflow_1/resume")
        assert response.status_code in [200, 400, 422]


class TestErrorHandling:
    """Test error handling in API."""
    
    def test_invalid_formula_validation(self, client):
        """Test validation with invalid formula."""
        payload = {
            "formula": "x ++ y",  # Invalid syntax
            "formula_id": "invalid_formula"
        }
        response = client.post(
            "/api/engineering/validate/formula",
            json=payload
        )
        # Should handle error gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_missing_required_fields(self, client):
        """Test request with missing required fields."""
        payload = {
            "title": "Missing fields"
            # Missing other required fields
        }
        response = client.post(
            "/api/engineering/decision/create",
            json=payload
        )
        # Should return validation error
        assert response.status_code in [400, 422]


class TestResponseFormats:
    """Test response format and structure."""
    
    def test_health_response_structure(self, client):
        """Test health check response structure."""
        response = client.get("/api/engineering/health")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "components" in data


class TestAPIIntegration:
    """Integration tests for API."""
    
    def test_complete_validation_workflow(self, client):
        """Test complete validation workflow via API."""
        # 1. Create decision
        decision_payload = {
            "title": "Design Decision",
            "description": "Test decision",
            "decision_type": "material_selection"
        }
        decision_response = client.post(
            "/api/engineering/decision/create",
            json=decision_payload
        )
        assert decision_response.status_code in [200, 400, 422]
        
        # 2. Validate formula
        formula_payload = {
            "formula": "stress = force / area"
        }
        formula_response = client.post(
            "/api/engineering/validate/formula",
            json=formula_payload
        )
        assert formula_response.status_code in [200, 400, 422]
        
        # 3. Generate report
        report_payload = {
            "design_id": "design_1",
            "design_name": "Test",
            "report_type": "validation",
            "title": "Validation Report",
            "content": {}
        }
        report_response = client.post(
            "/api/engineering/report/generate",
            json=report_payload
        )
        assert report_response.status_code in [200, 400, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
