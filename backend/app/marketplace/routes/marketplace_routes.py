"""
Marketplace Routes
"""
from fastapi import APIRouter
from app.marketplace.schemas.schemas import (
    PluginListResponse,
    InstallPluginRequest,
    InstallPluginResponse,
    ExecutePluginRequest,
    ExecutePluginResponse
)
from app.marketplace.services.marketplace_service import MarketplaceService
from app.marketplace.services.plugin_manager import PluginManager
from app.marketplace.services.plugin_runtime import PluginRuntime

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

marketplace_service = MarketplaceService()
plugin_manager = PluginManager()
plugin_runtime = PluginRuntime()


@router.get("/plugins", response_model=PluginListResponse)
async def list_plugins():
    plugins = marketplace_service.list_plugins()
    return PluginListResponse(plugins=plugins)


@router.post("/plugins/install", response_model=InstallPluginResponse)
async def install_plugin(request: InstallPluginRequest):
    result = plugin_manager.install_plugin(request.plugin_id, request.tenant_id)
    return InstallPluginResponse(**result)


@router.post("/plugins/execute", response_model=ExecutePluginResponse)
async def execute_plugin(request: ExecutePluginRequest):
    result = plugin_runtime.execute_plugin(request.plugin_id, request.payload)
    return ExecutePluginResponse(**result)
