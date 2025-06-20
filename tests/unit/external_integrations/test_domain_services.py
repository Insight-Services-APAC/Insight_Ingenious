"""
Unit tests for external integrations domain services.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.external_integrations.domain.services import (
    IContentModerationService,
    IExternalServiceRegistry,
    ILLMService,
)


class TestILLMService:
    """Test cases for ILLMService interface."""

    def test_is_abstract_interface(self):
        """Test that ILLMService is an abstract interface."""
        with pytest.raises(TypeError):
            ILLMService()

    @pytest.mark.asyncio
    async def test_generate_response_interface(self):
        """Test generate_response method interface."""
        mock_service = Mock(spec=ILLMService)
        mock_service.generate_response = AsyncMock()

        messages = [{"role": "user", "content": "Hello"}]
        await mock_service.generate_response(messages)

        mock_service.generate_response.assert_called_once_with(messages)

    @pytest.mark.asyncio
    async def test_generate_embedding_interface(self):
        """Test generate_embedding method interface."""
        mock_service = Mock(spec=ILLMService)
        mock_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])

        result = await mock_service.generate_embedding("test text")

        assert result == [0.1, 0.2, 0.3]
        mock_service.generate_embedding.assert_called_once_with("test text")


class TestIContentModerationService:
    """Test cases for IContentModerationService interface."""

    def test_is_abstract_interface(self):
        """Test that IContentModerationService is an abstract interface."""
        with pytest.raises(TypeError):
            IContentModerationService()

    @pytest.mark.asyncio
    async def test_moderate_content_interface(self):
        """Test moderate_content method interface."""
        mock_service = Mock(spec=IContentModerationService)
        mock_service.moderate_content = AsyncMock(
            return_value={"flagged": False, "categories": {}}
        )

        result = await mock_service.moderate_content("safe content")

        assert result == {"flagged": False, "categories": {}}
        mock_service.moderate_content.assert_called_once_with("safe content")


class TestIExternalServiceRegistry:
    """Test cases for IExternalServiceRegistry interface."""

    def test_is_abstract_interface(self):
        """Test that IExternalServiceRegistry is an abstract interface."""
        with pytest.raises(TypeError):
            IExternalServiceRegistry()

    def test_register_service_interface(self):
        """Test register_service method interface."""
        mock_registry = Mock(spec=IExternalServiceRegistry)

        config = {"api_key": "test", "base_url": "https://api.example.com"}
        mock_registry.register_service("openai", config)

        mock_registry.register_service.assert_called_once_with("openai", config)

    def test_get_service_config_interface(self):
        """Test get_service_config method interface."""
        mock_registry = Mock(spec=IExternalServiceRegistry)
        mock_registry.get_service_config.return_value = {
            "api_key": "test",
            "base_url": "https://api.example.com",
        }

        result = mock_registry.get_service_config("openai")

        assert result["api_key"] == "test"
        mock_registry.get_service_config.assert_called_once_with("openai")


class TestDomainServiceInteractions:
    """Test interactions between domain services."""

    @pytest.mark.asyncio
    async def test_llm_service_with_content_moderation(self):
        """Test LLM service working with content moderation."""
        llm_service = Mock(spec=ILLMService)
        moderation_service = Mock(spec=IContentModerationService)

        # Mock content moderation
        moderation_service.moderate_content = AsyncMock(
            return_value={"flagged": False, "categories": {}}
        )

        # Mock LLM response
        llm_service.generate_response = AsyncMock(
            return_value=Mock(content="Safe response")
        )

        # Simulate workflow
        content = "User input"
        moderation_result = await moderation_service.moderate_content(content)

        if not moderation_result["flagged"]:
            messages = [{"role": "user", "content": content}]
            response = await llm_service.generate_response(messages)
            assert response.content == "Safe response"

        moderation_service.moderate_content.assert_called_once_with(content)
        llm_service.generate_response.assert_called_once()

    def test_service_registry_configuration(self):
        """Test service registry configuration management."""
        registry = Mock(spec=IExternalServiceRegistry)
        registry.get_service_config.return_value = None

        # Test missing configuration
        config = registry.get_service_config("unknown_service")
        assert config is None

        # Test registering service
        new_config = {"api_key": "new_key", "timeout": 30}
        registry.register_service("new_service", new_config)

        registry.register_service.assert_called_once_with("new_service", new_config)
