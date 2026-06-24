"""
Tests for the Local AI Infrastructure (models) module.
"""
import pytest
from models.health_service import HealthService, ModelHealth, SystemHealth
from models.routing_service import RoutingService, TaskType


class TestHealthService:
    def test_register_model(self):
        service = HealthService()
        health = service.register_model("qwen")
        assert health.model_name == "qwen"
        assert health.available == False

    def test_record_success(self):
        service = HealthService()
        service.record_success("qwen", 1.5)
        health = service.get_model_health("qwen")
        assert health is not None
        assert health.total_requests == 1
        assert health.avg_response_time == 1.5

    def test_record_error(self):
        service = HealthService()
        service.record_error("deepseek")
        health = service.get_model_health("deepseek")
        assert health is not None
        assert health.error_count == 1

    def test_get_system_health(self):
        service = HealthService()
        system = service.get_system_health()
        assert isinstance(system, SystemHealth)
        assert system.ollama_available == False


class TestRoutingService:
    def test_classify_coding(self):
        service = RoutingService()
        assert service.classify_task("Write a Python function") == TaskType.CODING
        assert service.classify_task("Implement API endpoint") == TaskType.CODING
        assert service.classify_task("Debug TypeScript error") == TaskType.CODING

    def test_classify_engineering(self):
        service = RoutingService()
        assert service.classify_task("Calculate stress on beam") == TaskType.ENGINEERING
        assert service.classify_task("Design mechanical system") == TaskType.ENGINEERING

    def test_classify_general(self):
        service = RoutingService()
        assert service.classify_task("What is the meaning of life?") == TaskType.GENERAL_REASONING

    def test_select_model_no_health(self):
        service = RoutingService()
        model, prompt = service.select_model(TaskType.CODING)
        assert model == "qwen-coder"
        assert len(prompt) > 0

    def test_get_route_returns_route(self):
        service = RoutingService()
        route = service.get_route(TaskType.CODING)
        assert route.primary_model == "qwen-coder"
        assert "coding" in route.system_prompt.lower()


class TestModelOrchestrator:
    @pytest.mark.asyncio
    async def test_create_session(self):
        from models.model_orchestrator import ModelOrchestrator
        orch = ModelOrchestrator()
        session = await orch.create_session()
        assert session.session_id is not None
        assert len(session.messages) == 0

    @pytest.mark.asyncio
    async def test_get_session(self):
        from models.model_orchestrator import ModelOrchestrator
        orch = ModelOrchestrator()
        created = await orch.create_session()
        retrieved = await orch.get_session(created.session_id)
        assert retrieved is not None
        assert retrieved.session_id == created.session_id

    @pytest.mark.asyncio
    async def test_get_session_not_found(self):
        from models.model_orchestrator import ModelOrchestrator
        orch = ModelOrchestrator()
        session = await orch.get_session("nonexistent")
        assert session is None