"""
Model routing service for Engineering OS.
Routes requests to appropriate models based on task type.
"""
import logging
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Types of engineering tasks."""
    CODING = "coding"
    ENGINEERING = "engineering"
    GENERAL_REASONING = "general_reasoning"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    SIMULATION = "simulation"
    DESIGN_REVIEW = "design_review"


class ModelRoute:
    """Defines a routing rule for a model."""

    def __init__(
        self,
        task_type: TaskType,
        primary_model: str,
        fallback_models: list[str],
        system_prompt: str,
    ):
        self.task_type = task_type
        self.primary_model = primary_model
        self.fallback_models = fallback_models
        self.system_prompt = system_prompt


class RoutingService:
    """Routes engineering tasks to appropriate AI models."""

    MODEL_ROUTES = {
        TaskType.CODING: ModelRoute(
            task_type=TaskType.CODING,
            primary_model="qwen-coder",
            fallback_models=["qwen2.5-coder", "codellama", "deepseek-coder"],
            system_prompt=(
                "You are an expert coding assistant. Generate clean, "
                "well-documented, production-ready code. Focus on:\n"
                "- Type safety and error handling\n"
                "- Performance optimization\n"
                "- Testing and validation\n"
                "- Best practices and design patterns"
            ),
        ),
        TaskType.ENGINEERING: ModelRoute(
            task_type=TaskType.ENGINEERING,
            primary_model="deepseek-r1",
            fallback_models=["deepseek-r1:7b", "mixtral", "llama3"],
            system_prompt=(
                "You are an expert engineering assistant specializing in:\n"
                "- Mechanical, electrical, and software engineering\n"
                "- Engineering analysis and calculations\n"
                "- Design reviews and validation\n"
                "- Technical documentation and standards\n"
                "Provide rigorous, technically accurate responses."
            ),
        ),
        TaskType.GENERAL_REASONING: ModelRoute(
            task_type=TaskType.GENERAL_REASONING,
            primary_model="qwen",
            fallback_models=["qwen2.5", "llama3", "mistral"],
            system_prompt=(
                "You are a general-purpose reasoning assistant. "
                "Provide clear, logical, and well-structured responses "
                "to engineering and technical questions."
            ),
        ),
        TaskType.DOCUMENTATION: ModelRoute(
            task_type=TaskType.DOCUMENTATION,
            primary_model="qwen",
            fallback_models=["deepseek-r1", "llama3"],
            system_prompt=(
                "You are a technical documentation specialist. "
                "Generate clear, comprehensive documentation including:\n"
                "- Technical specifications\n"
                "- API documentation\n"
                "- User guides and manuals\n"
                "- Design documents and reports"
            ),
        ),
        TaskType.ANALYSIS: ModelRoute(
            task_type=TaskType.ANALYSIS,
            primary_model="deepseek-r1",
            fallback_models=["qwen", "mixtral"],
            system_prompt=(
                "You are an engineering analysis expert. "
                "Perform detailed analysis including:\n"
                "- Requirements analysis\n"
                "- Trade-off studies\n"
                "- Risk assessment\n"
                "- Performance analysis\n"
                "Provide data-driven conclusions."
            ),
        ),
        TaskType.DESIGN_REVIEW: ModelRoute(
            task_type=TaskType.DESIGN_REVIEW,
            primary_model="deepseek-r1",
            fallback_models=["qwen-coder", "qwen"],
            system_prompt=(
                "You are a senior engineering design reviewer. "
                "Review designs for:\n"
                "- Technical correctness\n"
                "- Safety and compliance\n"
                "- Manufacturing feasibility\n"
                "- Cost optimization\n"
                "Provide actionable feedback."
            ),
        ),
    }

    def __init__(self):
        self._model_health: dict[str, bool] = {}

    def get_route(self, task_type: TaskType) -> ModelRoute:
        """Get the routing configuration for a task type."""
        route = self.MODEL_ROUTES.get(task_type)
        if not route:
            logger.warning(f"No route defined for {task_type}, using general reasoning")
            route = self.MODEL_ROUTES[TaskType.GENERAL_REASONING]
        return route

    def select_model(self, task_type: TaskType) -> tuple[str, str]:
        """
        Select the best available model for a task type.
        Returns (model_name, system_prompt).
        """
        route = self.get_route(task_type)
        
        # Try primary model first
        if self._is_available(route.primary_model):
            logger.info(f"Routing {task_type} to primary model: {route.primary_model}")
            return route.primary_model, route.system_prompt
        
        # Try fallbacks
        for fallback in route.fallback_models:
            if self._is_available(fallback):
                logger.info(f"Routing {task_type} to fallback model: {fallback}")
                return fallback, route.system_prompt
        
        # Last resort: use primary even if unhealthy
        logger.warning(f"No healthy models for {task_type}, using {route.primary_model}")
        return route.primary_model, route.system_prompt

    def update_model_health(self, model_name: str, available: bool):
        """Update the health status of a model."""
        self._model_health[model_name] = available

    def _is_available(self, model_name: str) -> bool:
        """Check if a model is available and healthy."""
        return self._model_health.get(model_name, False)

    def get_available_models(self) -> list[str]:
        """Get list of currently available models."""
        return [name for name, available in self._model_health.items() if available]

    def classify_task(self, query: str) -> TaskType:
        """Classify a user query into a task type based on keywords."""
        query_lower = query.lower()
        
        # Coding keywords
        coding_keywords = [
            "code", "function", "class", "api", "endpoint", "implement",
            "write code", "program", "script", "algorithm", "data structure",
            "debug", "refactor", "typescript", "python", "javascript",
        ]
        if any(kw in query_lower for kw in coding_keywords):
            return TaskType.CODING
        
        # Engineering keywords
        engineering_keywords = [
            "design", "calculate", "analysis", "simulation", "stress",
            "load", "material", "circuit", "structural", "thermal",
            "fluid", "mechanical", "electrical", "tolerance",
        ]
        if any(kw in query_lower for kw in engineering_keywords):
            return TaskType.ENGINEERING
        
        # Documentation keywords
        doc_keywords = [
            "document", "specification", "report", "manual", "guide",
            "readme", "documentation", "writeup",
        ]
        if any(kw in query_lower for kw in doc_keywords):
            return TaskType.DOCUMENTATION
        
        # Default to general reasoning
        return TaskType.GENERAL_REASONING