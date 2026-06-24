# Sprint 2 Quick Start Guide

## Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 14+ (optional, for full persistence)
- Redis (optional, for caching)

### Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API server
uvicorn main:app --reload

# 3. Access the API
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Basic Usage Examples

### 1. Validate a Formula

```python
import asyncio
from validation.formula_validator import FormulaValidator

async def validate_formula():
    validator = FormulaValidator()
    result = await validator.validate_formula(
        "stress = force / area",
        "stress_calculation"
    )
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.errors}")
    print(f"Time (ms): {result.validation_time_ms}")

asyncio.run(validate_formula())
```

### 2. Make a Design Decision

```python
import asyncio
from reasoning.decision_engine import EngineeringDecisionEngine, DecisionType, DesignOption

async def make_decision():
    engine = EngineeringDecisionEngine()
    
    # Create decision
    decision = await engine.create_decision(
        "dec_1",
        "design_1",
        "Select Material",
        DecisionType.MATERIAL_SELECTION
    )
    
    # Add options
    options = [
        DesignOption("opt_1", "Steel", "Strong and durable"),
        DesignOption("opt_2", "Aluminum", "Lightweight"),
        DesignOption("opt_3", "Titanium", "Premium")
    ]
    
    for opt in options:
        await engine.add_option(decision, opt)
    
    # Evaluate
    evaluation = await engine.evaluate_options(decision)
    print(f"Best option: {evaluation.best_option}")
    
    # Get recommendations
    recommendations = await engine.generate_recommendations(decision)
    print(f"Recommendations: {recommendations}")

asyncio.run(make_decision())
```

### 3. Optimize a Design

```python
import asyncio
from calculations.optimization_engine import (
    OptimizationEngine, Objective, DesignVariable, ObjectiveType
)

async def optimize_design():
    engine = OptimizationEngine()
    
    # Create optimization run
    run = await engine.create_optimization("opt_1", "design_1")
    
    # Add objectives: minimize weight and cost
    await engine.add_objective(
        run,
        Objective("Weight", ObjectiveType.MINIMIZE, 0.6)
    )
    await engine.add_objective(
        run,
        Objective("Cost", ObjectiveType.MINIMIZE, 0.4)
    )
    
    # Add design variables
    await engine.add_design_variable(
        run,
        DesignVariable("Thickness", 1.0, 10.0, 5.0)
    )
    await engine.add_design_variable(
        run,
        DesignVariable("Material Density", 2700, 8960, 5500)
    )
    
    # Run optimization
    result = await engine.optimize_genetic_algorithm(run)
    print(f"Generations: {result.generations}")
    print(f"Best Fitness: {result.best_fitness}")
    print(f"Solutions: {len(result.pareto_frontier)} Pareto optimal solutions")

asyncio.run(optimize_design())
```

### 4. Execute Full Workflow

```python
import asyncio
from engineering_core.orchestrator import EngineeringOrchestrator

async def run_workflow():
    orchestrator = EngineeringOrchestrator()
    
    # Create workflow
    workflow = await orchestrator.create_workflow(
        "wf_1",
        "design_1",
        "Complete Product Design"
    )
    
    # Execute workflow
    result = await orchestrator.execute_workflow(workflow)
    print(f"Workflow Status: {workflow.status}")
    
    # Generate report
    report = await orchestrator.generate_workflow_report(workflow)
    print(f"Report Generated: {report.report_id}")

asyncio.run(run_workflow())
```

### 5. Generate Engineering Report

```python
import asyncio
from reports.report_system import ReportGenerator

async def generate_report():
    generator = ReportGenerator()
    
    # Create report
    report = await generator.create_calculation_report(
        "report_1",
        "design_1",
        "Product Name"
    )
    
    # Export to markdown
    markdown = await report.export_to_markdown()
    print(markdown)
    
    # Export to JSON
    json_data = await report.export_to_json()
    print(json_data)

asyncio.run(generate_report())
```

## API Endpoint Examples

### Using curl

```bash
# Health check
curl -X GET "http://localhost:8000/api/engineering/health"

# Validate formula
curl -X POST "http://localhost:8000/api/engineering/validate/formula" \
  -H "Content-Type: application/json" \
  -d '{
    "formula": "stress = force / area",
    "formula_id": "test_1"
  }'

# Create decision
curl -X POST "http://localhost:8000/api/engineering/decision/create" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Material Selection",
    "description": "Choose material for component",
    "decision_type": "material_selection",
    "design_id": "design_1"
  }'

# Optimize design
curl -X POST "http://localhost:8000/api/engineering/optimize/design" \
  -H "Content-Type: application/json" \
  -d '{
    "design_id": "design_1",
    "objectives": [{"name": "weight", "type": "minimize"}],
    "variables": [{"name": "thickness", "lower": 1.0, "upper": 10.0}]
  }'

# Execute workflow
curl -X POST "http://localhost:8000/api/engineering/workflow/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "design_id": "design_1",
    "design_name": "Test Design",
    "include_optimization": true,
    "include_reasoning": true
  }'
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/engineering/health")
print(response.json())

# Validate formula
payload = {
    "formula": "E = m * c**2",
    "formula_id": "einstein"
}
response = requests.post(
    "http://localhost:8000/api/engineering/validate/formula",
    json=payload
)
print(response.json())

# Execute workflow
payload = {
    "design_id": "design_1",
    "design_name": "New Product",
    "include_optimization": True,
    "include_reasoning": True
}
response = requests.post(
    "http://localhost:8000/api/engineering/workflow/execute",
    json=payload
)
print(response.json())
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=validation --cov=reasoning --cov=calculations \
  --cov=reports --cov=knowledge_network --cov=engineering_core \
  --cov=api --cov-report=html

# Run specific test file
pytest tests/test_optimization_engine.py -v

# Run with detailed output
pytest tests/ -vv -s

# Run only async tests
pytest tests/ -m asyncio -v
```

## Configuration

### Environment Variables

```bash
# Database
export DATABASE_URL="postgresql://user:password@localhost/troy_ai"

# Redis
export REDIS_URL="redis://localhost:6379"

# Logging
export LOG_LEVEL="INFO"
```

### main.py Integration

The Sprint 2 API is automatically registered in `main.py`:

```python
from api.routes_sprint2 import router as engineering_core_router
app.include_router(engineering_core_router)
```

## Common Tasks

### Search Formulas

```bash
curl "http://localhost:8000/api/engineering/formulas/search?query=stress&domain=mechanics"
```

### Create Review

```bash
curl -X POST "http://localhost:8000/api/engineering/review/create" \
  -H "Content-Type: application/json" \
  -d '{"design_id": "design_1", "category": "design"}'
```

### Analyze Constraints

```bash
curl -X POST "http://localhost:8000/api/engineering/constraints/analyze"
```

### Generate Report

```bash
curl -X POST "http://localhost:8000/api/engineering/report/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "design_id": "design_1",
    "design_name": "Product",
    "report_type": "calculation",
    "title": "Design Report",
    "content": {}
  }'
```

## Troubleshooting

### ImportError for modules

**Solution**: Ensure all modules are in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Async warnings in tests

**Solution**: The test configuration already handles this:
```bash
pytest tests/ -v  # asyncio_mode=auto is configured
```

### Database connection errors

**Solution**: Start without database (in-memory mode):
```python
# Modules will work with dummy data
# Real persistence requires PostgreSQL
```

### Test timeouts

**Solution**: Increase pytest timeout:
```bash
pytest tests/ --timeout=300 -v
```

## Documentation

- **Full Guide**: See `SPRINT2_COMPLETE.md`
- **Status Report**: See `SPRINT2_STATUS.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Test Coverage**: `htmlcov/index.html` (after running coverage)

## Next Steps

1. **Explore the API**: Open http://localhost:8000/docs in browser
2. **Run Tests**: `pytest tests/ -v`
3. **Try Examples**: Copy-paste examples from this guide
4. **Read Documentation**: Check `SPRINT2_COMPLETE.md` for details
5. **Integrate**: Use engines in your own code

## Architecture Overview

```
User Request
    ↓
FastAPI Router (api/routes_sprint2.py)
    ↓
Engine (validation, reasoning, optimization, etc.)
    ↓
Database Model (sprint2_models.py)
    ↓
PostgreSQL (persistent storage)
```

## Support Files

- **Core Modules**: `validation/`, `reasoning/`, `calculations/`, `reports/`, `knowledge_network/`, `engineering_core/`
- **Tests**: `tests/test_*.py`
- **Database**: `database/sprint2_models.py`
- **API**: `api/routes_sprint2.py`
- **Main App**: `main.py`

---

**Status**: Sprint 2 Complete and Production Ready ✅

For questions, refer to `SPRINT2_COMPLETE.md` for comprehensive documentation.
