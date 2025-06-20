"""
Integration tests for configuration API endpoints.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from ingenious.configuration.domain.models import (
    Configuration,
    ConfigurationSection,
    ConfigurationType,
)


class TestConfigurationAPI:
    """Test cases for configuration API endpoints."""

    @pytest.fixture
    def mock_configuration_service(self):
        """Mock configuration service."""
        return Mock()

    @pytest.fixture
    def sample_configuration(self):
        """Sample configuration for testing."""
        return Configuration(
            name="test_config",
            config_type=ConfigurationType.APPLICATION,
            sections=[
                ConfigurationSection(
                    name="database", settings={"host": "localhost", "port": 5432}
                )
            ],
        )

    @pytest.mark.asyncio
    async def test_get_configuration_success(
        self, async_client, mock_configuration_service, sample_configuration
    ):
        """Test successful configuration retrieval."""
        mock_configuration_service.get_configuration = AsyncMock(
            return_value=sample_configuration
        )

        response = await async_client.get("/api/configuration/test_config")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test_config"
        assert data["config_type"] == "APPLICATION"
        assert len(data["sections"]) == 1

    @pytest.mark.asyncio
    async def test_get_configuration_not_found(
        self, async_client, mock_configuration_service
    ):
        """Test configuration not found."""
        mock_configuration_service.get_configuration = AsyncMock(return_value=None)

        response = await async_client.get("/api/configuration/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_create_configuration_success(
        self, async_client, mock_configuration_service, sample_configuration
    ):
        """Test successful configuration creation."""
        mock_configuration_service.create_configuration = AsyncMock(
            return_value=sample_configuration
        )

        config_data = {
            "name": "new_config",
            "config_type": "APPLICATION",
            "sections": [{"name": "api", "settings": {"timeout": 30, "retries": 3}}],
        }

        response = await async_client.post("/api/configuration", json=config_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new_config"

    @pytest.mark.asyncio
    async def test_update_configuration_success(
        self, async_client, mock_configuration_service, sample_configuration
    ):
        """Test successful configuration update."""
        updated_config = Configuration(
            name="test_config",
            config_type=ConfigurationType.APPLICATION,
            sections=[
                ConfigurationSection(
                    name="database", settings={"host": "updated-host", "port": 5433}
                )
            ],
        )

        mock_configuration_service.update_configuration = AsyncMock(
            return_value=updated_config
        )

        update_data = {
            "sections": [
                {"name": "database", "settings": {"host": "updated-host", "port": 5433}}
            ]
        }

        response = await async_client.put(
            "/api/configuration/test_config", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sections"][0]["settings"]["host"] == "updated-host"

    @pytest.mark.asyncio
    async def test_delete_configuration_success(
        self, async_client, mock_configuration_service
    ):
        """Test successful configuration deletion."""
        mock_configuration_service.delete_configuration = AsyncMock(return_value=True)

        response = await async_client.delete("/api/configuration/test_config")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_configuration_not_found(
        self, async_client, mock_configuration_service
    ):
        """Test deleting non-existent configuration."""
        mock_configuration_service.delete_configuration = AsyncMock(return_value=False)

        response = await async_client.delete("/api/configuration/nonexistent")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_configurations(
        self, async_client, mock_configuration_service, sample_configuration
    ):
        """Test listing all configurations."""
        configs = [sample_configuration]
        mock_configuration_service.list_configurations = AsyncMock(return_value=configs)

        response = await async_client.get("/api/configuration")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "test_config"

    @pytest.mark.asyncio
    async def test_get_configuration_section(
        self, async_client, mock_configuration_service
    ):
        """Test getting a specific configuration section."""
        section = ConfigurationSection(
            name="database", settings={"host": "localhost", "port": 5432}
        )
        mock_configuration_service.get_configuration_section = AsyncMock(
            return_value=section
        )

        response = await async_client.get("/api/configuration/test_config/database")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "database"
        assert data["settings"]["host"] == "localhost"

    @pytest.mark.asyncio
    async def test_create_configuration_validation_error(self, async_client):
        """Test configuration creation with validation errors."""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "config_type": "INVALID_TYPE",
            "sections": [],
        }

        response = await async_client.post("/api/configuration", json=invalid_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_configuration_api_error_handling(
        self, async_client, mock_configuration_service
    ):
        """Test API error handling for configuration operations."""
        mock_configuration_service.get_configuration = AsyncMock(
            side_effect=Exception("Database connection error")
        )

        response = await async_client.get("/api/configuration/test_config")

        assert response.status_code == 500
        data = response.json()
        assert "internal server error" in data["detail"].lower()


class TestConfigurationAPIIntegration:
    """Integration tests for configuration API workflows."""

    @pytest.mark.asyncio
    async def test_configuration_crud_workflow(
        self, async_client, mock_configuration_service
    ):
        """Test complete CRUD workflow for configurations."""
        # Create configuration
        config_data = {
            "name": "test_workflow",
            "config_type": "APPLICATION",
            "sections": [
                {"name": "logging", "settings": {"level": "INFO", "format": "json"}}
            ],
        }

        created_config = Configuration(
            name="test_workflow",
            config_type=ConfigurationType.APPLICATION,
            sections=[
                ConfigurationSection(
                    name="logging", settings={"level": "INFO", "format": "json"}
                )
            ],
        )

        mock_configuration_service.create_configuration = AsyncMock(
            return_value=created_config
        )

        create_response = await async_client.post(
            "/api/configuration", json=config_data
        )
        assert create_response.status_code == 201

        # Read configuration
        mock_configuration_service.get_configuration = AsyncMock(
            return_value=created_config
        )

        read_response = await async_client.get("/api/configuration/test_workflow")
        assert read_response.status_code == 200

        # Update configuration
        updated_config = Configuration(
            name="test_workflow",
            config_type=ConfigurationType.APPLICATION,
            sections=[
                ConfigurationSection(
                    name="logging", settings={"level": "DEBUG", "format": "text"}
                )
            ],
        )

        mock_configuration_service.update_configuration = AsyncMock(
            return_value=updated_config
        )

        update_data = {
            "sections": [
                {"name": "logging", "settings": {"level": "DEBUG", "format": "text"}}
            ]
        }

        update_response = await async_client.put(
            "/api/configuration/test_workflow", json=update_data
        )
        assert update_response.status_code == 200

        # Delete configuration
        mock_configuration_service.delete_configuration = AsyncMock(return_value=True)

        delete_response = await async_client.delete("/api/configuration/test_workflow")
        assert delete_response.status_code == 204

    @pytest.mark.asyncio
    async def test_configuration_section_management(
        self, async_client, mock_configuration_service
    ):
        """Test configuration section management."""
        # Add section to existing configuration
        section_data = {
            "name": "new_section",
            "settings": {"key1": "value1", "key2": "value2"},
        }

        new_section = ConfigurationSection(
            name="new_section", settings={"key1": "value1", "key2": "value2"}
        )

        mock_configuration_service.add_configuration_section = AsyncMock(
            return_value=new_section
        )

        response = await async_client.post(
            "/api/configuration/test_config/sections", json=section_data
        )
        assert response.status_code == 201

        # Update section
        mock_configuration_service.update_configuration_section = AsyncMock(
            return_value=new_section
        )

        update_section_data = {"settings": {"key1": "updated_value1", "key3": "value3"}}

        response = await async_client.put(
            "/api/configuration/test_config/sections/new_section",
            json=update_section_data,
        )
        assert response.status_code == 200

        # Delete section
        mock_configuration_service.delete_configuration_section = AsyncMock(
            return_value=True
        )

        response = await async_client.delete(
            "/api/configuration/test_config/sections/new_section"
        )
        assert response.status_code == 204
