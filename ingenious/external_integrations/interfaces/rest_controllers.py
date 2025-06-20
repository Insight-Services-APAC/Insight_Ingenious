"""
External Integrations REST controllers for the external_integrations bounded context.

This module contains FastAPI route handlers for external service integrations
including LLM services, content moderation, and other third-party APIs.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from typing_extensions import Annotated

import ingenious.dependencies as igen_deps
from ingenious.shared.domain.models import HTTPError

from ..application.services import (
    ContentModerationUseCase,
    ExternalIntegrationsApplicationService,
    HealthCheckUseCase,
    LLMCompletionUseCase,
)

logger = logging.getLogger(__name__)


# Request/Response models
class LLMRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class LLMResponse(BaseModel):
    response: str
    model: str
    usage: Dict[str, Any]
    finish_reason: str


class ContentModerationRequest(BaseModel):
    text: str


class ContentModerationResponse(BaseModel):
    flagged: bool
    categories: Dict[str, bool]
    category_scores: Dict[str, float]


class ServiceHealthResponse(BaseModel):
    service_name: str
    status: str  # "healthy" | "degraded" | "unhealthy"
    response_time_ms: Optional[float] = None
    last_check: str


class ExternalIntegrationsController:
    """REST controller for external service integrations."""

    def __init__(
        self, integrations_app_service: ExternalIntegrationsApplicationService
    ):
        self._integrations_app_service = integrations_app_service
        self._router = APIRouter()
        self._setup_routes()

    def _setup_routes(self):
        """Setup the external integrations routes."""
        # LLM operations
        self._router.post(
            "/llm/completions",
            responses={
                200: {"model": LLMResponse, "description": "LLM completion"},
                400: {"model": HTTPError, "description": "Bad request"},
                503: {"model": HTTPError, "description": "Service unavailable"},
            },
        )(self.create_completion)

        self._router.post(
            "/llm/chat",
            responses={
                200: {"model": LLMResponse, "description": "Chat completion"},
                400: {"model": HTTPError, "description": "Bad request"},
                503: {"model": HTTPError, "description": "Service unavailable"},
            },
        )(self.create_chat_completion)

        # Content moderation
        self._router.post(
            "/moderation",
            responses={
                200: {
                    "model": ContentModerationResponse,
                    "description": "Moderation result",
                },
                400: {"model": HTTPError, "description": "Bad request"},
                503: {"model": HTTPError, "description": "Service unavailable"},
            },
        )(self.moderate_content)

        # Service health
        self._router.get(
            "/health",
            responses={
                200: {
                    "model": List[ServiceHealthResponse],
                    "description": "Service health status",
                },
            },
        )(self.get_service_health)

        self._router.get(
            "/health/{service_name}",
            responses={
                200: {
                    "model": ServiceHealthResponse,
                    "description": "Individual service health",
                },
                404: {"model": HTTPError, "description": "Service not found"},
            },
        )(self.get_individual_service_health)

    @property
    def router(self) -> APIRouter:
        """Get the FastAPI router."""
        return self._router

    async def create_completion(
        self,
        llm_request: LLMRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> LLMResponse:
        """Create a text completion using LLM service."""
        try:
            # TODO: Implement actual completion logic
            # This is a placeholder implementation

            logger.info(f"LLM completion requested for model: {llm_request.model}")

            # Placeholder response
            return LLMResponse(
                response="This is a placeholder response. LLM completion not implemented yet.",
                model=llm_request.model or "gpt-3.5-turbo",
                usage={
                    "prompt_tokens": 10,
                    "completion_tokens": 15,
                    "total_tokens": 25,
                },
                finish_reason="stop",
            )

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=503, detail="LLM service unavailable")

    async def create_chat_completion(
        self,
        llm_request: LLMRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> LLMResponse:
        """Create a chat completion using LLM service."""
        try:
            # TODO: Implement actual chat completion logic
            # This is a placeholder implementation

            logger.info(f"Chat completion requested for model: {llm_request.model}")

            # Placeholder response
            return LLMResponse(
                response="This is a placeholder chat response. Chat completion not implemented yet.",
                model=llm_request.model or "gpt-3.5-turbo",
                usage={
                    "prompt_tokens": 20,
                    "completion_tokens": 25,
                    "total_tokens": 45,
                },
                finish_reason="stop",
            )

        except Exception as e:
            logger.exception(e)
            raise HTTPException(status_code=503, detail="Chat service unavailable")

    async def moderate_content(
        self,
        moderation_request: ContentModerationRequest,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> ContentModerationResponse:
        """Moderate content for policy violations."""
        try:
            # TODO: Implement actual content moderation logic
            # This is a placeholder implementation

            logger.info("Content moderation requested")

            # Placeholder response - assume content is safe
            return ContentModerationResponse(
                flagged=False,
                categories={
                    "hate": False,
                    "hate/threatening": False,
                    "self-harm": False,
                    "sexual": False,
                    "sexual/minors": False,
                    "violence": False,
                    "violence/graphic": False,
                },
                category_scores={
                    "hate": 0.001,
                    "hate/threatening": 0.001,
                    "self-harm": 0.001,
                    "sexual": 0.001,
                    "sexual/minors": 0.001,
                    "violence": 0.001,
                    "violence/graphic": 0.001,
                },
            )

        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=503, detail="Content moderation service unavailable"
            )

    async def get_service_health(
        self,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> List[ServiceHealthResponse]:
        """Get health status of all external services."""
        try:
            # TODO: Implement actual health checks
            # This is a placeholder implementation

            services = ["openai", "azure", "content_moderation"]
            health_responses = []

            for service in services:
                health_responses.append(
                    ServiceHealthResponse(
                        service_name=service,
                        status="healthy",
                        response_time_ms=150.5,
                        last_check="2025-06-20T12:00:00Z",
                    )
                )

            return health_responses

        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=500, detail="Failed to check service health"
            )

    async def get_individual_service_health(
        self,
        service_name: str,
        credentials: Annotated[
            HTTPBasicCredentials, Depends(igen_deps.get_security_service)
        ],
    ) -> ServiceHealthResponse:
        """Get health status of a specific external service."""
        try:
            # TODO: Implement actual health check for specific service
            # This is a placeholder implementation

            valid_services = ["openai", "azure", "content_moderation"]

            if service_name not in valid_services:
                raise HTTPException(
                    status_code=404, detail=f"Service '{service_name}' not found"
                )

            return ServiceHealthResponse(
                service_name=service_name,
                status="healthy",
                response_time_ms=120.3,
                last_check="2025-06-20T12:00:00Z",
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check health for service '{service_name}'",
            )


# Create router instance for FastAPI integration
# Note: In production, this should be managed by a DI container


# Mock implementations for now
class MockLLMService:
    async def get_completion(self, **kwargs):
        return {"response": "Mock LLM response", "model": "mock-model"}

    async def get_streaming_completion(self, **kwargs):
        yield {"delta": {"content": "Mock"}}
        yield {"delta": {"content": " streaming"}}
        yield {"delta": {"content": " response"}}

    async def is_healthy(self):
        return True


class MockModerationService:
    async def moderate_content(self, content: str):
        return {"flagged": False, "categories": {}, "category_scores": {}}

    async def is_healthy(self):
        return True


# Create service instances
llm_service = MockLLMService()
moderation_service = MockModerationService()

# Create use cases
llm_completion_use_case = LLMCompletionUseCase(llm_service)
content_moderation_use_case = ContentModerationUseCase(moderation_service)
health_check_use_case = HealthCheckUseCase(llm_service, moderation_service)

# Create application service
integrations_app_service = ExternalIntegrationsApplicationService(
    llm_completion_use_case, content_moderation_use_case, health_check_use_case
)

controller = ExternalIntegrationsController(integrations_app_service)
router = controller.router
