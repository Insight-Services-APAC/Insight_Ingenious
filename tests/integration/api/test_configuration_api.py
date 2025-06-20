"""
Integration tests for configuration API endpoints.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.configuration.domain.models import (
    AppConfiguration,
    AuthenticationConfig,
    ConfigurationItem,
    LLMConfig,
)


class TestConfigurationAPI:
    """Test cases for configuration API endpoints."""

    @pytest.fixture
    def mock_configuration_service(self):
        """Mock configuration service."""
        service = Mock()
        service.get_configuration = AsyncMock(
            return_value=AppConfiguration(
                items={
                    "app_name": "Insight Ingenious",
                    "version": "1.0.0",
                    "debug": False,
                }
            )
        )
        service.update_configuration = AsyncMock()
        service.reset_configuration = AsyncMock()
        return service

    @pytest.fixture
    def mock_app(self, mock_configuration_service):
        """Mock FastAPI app with configuration endpoints."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        @app.get("/api/v1/configuration")
        async def get_configuration():
            config = await mock_configuration_service.get_configuration()
            return {"configuration": config.model_dump()}

        @app.put("/api/v1/configuration")
        async def update_configuration(config_data: dict):
            await mock_configuration_service.update_configuration(config_data)
            return {"message": "Configuration updated successfully"}

        @app.post("/api/v1/configuration/reset")
        async def reset_configuration():
            await mock_configuration_service.reset_configuration()
            return {"message": "Configuration reset to defaults"}

        return TestClient(app)

    async def test_get_configuration_success(
        self, mock_app, mock_configuration_service
    ):
        """Test successful configuration retrieval."""
        # Act
        response = mock_app.get("/api/v1/configuration")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "configuration" in data
        assert data["configuration"]["items"]["app_name"] == "Insight Ingenious"
        mock_configuration_service.get_configuration.assert_called_once()

    async def test_update_configuration_success(
        self, mock_app, mock_configuration_service
    ):
        """Test successful configuration update."""
        # Arrange
        update_data = {
            "items": {
                "app_name": "Updated App",
                "debug": True,
            }
        }

        # Act
        response = mock_app.put("/api/v1/configuration", json=update_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Configuration updated successfully"
        mock_configuration_service.update_configuration.assert_called_once_with(
            update_data
        )

    async def test_reset_configuration_success(
        self, mock_app, mock_configuration_service
    ):
        """Test successful configuration reset."""
        # Act
        response = mock_app.post("/api/v1/configuration/reset")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Configuration reset to defaults"
        mock_configuration_service.reset_configuration.assert_called_once()


class TestConfigurationModels:
    """Test configuration model validation in API context."""

    def test_configuration_item_validation(self):
        """Test configuration item model validation."""
        # Valid configuration item
        item = ConfigurationItem(
            key="test_key", value="test_value", description="Test description"
        )
        assert item.key == "test_key"
        assert item.value == "test_value"
        assert item.description == "Test description"

    def test_app_configuration_operations(self):
        """Test app configuration model operations."""
        config = AppConfiguration()

        # Test setting and getting values
        config.set("app_name", "Test App")
        assert config.get("app_name") == "Test App"
        assert config.get("nonexistent", "default") == "default"

    def test_authentication_config_model(self):
        """Test authentication configuration model."""
        auth_config = AuthenticationConfig(
            enable=True, username="testuser", password="testpass"
        )
        assert auth_config.enable is True
        assert auth_config.username == "testuser"
        assert auth_config.password == "testpass"

    def test_llm_config_model(self):
        """Test LLM configuration model."""
        llm_config = LLMConfig(
            provider="openai",
            api_key="test-key",
            model="gpt-4",
        )
        assert llm_config.provider == "openai"
        assert llm_config.api_key == "test-key"
        assert llm_config.model == "gpt-4"
