"""
Troy — FastAPI Application Entry Point
Main application with lifespan management, router registration, and middleware.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, async_session_factory
from app.core.logging import setup_logging, get_logger

logger = get_logger("main")

# ── SQL Schema ───────────────────────────────────────────────────
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    domain TEXT NOT NULL CHECK(domain IN ('aerospace', 'drones', 'robotics', 'electronics', 'multi')),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'archived')),
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calculations (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    formula_id TEXT NOT NULL,
    title TEXT NOT NULL,
    inputs_json TEXT NOT NULL DEFAULT '{}',
    outputs_json TEXT NOT NULL DEFAULT '{}',
    units_json TEXT DEFAULT '{}',
    execution_time_ms REAL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('completed', 'error', 'pending')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS calculation_steps (
    id TEXT PRIMARY KEY,
    calculation_id TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL CHECK(step_type IN ('symbolic', 'substitution', 'simplification', 'result', 'unit_conversion')),
    description TEXT NOT NULL,
    latex_expression TEXT NOT NULL,
    expression_json TEXT DEFAULT '{}',
    variables_json TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    calculation_id TEXT,
    title TEXT NOT NULL,
    doc_type TEXT NOT NULL CHECK(doc_type IN ('calculation_report', 'project_summary', 'custom')),
    format TEXT NOT NULL DEFAULT 'markdown' CHECK(format IN ('markdown', 'html')),
    content TEXT NOT NULL DEFAULT '',
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_entries (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    entry_type TEXT NOT NULL CHECK(entry_type IN ('decision', 'assumption', 'constraint', 'note', 'reference')),
    content TEXT NOT NULL,
    context TEXT DEFAULT '',
    tags_json TEXT DEFAULT '[]',
    relevance_score REAL DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_calculations_project ON calculations(project_id);
CREATE INDEX IF NOT EXISTS idx_calculations_domain ON calculations(domain);
CREATE INDEX IF NOT EXISTS idx_calc_steps_calc ON calculation_steps(calculation_id);
CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_project ON memory_entries(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_project ON chat_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);

CREATE TABLE IF NOT EXISTS solver_sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    user_query TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS solver_runs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    execution_time_ms REAL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES solver_sessions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_requirements (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    project_type TEXT,
    mission_type TEXT,
    payload TEXT,
    flight_time TEXT,
    missing_requirements TEXT,
    raw_extracted TEXT,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_assumptions (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    missing_information TEXT NOT NULL,
    assumption TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    confidence_score TEXT NOT NULL,
    editable INTEGER NOT NULL DEFAULT 1,
    user_override TEXT,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_constraints (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    category TEXT NOT NULL,
    limit_value TEXT NOT NULL,
    source TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_variables (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    name TEXT NOT NULL,
    value REAL,
    unit TEXT,
    description TEXT,
    var_type TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS solver_recommendations (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    expected_benefits TEXT,
    potential_risks TEXT,
    FOREIGN KEY(run_id) REFERENCES solver_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_solver_runs_session ON solver_runs(session_id);
CREATE INDEX IF NOT EXISTS idx_solver_req_run ON solver_requirements(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_assume_run ON solver_assumptions(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_const_run ON solver_constraints(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_var_run ON solver_variables(run_id);
CREATE INDEX IF NOT EXISTS idx_solver_rec_run ON solver_recommendations(run_id);

CREATE TABLE IF NOT EXISTS validation_runs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    solver_run_id TEXT,
    domain TEXT NOT NULL,
    total_errors INTEGER NOT NULL DEFAULT 0,
    total_warnings INTEGER NOT NULL DEFAULT 0,
    is_approved INTEGER NOT NULL DEFAULT 1 CHECK(is_approved IN (0, 1)),
    execution_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(solver_run_id) REFERENCES solver_runs(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS validation_issues (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('error', 'warning', 'info')),
    category TEXT NOT NULL,
    message TEXT NOT NULL,
    validator_name TEXT NOT NULL,
    engineering_reasoning TEXT,
    recommendation TEXT,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS engineering_reviews (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    design_decisions_check TEXT NOT NULL,
    component_choices_check TEXT NOT NULL,
    structural_choices_check TEXT NOT NULL,
    electrical_choices_check TEXT NOT NULL,
    weight_budgets_check TEXT NOT NULL,
    power_budgets_check TEXT NOT NULL,
    thermal_assumptions_check TEXT NOT NULL,
    overall_assessment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    overall_risk_level TEXT NOT NULL CHECK(overall_risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    risks_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS approval_decisions (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('APPROVED', 'APPROVED WITH CONCERNS', 'REQUIRES REVISION', 'REJECTED')),
    engineering_reasoning TEXT NOT NULL,
    risk_summary TEXT NOT NULL,
    validation_summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_reports (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    report_type TEXT NOT NULL,
    format TEXT NOT NULL CHECK(format IN ('markdown', 'html', 'json', 'pdf')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(run_id) REFERENCES validation_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    action TEXT NOT NULL,
    user_id TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_validation_runs_project ON validation_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_validation_issues_run ON validation_issues(run_id);
CREATE INDEX IF NOT EXISTS idx_reviews_run ON engineering_reviews(run_id);
CREATE INDEX IF NOT EXISTS idx_risks_run ON risk_assessments(run_id);
CREATE INDEX IF NOT EXISTS idx_approvals_run ON approval_decisions(run_id);
CREATE INDEX IF NOT EXISTS idx_audit_reports_run ON audit_reports(run_id);
"""


# ── Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown handlers."""
    # ── Startup ──────────────────────────────────────────────
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Ensure directories exist
    settings.ensure_dirs()

    # Create database tables
    async with engine.begin() as conn:
        for statement in SCHEMA_SQL.strip().split(";"):
            stmt = statement.strip()
            if stmt:
                await conn.execute(text(stmt))
    logger.info("Database tables initialized")

    # Import domain formulas to trigger registration
    _register_all_formulas()

    from app.calculations.registry import registry
    logger.info(f"Formula registry loaded: {registry.count} formulas across {registry.get_domains()}")

    # Create default project if none exists
    async with async_session_factory() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM projects"))
        count = result.scalar()
        if count == 0:
            await session.execute(
                text("""
                    INSERT INTO projects (id, name, description, domain, status)
                    VALUES ('default', 'Default Project', 'Default engineering workspace', 'multi', 'active')
                """)
            )
            await session.commit()
            logger.info("Created default project")

    logger.info(f"✓ {settings.APP_NAME} ready — API at http://localhost:8000{settings.API_V1_PREFIX}")

    yield

    # ── Shutdown ─────────────────────────────────────────────
    logger.info("Shutting down...")
    await engine.dispose()
    logger.info("Database engine disposed")


def _register_all_formulas():
    """Import all domain formula modules to trigger @register_formula decorators."""
    # Aerospace
    import app.domains.aerospace.formulas.aerodynamics  # noqa: F401
    import app.domains.aerospace.formulas.propulsion    # noqa: F401

    # Drones
    import app.domains.drones.formulas.flight_dynamics  # noqa: F401
    import app.domains.drones.formulas.battery          # noqa: F401

    # Robotics
    import app.domains.robotics.formulas.kinematics     # noqa: F401

    # Electronics
    import app.domains.electronics.formulas.circuit_analysis  # noqa: F401


# ── Application Factory ──────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered engineering copilot for Aerospace, Drones, Robotics & Electronics",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ─────────────────────────────────────────────
from app.calculations.router import router as calc_router
from app.projects.router import router as projects_router
from app.memory.router import router as memory_router
from app.memory.chat_router import router as chat_router
from app.documents.router import router as documents_router
from app.solver.router import router as solver_router
from app.validation.routes.validation_routes import router as validation_router
from documentation.routes.api import router as documentation_router

app.include_router(calc_router, prefix=settings.API_V1_PREFIX)
app.include_router(projects_router, prefix=settings.API_V1_PREFIX)
app.include_router(memory_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(solver_router, prefix=settings.API_V1_PREFIX)
app.include_router(validation_router, prefix=settings.API_V1_PREFIX)
app.include_router(documentation_router, prefix=settings.API_V1_PREFIX)



# ── Health Check ─────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    """Application health check endpoint."""
    from app.calculations.registry import registry
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "formulas_loaded": registry.count,
        "domains": registry.get_domains(),
    }
