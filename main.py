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

@app.get("/")
async def root():
    return {
        "system": "Autonomous Engineering Organization Platform",
        "modules": [
            "Verification/HIL (Day 31)", "Multi-Agent Swarm (Day 32)", 
            "Project Execution (Day 33)", "Review Council (Day 34)", 
            "Engineering Org (Day 35)", "Aerospace Preliminary Sizing",
            "Advanced Simulation & Digital Twin", "Validation Engine",
            "Multi-Physics Simulation Execution", "Enterprise Collaboration Platform"
        ],
        "docs": "/docs"
    }

