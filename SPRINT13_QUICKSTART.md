# SPRINT 13 QUICK START GUIDE

## 🚀 Getting Started in 5 Minutes

### Installation

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy pydantic pytest

# Navigate to project
cd troy.ai
```

### Start the API Server

```bash
# Start FastAPI server
uvicorn main:app --reload --port 8000

# Open browser to http://localhost:8000/docs
```

---

## 📋 Basic Workflow Examples

### 1. Create a Mission

```bash
curl -X POST "http://localhost:8000/api/sprint13/mission/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "UAV Surveillance",
    "description": "Surveillance mission for area",
    "mission_type": "uav",
    "priority": "high"
  }'
```

**Response**:
```json
{
  "id": "mission-uuid",
  "name": "UAV Surveillance",
  "status": "planning",
  "objectives": [],
  "assigned_assets": []
}
```

### 2. Create a Swarm

```bash
curl -X POST "http://localhost:8000/api/sprint13/swarm/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alpha Swarm",
    "swarm_type": "homogeneous",
    "agents": [
      {"id": "uav1", "type": "uav"},
      {"id": "uav2", "type": "uav"},
      {"id": "uav3", "type": "uav"}
    ]
  }'
```

### 3. Form Swarm with Line Formation

```bash
curl -X POST "http://localhost:8000/api/sprint13/swarm/{swarm_id}/form" \
  -H "Content-Type: application/json" \
  -d '{
    "formation_type": "line",
    "formation_spacing": 5.0
  }'
```

**Response**:
```json
{
  "status": "formed",
  "swarm": {
    "formation_type": "line",
    "formation_spacing": 5.0,
    "status": "coordinated"
  }
}
```

### 4. Plan Mission

```bash
curl -X POST "http://localhost:8000/api/sprint13/mission/{mission_id}/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "constraints": {
      "max_flight_time": 120,
      "max_distance": 50
    }
  }'
```

### 5. Generate Scenario

```bash
curl -X POST "http://localhost:8000/api/sprint13/scenario/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Urban Environment",
    "scenario_type": "urban",
    "environment_id": "env-001"
  }'
```

### 6. Run Rehearsal

```bash
curl -X POST "http://localhost:8000/api/sprint13/rehearsal/run" \
  -H "Content-Type: application/json" \
  -d '{
    "mission_id": "mission-uuid",
    "scenario_id": "scenario-uuid",
    "participants": ["pilot1", "navigator1"]
  }'
```

### 7. Check Readiness

```bash
curl -X GET "http://localhost:8000/api/sprint13/readiness/check"
```

**Response**:
```json
{
  "fleet_readiness": 0.92,
  "assets_ready": 18,
  "assets_degraded": 2,
  "assets_unready": 0
}
```

### 8. Issue Command

```bash
curl -X POST "http://localhost:8000/api/sprint13/command/issue" \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": "asset-001",
    "command_type": "mission_start",
    "parameters": {
      "mission_id": "mission-uuid"
    }
  }'
```

### 9. Get Operational Picture

```bash
curl -X GET "http://localhost:8000/api/sprint13/operational-picture"
```

### 10. Run Analytics

```bash
curl -X POST "http://localhost:8000/api/sprint13/analytics/run" \
  -H "Content-Type: application/json" \
  -d '{
    "mission_id": "mission-uuid",
    "analysis_type": "performance"
  }'
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests_sprint13/test_sprint13.py -v

# Run specific test class
pytest tests_sprint13/test_sprint13.py::TestMissionEngine -v

# Run with coverage
pytest tests_sprint13/test_sprint13.py --cov=mission_systems

# Run tests from Python
python -m pytest tests_sprint13/test_sprint13.py -v
```

---

## 🐍 Python Usage Examples

### Example 1: Create and Plan Mission

```python
from mission_systems.mission_engine import MissionEngine
from mission_systems.mission_planner import MissionPlanner

# Create mission
engine = MissionEngine()
mission = engine.create_mission(
    "Survey Mission",
    "Survey designated area",
    "uav"
)

# Plan mission
planner = MissionPlanner()
success, plan, result = planner.create_mission_plan(
    mission.id,
    objectives=[],
    constraints=[]
)

print(f"Mission ID: {mission.id}")
print(f"Plan Status: {plan.status}")
print(f"Efficiency: {plan.efficiency_score}")
```

### Example 2: Coordinate Swarm

```python
from swarm_ops.swarm_manager import SwarmManager, SwarmAgent

# Create swarm
manager = SwarmManager()
agents = [
    SwarmAgent(agent_id=f"uav{i}", agent_type="uav")
    for i in range(5)
]
swarm = manager.create_swarm("Alpha Swarm", "homogeneous", agents)

# Form swarm
success, result = manager.form_swarm(swarm.id, "circle", 10.0)

# Get metrics
metrics = manager.get_swarm_metrics(swarm.id)
print(f"Swarm Status: {swarm.status}")
print(f"Cohesion: {metrics['cohesion']}")
print(f"Efficiency: {metrics['efficiency']}")
```

### Example 3: Issue Commands

```python
from command_control.c2_engine import C2Engine, CommandType

engine = C2Engine()

# Issue command
cmd_id = engine.issue_command(
    CommandType.MISSION_START,
    "asset-001",
    {"mission_id": "m1"},
    "operator1"
)

# Authorize command
engine.authorize_command(cmd_id, "supervisor1")

# Transmit command
engine.transmit_command(cmd_id)

# Execute command
engine.execute_command(cmd_id, {"result": "success"})

print(f"Command Status: {engine.get_command(cmd_id)['status']}")
```

### Example 4: Mission Rehearsal

```python
from rehearsal.rehearsal_engine import RehearsalEngine

engine = RehearsalEngine()

# Create rehearsal
rehearsal_id = engine.create_rehearsal(
    mission_id="m1",
    scenario_id="s1",
    participants=["pilot1", "nav1"]
)

# Run rehearsal
engine.start_rehearsal(rehearsal_id)

# Record events
engine.record_event(rehearsal_id, "communication_issue", 
                   "Radio degradation observed")

# Complete rehearsal
engine.end_rehearsal(rehearsal_id)

# Get results
results = engine.get_rehearsal_result(rehearsal_id)
print(f"Lessons: {results['lessons_learned']}")
```

### Example 5: Digital Twins

```python
from operational_twins.operational_twin import OperationalTwin

# Create twin
twin = OperationalTwin("uav-001", "uav")

# Update state
twin.update_state({
    "position": {"x": 100, "y": 200, "z": 300},
    "velocity": {"vx": 10, "vy": 5, "vz": 0},
    "health": 0.95,
    "battery": 85,
    "status": "active"
})

# Predict future state
prediction = twin.predict_state(time_ahead_minutes=30)

# Detect anomalies
anomalies = twin.detect_anomalies()

print(f"Health: {twin.current_state['health']}")
print(f"Battery: {twin.current_state['battery']}")
print(f"Predicted Battery: {prediction['predicted_battery']}")
```

### Example 6: Analytics

```python
from mission_analytics.analytics_engine import AnalyticsEngine
from mission_analytics.mission_metrics import MissionMetrics

analytics = AnalyticsEngine()
metrics_engine = MissionMetrics()

# Analyze mission
analysis_id = analytics.analyze_mission(
    "mission1",
    {
        "success": True,
        "duration": 120,
        "efficiency": 0.92
    }
)

# Calculate metrics
mission_metrics = metrics_engine.calculate_metrics({
    "id": "mission1",
    "success": True,
    "efficiency": 0.92,
    "safety_score": 0.98
})

print(f"Success: {mission_metrics['success']}")
print(f"Efficiency: {mission_metrics['efficiency']}")
```

### Example 7: Operations Orchestrator

```python
from operations_core.operations_orchestrator import (
    OperationsOrchestrator, 
    OperationPhase
)

orchestrator = OperationsOrchestrator()

# Initiate operation
op_id = orchestrator.initiate_operation(
    "Operation Alpha",
    "mission1",
    ["pilot1", "navigator1"]
)

# Advance through phases
phases = [
    OperationPhase.PLANNING,
    OperationPhase.SIMULATION,
    OperationPhase.REHEARSAL,
    OperationPhase.EXECUTION,
]

for phase in phases:
    orchestrator.advance_phase(op_id, phase)
    print(f"Advanced to {phase.value}")

# Get workflow status
status = orchestrator.get_workflow_status(op_id)
print(f"Current Phase: {status['current_phase']}")
```

---

## 📊 Key Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/mission/create` | POST | Create mission |
| `/mission/{id}` | GET | Get mission details |
| `/missions` | GET | List missions |
| `/mission/{id}/plan` | POST | Plan mission |
| `/swarm/create` | POST | Create swarm |
| `/swarm/{id}/form` | POST | Form swarm |
| `/swarm/{id}` | GET | Get swarm details |
| `/scenario/generate` | POST | Generate scenario |
| `/scenario/{id}` | GET | Get scenario |
| `/rehearsal/run` | POST | Run rehearsal |
| `/analytics/run` | POST | Run analytics |
| `/readiness/check` | GET | Check readiness |
| `/command/issue` | POST | Issue command |
| `/operational-picture` | GET | Get operational picture |
| `/health` | GET | Health check |

---

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/troy_ai
SQLALCHEMY_TRACK_MODIFICATIONS=False

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

---

## 📁 Project Structure

```
troy.ai/
├── mission_systems/          # Module 1
├── swarm_ops/                # Module 2
├── command_control/          # Module 3
├── battlespace/              # Module 4
├── rehearsal/                # Module 5
├── sensor_fusion/            # Module 6
├── operational_twins/        # Module 7
├── logistics_readiness/      # Module 8
├── mission_analytics/        # Module 9
├── operations_core/          # Module 10
├── database/
│   └── sprint13_models.py
├── api/
│   └── routes_sprint13.py
├── tests_sprint13/
│   └── test_sprint13.py
├── main.py
└── SPRINT13_COMPLETE.md
```

---

## 🎯 Next Steps

1. **Review** the 10 modules and their capabilities
2. **Run** the test suite to verify functionality
3. **Explore** API endpoints with Swagger UI at `/docs`
4. **Integrate** with your existing systems
5. **Customize** modules for your specific use case

---

## 🆘 Troubleshooting

### API Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn main:app --port 8001
```

### Import Errors
```bash
# Ensure all modules are in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/troy.ai"
```

### Tests Failing
```bash
# Run with verbose output
pytest tests_sprint13/ -vv

# Run specific test
pytest tests_sprint13/test_sprint13.py::TestMissionEngine::test_create_mission -v
```

---

## 📚 Additional Resources

- [Complete Documentation](SPRINT13_COMPLETE.md)
- [API Documentation](http://localhost:8000/docs)
- [ReDoc](http://localhost:8000/redoc)
- [Source Code Comments](mission_systems/)

---

**Happy Operations!** 🚀

For more information, see the complete Sprint 13 documentation.
