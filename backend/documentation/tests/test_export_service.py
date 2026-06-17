import pytest
import time
from documentation.services.export_service import ExportService
from documentation.services.template_engine import TemplateEngine

class MockDB:
    def query(self, model):
        from documentation.models.database import ProjectReport, CalculationReport
        
        class MockQuery:
            def __init__(self, model):
                self.model = model
            def filter(self, *args): return self
            def first(self): 
                if self.model == ProjectReport:
                    return type('obj', (object,), {
                        'id': 1, 'title': 'Thrust Calc', 'generated_at': '2026-06-16T10:00:00'
                    })()
                elif self.model == CalculationReport:
                    return type('obj', (object,), {
                        'id': 1,
                        'project_report_id': 1,
                        'problem_statement': 'Calculate thrust',
                        'requirements': 'Factor of safety 1.5',
                        'known_variables': {'mass': 1.0},
                        'unknown_variables': {'thrust': 1.5},
                        'assumptions': 'calm weather',
                        'formula_selection': 'T = m * g',
                        'formula_explanation': 'Gravity times mass',
                        'unit_analysis': 'Newton',
                        'substitution_steps': 'T = 1.0 * 9.81',
                        'intermediate_calculations': {},
                        'final_results': {'T': 9.81},
                        'verification_results': 'OK',
                        'engineering_interpretation': 'Thrust is sufficient',
                        'recommendations': 'None'
                    })()
                return None
        return MockQuery(model)

@pytest.mark.asyncio
async def test_export_performance_under_2_seconds():
    db = MockDB()
    service = ExportService(db)
    
    start = time.perf_counter()
    result = service.export_report(1, "MARKDOWN")
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    assert elapsed_ms < 1000, f"Markdown export took {elapsed_ms}ms, exceeding 1s target"
    assert "Engineering Calculation Report" in result["content"]

@pytest.mark.asyncio
async def test_template_engine_caching():
    engine = TemplateEngine()
    
    start = time.perf_counter()
    engine.get_template("AEROSPACE", "CALCULATION")
    engine.get_template("AEROSPACE", "CALCULATION") # Should be cached
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    assert elapsed_ms < 10, "Lru_cache failed to speed up template retrieval"
