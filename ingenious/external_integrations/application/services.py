"""
External integrations application services.

This module contains the application services that orchestrate business logic
for external service integrations.
"""

from typing import Any, Dict, List, Optional

from ..domain.services import IContentModerationService, ILLMService


class LLMCompletionUseCase:
    """Use case for LLM completion operations."""

    def __init__(self, llm_service: ILLMService):
        self._llm_service = llm_service

    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get completion from LLM service."""
        return await self._llm_service.get_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def get_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """Get streaming completion from LLM service."""
        async for chunk in self._llm_service.get_streaming_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk


class ContentModerationUseCase:
    """Use case for content moderation operations."""

    def __init__(self, moderation_service: IContentModerationService):
        self._moderation_service = moderation_service

    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content for policy violations."""
        return await self._moderation_service.moderate_content(content)


class HealthCheckUseCase:
    """Use case for external service health checks."""

    def __init__(
        self, llm_service: ILLMService, moderation_service: IContentModerationService
    ):
        self._llm_service = llm_service
        self._moderation_service = moderation_service

    async def check_llm_service_health(self) -> bool:
        """Check if LLM service is healthy."""
        return await self._llm_service.is_healthy()

    async def check_moderation_service_health(self) -> bool:
        """Check if moderation service is healthy."""
        return await self._moderation_service.is_healthy()

    async def check_all_services_health(self) -> Dict[str, bool]:
        """Check health of all external services."""
        return {
            "llm_service": await self.check_llm_service_health(),
            "moderation_service": await self.check_moderation_service_health(),
        }


class ExternalIntegrationsApplicationService:
    """Main application service for external integrations."""

    def __init__(
        self,
        llm_completion_use_case: LLMCompletionUseCase,
        content_moderation_use_case: ContentModerationUseCase,
        health_check_use_case: HealthCheckUseCase,
    ):
        self._llm_completion = llm_completion_use_case
        self._content_moderation = content_moderation_use_case
        self._health_check = health_check_use_case

    async def get_llm_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get completion from LLM service."""
        return await self._llm_completion.get_completion(
            messages, model, temperature, max_tokens
        )

    async def get_streaming_llm_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """Get streaming completion from LLM service."""
        async for chunk in self._llm_completion.get_streaming_completion(
            messages, model, temperature, max_tokens
        ):
            yield chunk

    async def moderate_content(self, content: str) -> Dict[str, Any]:
        """Moderate content for policy violations."""
        return await self._content_moderation.moderate_content(content)

    async def check_service_health(self) -> Dict[str, bool]:
        """Check health of all external services."""
        return await self._health_check.check_all_services_health()
