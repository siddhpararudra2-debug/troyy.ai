"""
Engineering OS - Main Application Entry Point
FastAPI application that integrates all Sprint 1, Sprint 2, Sprint3, and Sprint 5 components.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.model_orchestrator import ModelOrchestrator
from agents.agent_registry import AgentRegistry
from agents.agent_runtime import AgentRuntime
from agents.task_manager import TaskManager
from agents.communication_bus import CommunicationBus
from agents.specialized_agents import (
    MechanicalAgent, ElectronicsAgent, PCBAgent, 
    FirmwareAgent, SimulationAgent, DocumentationAgent
)
from api.routes import router, set_orchestrator, set_agent_runtime
from database.session import db_manager
from app.cad.routes.cad_routes import router as cad_router
from app.calculations.router import router as calculations_router
from app.simulation.routes.simulation_routes import router as simulation_router
from app.digital_twin_ecosystem.routes.digital_twin_ecosystem_routes import router as digital_twin_router
from app.engineering_os.routes.engineering_os_routes import sprint8_router, sprint9_router
from api.routes_sprint13 import router as sprint13_router
from api.routes_sprint14 import router as sprint14_router
from api.routes_sprint16 import router as sprint16_router
from api.routes_sprint17 import router as sprint17_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan managing startup and shutdown."""
    logger.info("Starting Engineering OS...")
    
    # Initialize model orchestrator
    orchestrator = ModelOrchestrator()
    await orchestrator.initialize()
    set_orchestrator(orchestrator)
    
    # Initialize database
    try:
        await db_manager.initialize()
        await db_manager.create_tables()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")
    
    # Initialize agent framework
    registry = AgentRegistry()
    bus = CommunicationBus()
    task_manager = TaskManager(registry, bus)
    runtime = AgentRuntime(registry, task_manager, bus)
    
    # Register specialized agents
    registry.register(MechanicalAgent(orchestrator))
    registry.register(ElectronicsAgent(orchestrator))
    registry.register(PCBAgent(orchestrator))
    registry.register(FirmwareAgent(orchestrator))
    registry.register(SimulationAgent(orchestrator))
    registry.register(DocumentationAgent(orchestrator))
    
    await runtime.start()
    set_agent_runtime(runtime)
    logger.info(f"Agent runtime started with {registry.count()} agents")
    
    logger.info("Engineering OS ready")
    
    yield
    
    # Shutdown
    await runtime.stop()
    await orchestrator.shutdown()
    await db_manager.close()
    logger.info("Engineering OS shut down")


app = FastAPI(
    title="Engineering OS",
    description="Local Engineering Operating System with AI-powered multi-agent framework",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")
app.include_router(calculations_router, prefix="/api/v1")
app.include_router(cad_router, prefix="/api/v1")
app.include_router(simulation_router, prefix="/api/v1")
app.include_router(digital_twin_router, prefix="/api/v1")
app.include_router(sprint8_router, prefix="/api/v1")
app.include_router(sprint9_router, prefix="/api/v1")
app.include_router(sprint13_router, prefix="/api/v1")
app.include_router(sprint14_router, prefix="/api/v1")
app.include_router(sprint16_router, prefix="/api/v1")
app.include_router(sprint17_router, prefix="/api/v1")

# Mount frontend static files (if built)
# from fastapi.staticfiles import StaticFiles
# app.mount("/", StaticFiles(directory="frontend/out", html=True), name="frontend")


@app.get("/")
async def root():
    return {
        "system": "Engineering OS",
        "version": "1.0.0",
        "components": [
            "Local AI Infrastructure (Ollama + DeepSeek + Qwen)",
            "Engineering Workspace Dashboard",
            "Project Memory System",
            "Engineering Knowledge System (RAG + Qdrant)",
            "Multi-Agent Framework",
            "Engineering Mathematics & Physics (Sprint 2)",
            "Mechanical Design & CAD Generation Platform (Sprint 3)",
            "Simulation, FEA/CFD, Optimization & Digital Twins (Sprint 5)",
        ],
        "docs": "/docs",
        "api": "/api/v1/health",
    }