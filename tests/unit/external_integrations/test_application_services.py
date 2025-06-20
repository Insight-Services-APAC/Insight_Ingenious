"""
Unit tests for external integrations application services.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.external_integrations.application.services import (
    ContentModerationUseCase,
    ExternalIntegrationsApplicationService,
    HealthCheckUseCase,
    LLMCompletionUseCase,
)
from ingenious.external_integrations.domain.services import (
    IContentModerationService,
    ILLMService,
)


class TestLLMCompletionUseCase:
    """Test cases for LLMCompletionUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_service = Mock(spec=ILLMService)
        self.use_case = LLMCompletionUseCase(self.mock_llm_service)

    @pytest.mark.asyncio
    async def test_get_completion_success(self):
        """Test successful completion request."""
        messages = [{"role": "user", "content": "Hello"}]
        expected_response = {"choices": [{"message": {"content": "Hi there!"}}]}

        self.mock_llm_service.get_completion = AsyncMock(return_value=expected_response)

        result = await self.use_case.get_completion(messages)

        assert result == expected_response
        self.mock_llm_service.get_completion.assert_called_once_with(
            messages=messages,
            model=None,
            temperature=None,
            max_tokens=None,
        )

    @pytest.mark.asyncio
    async def test_get_completion_with_parameters(self):
        """Test completion request with parameters."""
        messages = [{"role": "user", "content": "Hello"}]
        model = "gpt-4"
        temperature = 0.7
        max_tokens = 100

        self.mock_llm_service.get_completion = AsyncMock(
            return_value={"choices": [{"message": {"content": "Response"}}]}
        )

        await self.use_case.get_completion(
            messages, model=model, temperature=temperature, max_tokens=max_tokens
        )

        self.mock_llm_service.get_completion.assert_called_once_with(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    @pytest.mark.asyncio
    async def test_get_streaming_completion(self):
        """Test streaming completion."""
        messages = [{"role": "user", "content": "Hello"}]
        chunks = ["Hello", " there", "!"]

        async def mock_streaming():
            for chunk in chunks:
                yield chunk

        self.mock_llm_service.get_streaming_completion = Mock(
            return_value=mock_streaming()
        )

        result_chunks = []
        async for chunk in self.use_case.get_streaming_completion(messages):
            result_chunks.append(chunk)

        assert result_chunks == chunks
        self.mock_llm_service.get_streaming_completion.assert_called_once()


class TestContentModerationUseCase:
    """Test cases for ContentModerationUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_moderation_service = Mock(spec=IContentModerationService)
        self.use_case = ContentModerationUseCase(self.mock_moderation_service)

    @pytest.mark.asyncio
    async def test_moderate_content_safe(self):
        """Test moderating safe content."""
        content = "This is safe content"
        expected_result = {
            "flagged": False,
            "categories": {"hate": False, "violence": False},
        }

        self.mock_moderation_service.moderate_content = AsyncMock(
            return_value=expected_result
        )

        result = await self.use_case.moderate_content(content)

        assert result == expected_result
        self.mock_moderation_service.moderate_content.assert_called_once_with(content)

    @pytest.mark.asyncio
    async def test_moderate_content_flagged(self):
        """Test moderating flagged content."""
        content = "Inappropriate content"
        expected_result = {
            "flagged": True,
            "categories": {"hate": True, "violence": False},
        }

        self.mock_moderation_service.moderate_content = AsyncMock(
            return_value=expected_result
        )

        result = await self.use_case.moderate_content(content)

        assert result == expected_result
        assert result["flagged"] is True


class TestHealthCheckUseCase:
    """Test cases for HealthCheckUseCase."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_service = Mock(spec=ILLMService)
        self.mock_moderation_service = Mock(spec=IContentModerationService)
        self.use_case = HealthCheckUseCase(
            self.mock_llm_service, self.mock_moderation_service
        )

    @pytest.mark.asyncio
    async def test_check_llm_service_health_healthy(self):
        """Test LLM service health check when healthy."""
        self.mock_llm_service.is_healthy = AsyncMock(return_value=True)

        result = await self.use_case.check_llm_service_health()

        assert result is True
        self.mock_llm_service.is_healthy.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_llm_service_health_unhealthy(self):
        """Test LLM service health check when unhealthy."""
        self.mock_llm_service.is_healthy = AsyncMock(return_value=False)

        result = await self.use_case.check_llm_service_health()

        assert result is False

    @pytest.mark.asyncio
    async def test_check_moderation_service_health(self):
        """Test moderation service health check."""
        self.mock_moderation_service.is_healthy = AsyncMock(return_value=True)

        result = await self.use_case.check_moderation_service_health()

        assert result is True
        self.mock_moderation_service.is_healthy.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_all_services_health(self):
        """Test checking health of all services."""
        self.mock_llm_service.is_healthy = AsyncMock(return_value=True)
        self.mock_moderation_service.is_healthy = AsyncMock(return_value=False)

        result = await self.use_case.check_all_services_health()

        expected = {
            "llm_service": True,
            "moderation_service": False,
        }
        assert result == expected


class TestExternalIntegrationsApplicationService:
    """Test cases for ExternalIntegrationsApplicationService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm_use_case = Mock(spec=LLMCompletionUseCase)
        self.mock_moderation_use_case = Mock(spec=ContentModerationUseCase)
        self.mock_health_check_use_case = Mock(spec=HealthCheckUseCase)

        self.service = ExternalIntegrationsApplicationService(
            self.mock_llm_use_case,
            self.mock_moderation_use_case,
            self.mock_health_check_use_case,
        )

    @pytest.mark.asyncio
    async def test_get_llm_completion(self):
        """Test getting LLM completion through application service."""
        messages = [{"role": "user", "content": "Hello"}]
        expected_response = {"choices": [{"message": {"content": "Hi!"}}]}

        self.mock_llm_use_case.get_completion = AsyncMock(
            return_value=expected_response
        )

        result = await self.service.get_llm_completion(messages)

        assert result == expected_response
        self.mock_llm_use_case.get_completion.assert_called_once_with(
            messages, None, None, None
        )

    @pytest.mark.asyncio
    async def test_get_streaming_llm_completion(self):
        """Test getting streaming LLM completion."""
        messages = [{"role": "user", "content": "Hello"}]
        chunks = ["Hello", " world"]

        async def mock_streaming():
            for chunk in chunks:
                yield chunk

        self.mock_llm_use_case.get_streaming_completion = Mock(
            return_value=mock_streaming()
        )

        result_chunks = []
        async for chunk in self.service.get_streaming_llm_completion(messages):
            result_chunks.append(chunk)

        assert result_chunks == chunks

    @pytest.mark.asyncio
    async def test_moderate_content(self):
        """Test content moderation through application service."""
        content = "Test content"
        expected_result = {"flagged": False, "categories": {}}

        self.mock_moderation_use_case.moderate_content = AsyncMock(
            return_value=expected_result
        )

        result = await self.service.moderate_content(content)

        assert result == expected_result
        self.mock_moderation_use_case.moderate_content.assert_called_once_with(content)

    @pytest.mark.asyncio
    async def test_check_service_health(self):
        """Test service health check through application service."""
        expected_health = {"llm_service": True, "moderation_service": True}

        self.mock_health_check_use_case.check_all_services_health = AsyncMock(
            return_value=expected_health
        )

        result = await self.service.check_service_health()

        assert result == expected_health
        self.mock_health_check_use_case.check_all_services_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_integration_workflow(self):
        """Test integration workflow with all services."""
        # Test a workflow that uses moderation + LLM completion
        content = "User input"
        moderation_result = {"flagged": False, "categories": {}}
        llm_response = {"choices": [{"message": {"content": "AI response"}}]}

        self.mock_moderation_use_case.moderate_content = AsyncMock(
            return_value=moderation_result
        )
        self.mock_llm_use_case.get_completion = AsyncMock(return_value=llm_response)

        # First moderate the content
        mod_result = await self.service.moderate_content(content)
        assert not mod_result["flagged"]

        # Then get LLM completion if content is safe
        if not mod_result["flagged"]:
            messages = [{"role": "user", "content": content}]
            completion = await self.service.get_llm_completion(messages)
            assert completion == llm_response

        self.mock_moderation_use_case.moderate_content.assert_called_once()
        self.mock_llm_use_case.get_completion.assert_called_once()
