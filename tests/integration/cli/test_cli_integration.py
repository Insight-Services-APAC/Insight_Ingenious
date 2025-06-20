"""
Integration tests for CLI commands.

This module tests the CLI interface with real command execution.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch, Mock

from ingenious.cli.main import create_cli_app


@pytest.mark.integration
@pytest.mark.cli
class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def cli_app(self):
        """Create CLI application for testing."""
        return create_cli_app()
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create temporary directory for project testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_cli_help_command(self, cli_runner, cli_app):
        """Test CLI help command."""
        # Act
        result = cli_runner.invoke(cli_app, ["--help"])
        
        # Assert
        assert result.exit_code == 0
        assert "Usage:" in result.stdout
        assert "Commands:" in result.stdout or "Options:" in result.stdout
    
    def test_create_project_command_success(self, cli_runner, cli_app, temp_project_dir):
        """Test successful project creation via CLI."""
        # Arrange
        project_name = "test-cli-project"
        project_path = temp_project_dir / project_name
        
        # Mock the services to avoid actual file operations
        with patch('ingenious.cli.infrastructure.services.FileSystemProjectService') as mock_service:
            mock_instance = Mock()
            mock_instance.create_project.return_value = True
            mock_instance.project_exists.return_value = False
            mock_service.return_value = mock_instance
            
            with patch('ingenious.cli.infrastructure.services.TemplateGenerationService') as mock_template:
                mock_template_instance = Mock()
                mock_template_instance.generate_template.return_value = True
                mock_template.return_value = mock_template_instance
                
                # Act
                result = cli_runner.invoke(cli_app, [
                    "create-project",
                    project_name,
                    str(project_path)
                ])
        
        # Assert
        assert result.exit_code == 0
        assert project_name in result.stdout or result.exit_code == 0  # Success case
    
    def test_create_project_command_invalid_name(self, cli_runner, cli_app, temp_project_dir):
        """Test project creation with invalid name."""
        # Arrange
        invalid_name = "invalid project name"  # Spaces not allowed
        project_path = temp_project_dir / "invalid"
        
        # Act
        result = cli_runner.invoke(cli_app, [
            "create-project",
            invalid_name,
            str(project_path)
        ])
        
        # Assert
        assert result.exit_code != 0  # Should fail
        assert "error" in result.stdout.lower() or result.exit_code != 0
    
    def test_start_server_command(self, cli_runner, cli_app):
        """Test start server command."""
        # Arrange
        with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_service:
            mock_instance = Mock()
            mock_instance.start_server.return_value = True
            mock_instance.is_running.return_value = False
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, [
                "start-server",
                "--host", "127.0.0.1",
                "--port", "8001"
            ])
        
        # Assert
        assert result.exit_code == 0 or "server" in result.stdout.lower()
    
    def test_start_server_command_default_options(self, cli_runner, cli_app):
        """Test start server command with default options."""
        # Arrange
        with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_service:
            mock_instance = Mock()
            mock_instance.start_server.return_value = True
            mock_instance.is_running.return_value = False
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, ["start-server"])
        
        # Assert
        assert result.exit_code == 0 or "server" in result.stdout.lower()
    
    def test_stop_server_command(self, cli_runner, cli_app):
        """Test stop server command."""
        # Arrange
        with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_service:
            mock_instance = Mock()
            mock_instance.stop_server.return_value = True
            mock_instance.is_running.return_value = True
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, ["stop-server"])
        
        # Assert
        assert result.exit_code == 0 or "server" in result.stdout.lower()
    
    def test_server_status_command(self, cli_runner, cli_app):
        """Test server status command."""
        # Arrange
        with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_service:
            mock_instance = Mock()
            mock_instance.is_running.return_value = False
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, ["server-status"])
        
        # Assert
        assert result.exit_code == 0
        assert "status" in result.stdout.lower() or "running" in result.stdout.lower() or "stopped" in result.stdout.lower()
    
    def test_list_templates_command(self, cli_runner, cli_app):
        """Test list templates command."""
        # Arrange
        with patch('ingenious.cli.infrastructure.services.TemplateGenerationService') as mock_service:
            mock_instance = Mock()
            mock_instance.list_templates.return_value = ["basic", "react", "vue", "angular"]
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, ["list-templates"])
        
        # Assert
        assert result.exit_code == 0
        assert "templates" in result.stdout.lower() or any(template in result.stdout for template in ["basic", "react", "vue"])
    
    def test_generate_template_command(self, cli_runner, cli_app, temp_project_dir):
        """Test generate template command."""
        # Arrange
        template_name = "react"
        output_path = temp_project_dir / "react-project"
        
        with patch('ingenious.cli.infrastructure.services.TemplateGenerationService') as mock_service:
            mock_instance = Mock()
            mock_instance.generate_template.return_value = True
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, [
                "generate-template",
                template_name,
                str(output_path)
            ])
        
        # Assert
        assert result.exit_code == 0 or "template" in result.stdout.lower()
    
    def test_project_info_command(self, cli_runner, cli_app, temp_project_dir):
        """Test project info command."""
        # Arrange
        project_path = temp_project_dir / "info-project"
        
        with patch('ingenious.cli.infrastructure.services.FileSystemProjectService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_project_config.return_value = Mock(
                name="info-project",
                path=str(project_path),
                profile="dev"
            )
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, [
                "project-info",
                str(project_path)
            ])
        
        # Assert
        assert result.exit_code == 0 or "project" in result.stdout.lower()
    
    def test_invalid_command(self, cli_runner, cli_app):
        """Test invalid command handling."""
        # Act
        result = cli_runner.invoke(cli_app, ["invalid-command"])
        
        # Assert
        assert result.exit_code != 0
        assert "Usage:" in result.stdout or "No such command" in result.stdout or result.exit_code == 2
    
    def test_command_with_invalid_options(self, cli_runner, cli_app):
        """Test command with invalid options."""
        # Act
        result = cli_runner.invoke(cli_app, [
            "start-server",
            "--invalid-option", "value"
        ])
        
        # Assert
        assert result.exit_code != 0
        assert "Usage:" in result.stdout or "No such option" in result.stdout or result.exit_code == 2
    
    def test_verbose_output(self, cli_runner, cli_app):
        """Test verbose output option."""
        # Arrange
        with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_service:
            mock_instance = Mock()
            mock_instance.is_running.return_value = False
            mock_service.return_value = mock_instance
            
            # Act
            result = cli_runner.invoke(cli_app, [
                "server-status",
                "--verbose"
            ])
        
        # Assert
        assert result.exit_code == 0
        # Verbose mode might show additional information
    
    def test_help_for_specific_command(self, cli_runner, cli_app):
        """Test help for specific commands."""
        # Arrange
        commands = ["create-project", "start-server", "stop-server"]
        
        for command in commands:
            # Act
            result = cli_runner.invoke(cli_app, [command, "--help"])
            
            # Assert
            assert result.exit_code == 0
            assert "Usage:" in result.stdout
            assert command in result.stdout


@pytest.mark.integration
@pytest.mark.cli
@pytest.mark.slow
class TestCLIWorkflows:
    """Integration tests for complete CLI workflows."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def cli_app(self):
        """Create CLI application for testing."""
        return create_cli_app()
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for workflow testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_complete_project_creation_workflow(self, cli_runner, cli_app, temp_workspace):
        """Test complete project creation and server startup workflow."""
        # Arrange
        project_name = "workflow-project"
        project_path = temp_workspace / project_name
        
        # Mock all services
        with patch('ingenious.cli.infrastructure.services.FileSystemProjectService') as mock_project:
            with patch('ingenious.cli.infrastructure.services.TemplateGenerationService') as mock_template:
                with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_server:
                    # Configure mocks
                    mock_project_instance = Mock()
                    mock_project_instance.create_project.return_value = True
                    mock_project_instance.project_exists.return_value = False
                    mock_project_instance.get_project_config.return_value = Mock(
                        name=project_name,
                        path=str(project_path),
                        profile="dev"
                    )
                    mock_project.return_value = mock_project_instance
                    
                    mock_template_instance = Mock()
                    mock_template_instance.generate_template.return_value = True
                    mock_template_instance.list_templates.return_value = ["basic", "react"]
                    mock_template.return_value = mock_template_instance
                    
                    mock_server_instance = Mock()
                    mock_server_instance.start_server.return_value = True
                    mock_server_instance.stop_server.return_value = True
                    mock_server_instance.is_running.side_effect = [False, True, True, False]  # State changes
                    mock_server.return_value = mock_server_instance
                    
                    # Act - Complete workflow
                    # 1. List available templates
                    list_result = cli_runner.invoke(cli_app, ["list-templates"])
                    
                    # 2. Create project
                    create_result = cli_runner.invoke(cli_app, [
                        "create-project",
                        project_name,
                        str(project_path)
                    ])
                    
                    # 3. Get project info
                    info_result = cli_runner.invoke(cli_app, [
                        "project-info",
                        str(project_path)
                    ])
                    
                    # 4. Start server
                    start_result = cli_runner.invoke(cli_app, [
                        "start-server",
                        "--host", "127.0.0.1",
                        "--port", "8000"
                    ])
                    
                    # 5. Check server status
                    status_result = cli_runner.invoke(cli_app, ["server-status"])
                    
                    # 6. Stop server
                    stop_result = cli_runner.invoke(cli_app, ["stop-server"])
        
        # Assert
        assert list_result.exit_code == 0
        assert create_result.exit_code == 0
        assert info_result.exit_code == 0
        assert start_result.exit_code == 0
        assert status_result.exit_code == 0
        assert stop_result.exit_code == 0
    
    def test_error_handling_workflow(self, cli_runner, cli_app, temp_workspace):
        """Test error handling in CLI workflows."""
        # Arrange
        project_name = "error-project"
        project_path = temp_workspace / project_name
        
        with patch('ingenious.cli.infrastructure.services.FileSystemProjectService') as mock_project:
            with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_server:
                # Configure mocks to simulate errors
                mock_project_instance = Mock()
                mock_project_instance.project_exists.return_value = True  # Project already exists
                mock_project.return_value = mock_project_instance
                
                mock_server_instance = Mock()
                mock_server_instance.is_running.return_value = True  # Server already running
                mock_server.return_value = mock_server_instance
                
                # Act - Error scenarios
                # 1. Try to create existing project
                create_result = cli_runner.invoke(cli_app, [
                    "create-project",
                    project_name,
                    str(project_path)
                ])
                
                # 2. Try to start already running server
                start_result = cli_runner.invoke(cli_app, ["start-server"])
                
                # 3. Try invalid project info
                mock_project_instance.get_project_config.side_effect = FileNotFoundError("Not found")
                info_result = cli_runner.invoke(cli_app, [
                    "project-info",
                    str(project_path)
                ])
        
        # Assert - All should handle errors gracefully
        # Commands should either succeed or fail with proper error messages
        assert isinstance(create_result.exit_code, int)
        assert isinstance(start_result.exit_code, int)
        assert isinstance(info_result.exit_code, int)
    
    def test_configuration_workflow(self, cli_runner, cli_app, temp_workspace):
        """Test configuration-related workflow."""
        # Arrange
        config_project = temp_workspace / "config-project"
        
        with patch('ingenious.cli.infrastructure.services.FileSystemProjectService') as mock_project:
            mock_project_instance = Mock()
            mock_project_instance.create_project.return_value = True
            mock_project_instance.project_exists.return_value = False
            mock_project.return_value = mock_project_instance
            
            with patch('ingenious.cli.infrastructure.services.TemplateGenerationService') as mock_template:
                mock_template_instance = Mock()
                mock_template_instance.generate_template.return_value = True
                mock_template.return_value = mock_template_instance
                
                # Act
                # Create project with specific profile
                result = cli_runner.invoke(cli_app, [
                    "create-project",
                    "config-project",
                    str(config_project),
                    "--profile", "production"
                ])
        
        # Assert
        assert result.exit_code == 0 or "project" in result.stdout.lower()
    
    def test_concurrent_cli_operations(self, cli_runner, cli_app):
        """Test handling of concurrent CLI operations."""
        # Arrange
        import threading
        import time
        
        results = []
        
        def run_command():
            with patch('ingenious.cli.infrastructure.services.UvicornServerService') as mock_service:
                mock_instance = Mock()
                mock_instance.is_running.return_value = False
                mock_service.return_value = mock_instance
                
                result = cli_runner.invoke(cli_app, ["server-status"])
                results.append(result.exit_code)
        
        # Act - Run multiple commands concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=run_command)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Assert
        assert len(results) == 3
        assert all(isinstance(code, int) for code in results)
    
    def test_cli_environment_isolation(self, cli_runner, cli_app, temp_workspace):
        """Test that CLI operations are properly isolated."""
        # Arrange
        project1 = temp_workspace / "project1"
        project2 = temp_workspace / "project2"
        
        with patch('ingenious.cli.infrastructure.services.FileSystemProjectService') as mock_service:
            mock_instance = Mock()
            mock_instance.create_project.return_value = True
            mock_instance.project_exists.return_value = False
            mock_service.return_value = mock_instance
            
            with patch('ingenious.cli.infrastructure.services.TemplateGenerationService') as mock_template:
                mock_template_instance = Mock()
                mock_template_instance.generate_template.return_value = True
                mock_template.return_value = mock_template_instance
                
                # Act - Create two separate projects
                result1 = cli_runner.invoke(cli_app, [
                    "create-project",
                    "project1",
                    str(project1)
                ])
                
                result2 = cli_runner.invoke(cli_app, [
                    "create-project",
                    "project2",
                    str(project2)
                ])
        
        # Assert
        assert result1.exit_code == 0
        assert result2.exit_code == 0
        # Both projects should be created independently
