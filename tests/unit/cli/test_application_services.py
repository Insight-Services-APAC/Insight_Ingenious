"""
Unit tests for CLI application services.

This module tests the application layer services for the CLI bounded context.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from ingenious.cli.application.services import CLIApplicationService
from ingenious.cli.domain.entities import ProjectConfig, ServerConfig
from ingenious.cli.domain.services import (
    IProjectService,
    IServerService,
    ITemplateService,
)


class TestCLIApplicationService:
    """Test suite for CLIApplicationService."""

    @pytest.fixture
    def mock_project_service(self):
        """Mock project service for testing."""
        mock = Mock(spec=IProjectService)
        mock.create_project.return_value = True
        mock.get_project_config.return_value = ProjectConfig(
            name="test-project", path="/tmp/test-project"
        )
        mock.project_exists.return_value = False
        return mock

    @pytest.fixture
    def mock_server_service(self):
        """Mock server service for testing."""
        mock = Mock(spec=IServerService)
        mock.start_server.return_value = True
        mock.stop_server.return_value = True
        mock.is_running.return_value = False
        return mock

    @pytest.fixture
    def mock_template_service(self):
        """Mock template service for testing."""
        mock = Mock(spec=ITemplateService)
        mock.generate_template.return_value = True
        return mock

    @pytest.fixture
    def cli_service(
        self, mock_project_service, mock_server_service, mock_template_service
    ):
        """Create CLIApplicationService with mocked dependencies."""
        return CLIApplicationService(
            project_service=mock_project_service,
            server_service=mock_server_service,
            template_service=mock_template_service,
        )

    def test_create_project_success(
        self, cli_service, mock_project_service, mock_template_service
    ):
        """Test successful project creation."""
        # Arrange
        project_name = "awesome-project"
        project_path = Path("/tmp/awesome-project")

        # Act
        result = cli_service.create_project(project_name, project_path)

        # Assert
        assert result is True
        mock_project_service.create_project.assert_called_once()
        mock_template_service.generate_template.assert_called_once()

        # Verify project creation was called with correct arguments
        call_args = mock_project_service.create_project.call_args
        config = call_args[0][0]  # ProjectConfig object
        assert config.name == project_name
        assert config.path == str(project_path)

    def test_create_project_already_exists(self, cli_service, mock_project_service):
        """Test project creation when project already exists."""
        # Arrange
        mock_project_service.project_exists.return_value = True
        project_name = "existing-project"
        project_path = Path("/tmp/existing-project")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            cli_service.create_project(project_name, project_path)

        assert "already exists" in str(exc_info.value)
        mock_project_service.create_project.assert_not_called()

    def test_create_project_with_profile(
        self, cli_service, mock_project_service, mock_template_service
    ):
        """Test project creation with specific profile."""
        # Arrange
        project_name = "profiled-project"
        project_path = Path("/tmp/profiled-project")
        profile = "production"

        # Act
        result = cli_service.create_project(project_name, project_path, profile=profile)

        # Assert
        assert result is True

        # Verify profile was passed correctly in the ProjectConfig
        call_args = mock_project_service.create_project.call_args
        project_config = call_args[0][0]  # First argument should be ProjectConfig
        assert project_config.profile == profile

    def test_start_server_success(self, cli_service, mock_server_service):
        """Test successful server start."""
        # Arrange
        server_config = ServerConfig(host="localhost", port=8000)

        # Act
        result = cli_service.start_server(server_config)

        # Assert
        assert result is True
        mock_server_service.start_server.assert_called_once_with(server_config)

    def test_start_server_already_running(self, cli_service, mock_server_service):
        """Test starting server when already running."""
        # Arrange
        mock_server_service.is_running.return_value = True
        server_config = ServerConfig(host="localhost", port=8000)

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            cli_service.start_server(server_config)

        assert "already running" in str(exc_info.value)
        mock_server_service.start_server.assert_not_called()

    def test_stop_server_success(self, cli_service, mock_server_service):
        """Test successful server stop."""
        # Arrange
        mock_server_service.is_running.return_value = True

        # Act
        result = cli_service.stop_server()

        # Assert
        assert result is True
        mock_server_service.stop_server.assert_called_once()

    def test_stop_server_not_running(self, cli_service, mock_server_service):
        """Test stopping server when not running."""
        # Arrange
        mock_server_service.is_running.return_value = False

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            cli_service.stop_server()

        assert "not running" in str(exc_info.value)
        mock_server_service.stop_server.assert_not_called()

    def test_get_project_info_success(self, cli_service, mock_project_service):
        """Test getting project information."""
        # Arrange
        project_path = Path("/tmp/test-project")
        expected_config = ProjectConfig(
            name="test-project", path="/tmp/test-project", profile="dev"
        )
        mock_project_service.get_project_config.return_value = expected_config

        # Act
        result = cli_service.get_project_info(project_path)

        # Assert
        assert result == expected_config
        mock_project_service.get_project_config.assert_called_once_with(project_path)

    def test_get_project_info_not_found(self, cli_service, mock_project_service):
        """Test getting project information when project not found."""
        # Arrange
        project_path = Path("/tmp/nonexistent-project")
        mock_project_service.get_project_config.side_effect = FileNotFoundError(
            "Project not found"
        )

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            cli_service.get_project_info(project_path)

    def test_server_status_running(self, cli_service, mock_server_service):
        """Test getting server status when running."""
        # Arrange
        mock_server_service.is_running.return_value = True

        # Act
        result = cli_service.get_server_status()

        # Assert
        assert result["status"] == "running"
        assert result["is_running"] is True

    def test_server_status_stopped(self, cli_service, mock_server_service):
        """Test getting server status when stopped."""
        # Arrange
        mock_server_service.is_running.return_value = False

        # Act
        result = cli_service.get_server_status()

        # Assert
        assert result["status"] == "stopped"
        assert result["is_running"] is False

    def test_generate_project_template_success(
        self, cli_service, mock_template_service
    ):
        """Test successful template generation."""
        # Arrange
        template_name = "react-app"
        output_path = Path("/tmp/new-react-app")
        mock_template_service.list_templates.return_value = [
            "react-app",
            "vue-app",
            "basic",
        ]

        # Act
        result = cli_service.generate_project_template(template_name, output_path)

        # Assert
        assert result is True
        mock_template_service.generate_template.assert_called_once_with(
            template_name, output_path
        )

    def test_generate_project_template_invalid_template(
        self, cli_service, mock_template_service
    ):
        """Test template generation with invalid template."""
        # Arrange
        mock_template_service.generate_template.side_effect = ValueError(
            "Invalid template"
        )
        template_name = "invalid-template"
        output_path = Path("/tmp/invalid")

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            cli_service.generate_project_template(template_name, output_path)

        assert "Invalid template" in str(exc_info.value)

    def test_list_available_templates(self, cli_service, mock_template_service):
        """Test listing available templates."""
        # Arrange
        expected_templates = ["react-app", "vue-app", "angular-app", "basic"]
        mock_template_service.list_templates.return_value = expected_templates

        # Act
        result = cli_service.list_available_templates()

        # Assert
        assert result == expected_templates
        mock_template_service.list_templates.assert_called_once()

    def test_validate_project_path_valid(self, cli_service):
        """Test project path validation with valid path."""
        # Arrange
        valid_path = Path("/tmp/valid-project")

        # Act & Assert - Should not raise any exception
        cli_service._validate_project_path(valid_path)

    def test_validate_project_path_none(self, cli_service):
        """Test project path validation with None."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            cli_service._validate_project_path(None)

        assert "Project path is required" in str(exc_info.value)

    def test_validate_project_name_valid(self, cli_service):
        """Test project name validation with valid name."""
        # Arrange
        valid_names = ["my-project", "awesome_app", "project123"]

        for name in valid_names:
            # Act & Assert - Should not raise any exception
            cli_service._validate_project_name(name)

    def test_validate_project_name_invalid(self, cli_service):
        """Test project name validation with invalid names."""
        # Arrange
        invalid_names = ["", "   ", "project with spaces", "project@special"]

        for name in invalid_names:
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                cli_service._validate_project_name(name)

            assert "Project name" in str(exc_info.value)


@pytest.mark.unit
class TestCLIApplicationServiceIntegration:
    """Integration tests for CLI application service with realistic scenarios."""

    @pytest.fixture
    def realistic_services(self):
        """Create more realistic mock services."""
        project_service = Mock(spec=IProjectService)
        server_service = Mock(spec=IServerService)
        template_service = Mock(spec=ITemplateService)

        # Configure realistic behaviors
        project_service.project_exists.return_value = False
        project_service.create_project.return_value = True
        project_service.get_project_config.return_value = ProjectConfig(
            name="test-project", path="/tmp/test-project"
        )

        server_service.is_running.return_value = False
        server_service.start_server.return_value = True
        server_service.stop_server.return_value = True

        template_service.list_templates.return_value = ["basic", "react", "vue"]
        template_service.generate_template.return_value = True

        return {
            "project": project_service,
            "server": server_service,
            "template": template_service,
        }

    def test_complete_project_workflow(self, realistic_services):
        """Test a complete project creation and server start workflow."""
        # Arrange
        cli_service = CLIApplicationService(
            project_service=realistic_services["project"],
            server_service=realistic_services["server"],
            template_service=realistic_services["template"],
        )

        project_name = "workflow-project"
        project_path = Path("/tmp/workflow-project")
        server_config = ServerConfig(host="localhost", port=8000)

        # Act
        # 1. Create project
        create_result = cli_service.create_project(project_name, project_path)

        # 2. Start server
        start_result = cli_service.start_server(server_config)

        # Update server status to running after start
        realistic_services["server"].is_running.return_value = True

        # 3. Check status
        status = cli_service.get_server_status()

        # 4. Get project info
        info = cli_service.get_project_info(project_path)

        # Assert
        assert create_result is True
        assert start_result is True
        assert status["is_running"] is True
        assert info.name == "test-project"

        # Verify service calls
        realistic_services["project"].create_project.assert_called_once()
        realistic_services["server"].start_server.assert_called_once()
        realistic_services["project"].get_project_config.assert_called_once()

    def test_error_handling_in_workflow(self, realistic_services):
        """Test error handling in a workflow scenario."""
        # Arrange
        cli_service = CLIApplicationService(
            project_service=realistic_services["project"],
            server_service=realistic_services["server"],
            template_service=realistic_services["template"],
        )

        # Configure services to simulate errors
        realistic_services[
            "project"
        ].project_exists.return_value = True  # Project exists
        realistic_services["server"].is_running.return_value = True  # Server running

        project_name = "error-project"
        project_path = Path("/tmp/error-project")
        server_config = ServerConfig(host="localhost", port=8000)

        # Act & Assert
        # 1. Try to create existing project
        with pytest.raises(ValueError) as exc_info:
            cli_service.create_project(project_name, project_path)
        assert "already exists" in str(exc_info.value)

        # 2. Try to start already running server
        with pytest.raises(RuntimeError) as exc_info:
            cli_service.start_server(server_config)
        assert "already running" in str(exc_info.value)

        # 3. Try to stop non-running server (change state first)
        realistic_services["server"].is_running.return_value = False
        with pytest.raises(RuntimeError) as exc_info:
            cli_service.stop_server()
        assert "not running" in str(exc_info.value)

    def test_template_management_workflow(self, realistic_services):
        """Test template management workflow."""
        # Arrange
        cli_service = CLIApplicationService(
            project_service=realistic_services["project"],
            server_service=realistic_services["server"],
            template_service=realistic_services["template"],
        )

        # Act
        # 1. List available templates
        templates = cli_service.list_available_templates()

        # 2. Generate template
        template_result = cli_service.generate_project_template(
            "react", Path("/tmp/react-project")
        )

        # Assert
        assert templates == ["basic", "react", "vue"]
        assert template_result is True

        realistic_services["template"].list_templates.assert_called()
        assert (
            realistic_services["template"].list_templates.call_count == 2
        )  # Called by both methods
        realistic_services["template"].generate_template.assert_called_once_with(
            "react", Path("/tmp/react-project")
        )

    @pytest.mark.skip("Python doesn't enforce interface types at runtime")
    def test_service_dependency_validation(self):
        """Test that CLI service properly validates its dependencies."""
        # Act & Assert - Should raise TypeError with invalid dependencies
        with pytest.raises(TypeError):
            CLIApplicationService(
                project_service="invalid",  # Should be IProjectService
                server_service=Mock(spec=IServerService),
                template_service=Mock(spec=ITemplateService),
            )

    def test_concurrent_operations_handling(self, realistic_services):
        """Test handling of concurrent operations."""
        # Arrange
        cli_service = CLIApplicationService(
            project_service=realistic_services["project"],
            server_service=realistic_services["server"],
            template_service=realistic_services["template"],
        )

        # Simulate server state changes
        def toggle_server_state(*args, **kwargs):
            current_state = realistic_services["server"].is_running.return_value
            realistic_services["server"].is_running.return_value = not current_state
            return True

        realistic_services["server"].start_server.side_effect = toggle_server_state
        realistic_services["server"].stop_server.side_effect = toggle_server_state

        server_config = ServerConfig(host="localhost", port=8000)

        # Act
        # Start server
        start_result = cli_service.start_server(server_config)
        status_after_start = cli_service.get_server_status()

        # Stop server
        stop_result = cli_service.stop_server()
        status_after_stop = cli_service.get_server_status()

        # Assert
        assert start_result is True
        assert status_after_start["is_running"] is True
        assert stop_result is True
        assert status_after_stop["is_running"] is False
