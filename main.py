# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from verification.routes.verification_routes import router as verification_router
from engineering_swarm.routes.swarm_routes import router as swarm_router
from project_execution.routes.execution_routes import router as execution_router
from review_council.routes.review_routes import router as review_router
from engineering_org.routes.org_routes import router as org_router
from advanced_simulation.routes.advanced_sim_routes import router as advanced_sim_router
from aerospace.routes.aero_routes import router as aero_router
from validation.routes.api import router as validation_router
from simulation_execution.routes.simulation_routes import router as simulation_router
from collaboration.routes.collaboration_routes import router as collaboration_router
from api.routes_sprint2 import router as engineering_core_router
from api.routes_sprint13 import router as sprint13_router
from api.routes_sprint12 import router as sprint12_router

app = FastAPI(title="Autonomous Engineering Organization Platform")

app.include_router(verification_router)
app.include_router(swarm_router)
app.include_router(execution_router)
app.include_router(review_router)
app.include_router(org_router)
app.include_router(advanced_sim_router)
app.include_router(aero_router)
app.include_router(validation_router)
app.include_router(simulation_router)
app.include_router(collaboration_router)
app.include_router(engineering_core_router)
app.include_router(sprint13_router)
app.include_router(sprint12_router)


@app.get("/")
async def root():
    return {
        "system": "Autonomous Engineering Organization Platform",
        "current_sprint": "Sprint 12 - Cloud-Native Infrastructure & Sprint 13 - Defense, Mission Systems & Autonomous Operations",
        "modules": [
            "Verification/HIL (Day 31)", "Multi-Agent Swarm (Day 32)", 
            "Project Execution (Day 33)", "Review Council (Day 34)", 
            "Engineering Org (Day 35)", "Aerospace Preliminary Sizing",
            "Advanced Simulation & Digital Twin", "Validation Engine",
            "Multi-Physics Simulation Execution", "Enterprise Collaboration Platform",
            "Mission Systems Platform", "Swarm Coordination",
            "Command & Control", "Digital Battlespace", "Mission Rehearsal",
            "Sensor Fusion", "Operational Twins", "Logistics & Readiness",
            "Mission Analytics", "Operations Orchestrator",
            "Cloud Orchestration (Sprint 12)", "Distributed Agents (Sprint 12)",
            "HPC Platform (Sprint 12)", "Data Platform (Sprint 12)",
            "Event Streaming (Sprint 12)", "Observability Stack (Sprint 12)",
            "Cloud Security (Sprint 12)", "Global Infrastructure (Sprint 12)",
            "Platform Engineering (Sprint 12)", "Cloud Core (Sprint 12)"
        ],
        "docs": "/docs",
        "sprint12_endpoints": "/api/v1/sprint12",
        "sprint13_endpoints": "/api/sprint13"
    }

