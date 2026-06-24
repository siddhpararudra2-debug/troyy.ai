"""
API Routes for Sprint 8 & 9 Engineering OS
"""
import logging
from fastapi import APIRouter
from app.engineering_os.schemas.schemas import (
    ExecuteAgentRequest,
    DesignGenerateRequest,
    CopilotChatRequest,
    ProjectCreateRequest,
    KnowledgeQueryRequest,
    CreateOrganizationRequest,
    CreateTeamRequest,
    CreateRoleRequest,
    AssignRoleRequest,
    TrackEventRequest,
    StartReviewRequest,
    RequestApprovalRequest,
    UploadDocumentRequest,
    CreateKnowledgeArticleRequest,
    CreatePortfolioRequest,
    CreateTenantRequest,
    LoginWithProviderRequest,
    VerifySessionRequest,
)
from app.engineering_os.operating_system import EngineeringOS
from app.autonomous_design.design_engine import DesignEngine
from app.copilot.engineering_copilot import EngineeringCopilot
from app.program_management.project_manager import ProjectManager
from app.analytics.performance_dashboard import PerformanceDashboard
from app.knowledge_graph.graph_engine import GraphEngine
# Sprint 9 Services
from app.organizations.organization_manager import OrganizationManager
from app.organizations.team_manager import TeamManager
from app.security.role_manager import RoleManager
from app.audit.event_tracker import EventTracker
from app.collaboration.comments_engine import CommentsEngine
from app.collaboration.review_engine import ReviewEngine
from app.documents.document_manager import DocumentManager
from app.enterprise_knowledge.knowledge_manager import KnowledgeManager
from app.portfolio.portfolio_manager import PortfolioManager
from app.enterprise_analytics.executive_dashboard import ExecutiveDashboard
from app.multitenancy.tenant_manager import TenantManager
from app.auth.auth_service import AuthService

# Sprint 8 Router
sprint8_router = APIRouter(prefix="/sprint8", tags=["Sprint 8 Engineering OS"])

# Sprint 9 Router
sprint9_router = APIRouter(prefix="/sprint9", tags=["Sprint 9 Enterprise Engineering OS"])

# Initialize Sprint 8 services
design_engine = DesignEngine()
copilot = EngineeringCopilot()
project_manager = ProjectManager()
analytics = PerformanceDashboard()
knowledge_graph = GraphEngine()

# Initialize Sprint 9 services
org_manager = OrganizationManager()
team_manager = TeamManager()
role_manager = RoleManager()
event_tracker = EventTracker()
comments_engine = CommentsEngine()
review_engine = ReviewEngine()
doc_manager = DocumentManager()
ek_knowledge_manager = KnowledgeManager()
portfolio_manager = PortfolioManager()
executive_dashboard = ExecutiveDashboard()
tenant_manager = TenantManager()
auth_service = AuthService()


@sprint8_router.post("/agent/execute")
async def execute_agent(request: ExecuteAgentRequest):
    """Execute an engineering agent."""
    from agents.task_manager import TaskManager
    from agents.agent_registry import AgentRegistry
    from agents.communication_bus import CommunicationBus
    registry = AgentRegistry()
    bus = CommunicationBus()
    task_manager = TaskManager(registry, bus)
    task_id = "temp_task_id"
    await task_manager.create_task(
        task_id=task_id,
        agent_type=request.agent_type,
        title=request.title,
        description=request.description,
        input_data=request.input_data,
        project_id=request.project_id,
    )
    result = await task_manager.execute_task(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "output": result.output,
    }


@sprint8_router.post("/design/generate")
async def generate_design(request: DesignGenerateRequest):
    """Generate design via autonomous design engine."""
    result = await design_engine.run_design_process(
        requirements=request.requirements,
        project_id=request.project_id,
        max_iterations=request.max_iterations,
    )
    return result


@sprint8_router.post("/copilot/chat")
async def copilot_chat(request: CopilotChatRequest):
    """Chat with engineering copilot."""
    return await copilot.chat(request.message, request.context)


@sprint8_router.post("/projects/create")
async def create_project(request: ProjectCreateRequest):
    """Create a new engineering project."""
    return await project_manager.create_project(request.name, request.requirements)


@sprint8_router.get("/projects/list")
async def list_projects():
    """List all projects."""
    return await project_manager.list_projects()


@sprint8_router.get("/dashboard")
async def get_dashboard(project_id: str = None):
    """Get analytics dashboard."""
    return analytics.get_dashboard(project_id)


@sprint8_router.post("/knowledge/query")
async def query_knowledge(request: KnowledgeQueryRequest):
    """Query engineering knowledge graph."""
    nodes = knowledge_graph.query_nodes(request.node_type)
    return {
        "query": request.query,
        "nodes": nodes,
    }


# Sprint 9 Routes
@sprint9_router.post("/organizations/create")
async def create_organization(request: CreateOrganizationRequest):
    """Create a new organization."""
    return await org_manager.create_organization(
        name=request.name,
        description=request.description,
        org_type=request.org_type,
        tenant_id=request.tenant_id,
    )


@sprint9_router.get("/organizations/{org_id}")
async def get_organization(org_id: str):
    """Get an organization by ID."""
    return await org_manager.get_organization(org_id)


@sprint9_router.post("/teams/create")
async def create_team(request: CreateTeamRequest):
    """Create a new team."""
    return await team_manager.create_team(
        org_id=request.org_id,
        name=request.name,
        description=request.description,
        department_id=request.department_id,
    )


@sprint9_router.get("/teams/{team_id}")
async def get_team(team_id: str):
    """Get a team by ID."""
    return await team_manager.get_team(team_id)


@sprint9_router.post("/roles/create")
async def create_role(request: CreateRoleRequest):
    """Create a custom role."""
    return await role_manager.create_custom_role(
        name=request.name,
        description=request.description,
        permissions=request.permissions,
    )


@sprint9_router.post("/roles/assign")
async def assign_role(request: AssignRoleRequest):
    """Assign a role to a user."""
    return await role_manager.assign_role_to_user(
        user_id=request.user_id,
        role_name=request.role_name,
    )


@sprint9_router.post("/events/track")
async def track_event(request: TrackEventRequest):
    """Track an audit event."""
    return await event_tracker.track_event(
        event_type=request.event_type,
        user_id=request.user_id,
        data=request.data,
        resource_id=request.resource_id,
        tenant_id=request.tenant_id,
    )


@sprint9_router.get("/events")
async def get_events(
    event_type: str = None,
    user_id: str = None,
    resource_id: str = None,
    tenant_id: str = None,
):
    """Get audit events."""
    return await event_tracker.get_events(
        event_type=event_type,
        user_id=user_id,
        resource_id=resource_id,
        tenant_id=tenant_id,
    )


@sprint9_router.post("/reviews/start")
async def start_review(request: StartReviewRequest):
    """Start a review."""
    return await review_engine.start_review(
        resource_id=request.resource_id,
        review_type=request.review_type,
        title=request.title,
        user_id=request.user_id,
        reviewer_ids=request.reviewer_ids,
    )


@sprint9_router.post("/approvals/request")
async def request_approval(request: RequestApprovalRequest):
    """Request an approval."""
    # Use collaboration's approval workflow or a dedicated one
    # For now, we'll just return a simple response
    return {
        "status": "pending",
        "resource_id": request.resource_id,
        "requested_by": request.user_id,
    }


@sprint9_router.post("/documents/upload")
async def upload_document(request: UploadDocumentRequest):
    """Upload a document."""
    return await doc_manager.upload_document(
        name=request.name,
        doc_type=request.doc_type,
        content=request.content,
        project_id=request.project_id,
        tenant_id=request.tenant_id,
    )


@sprint9_router.post("/knowledge/create")
async def create_knowledge_article(request: CreateKnowledgeArticleRequest):
    """Create a knowledge article."""
    return await ek_knowledge_manager.create_article(
        title=request.title,
        content=request.content,
        tags=request.tags,
        tenant_id=request.tenant_id,
    )


@sprint9_router.get("/knowledge/search")
async def search_knowledge(query: str = "", tenant_id: str = None):
    """Search knowledge articles."""
    return await ek_knowledge_manager.search_articles(
        query=query,
        tenant_id=tenant_id,
    )


@sprint9_router.post("/portfolios/create")
async def create_portfolio(request: CreatePortfolioRequest):
    """Create a portfolio."""
    return await portfolio_manager.create_portfolio(
        name=request.name,
        description=request.description,
        tenant_id=request.tenant_id,
    )


@sprint9_router.get("/portfolios/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """Get a portfolio by ID."""
    return await portfolio_manager.get_portfolio(portfolio_id)


@sprint9_router.get("/executive-dashboard")
async def get_executive_dashboard(tenant_id: str = None):
    """Get executive dashboard."""
    return executive_dashboard.get_dashboard(tenant_id)


@sprint9_router.post("/tenants/create")
async def create_tenant(request: CreateTenantRequest):
    """Create a new tenant."""
    return await tenant_manager.create_tenant(
        name=request.name,
        domain=request.domain,
        plan=request.plan,
    )


@sprint9_router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: str):
    """Get a tenant by ID"""
    return await tenant_manager.get_tenant(tenant_id)


# === Authentication Endpoints ===
@sprint9_router.post("/auth/login")
async def login_with_provider(request: LoginWithProviderRequest):
    """Login with OAuth/OIDC/SAML provider"""
    return await auth_service.login_with_provider(
        request.provider, request.code, request.state
    )


@sprint9_router.post("/auth/logout")
async def logout(request: VerifySessionRequest):
    """Logout a user"""
    auth_service.logout(request.session_id)
    return {"status": "logged_out", "session_id": request.session_id}


@sprint9_router.post("/auth/session/verify")
async def verify_session(request: VerifySessionRequest):
    """Verify a session is valid"""
    session = auth_service.verify_session(request.session_id)
    if session:
        return {"valid": True, "session": session}
    return {"valid": False, "session": None}
