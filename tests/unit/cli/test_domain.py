"""
Unit tests for CLI domain entities and value objects.

This module tests the core business entities in the CLI bounded context.
"""

import pytest
from pydantic import ValidationError

from ingenious.cli.domain.entities import CLICommand, ProjectConfig, ServerConfig
from ingenious.cli.domain.value_objects import HostAddress, Port, ProjectName


class TestProjectConfig:
    """Test suite for ProjectConfig entity."""

    def test_project_config_creation_minimal(self):
        """Test creating ProjectConfig with minimal required fields."""
        # Act
        config = ProjectConfig(name="test-project", path="/tmp/test-project")

        # Assert
        assert config.name == "test-project"
        assert config.path == "/tmp/test-project"
        assert config.profile == "dev"  # Default value

    def test_project_config_creation_full(self):
        """Test creating ProjectConfig with all fields."""
        # Act
        config = ProjectConfig(
            name="my-awesome-project",
            path="/home/user/projects/awesome",
            profile="production",
        )

        # Assert
        assert config.name == "my-awesome-project"
        assert config.path == "/home/user/projects/awesome"
        assert config.profile == "production"

    def test_project_config_string_representation(self):
        """Test string representation of ProjectConfig."""
        # Arrange
        config = ProjectConfig(name="test-project", path="/tmp/test-project")

        # Act
        str_repr = str(config)

        # Assert
        assert "test-project" in str_repr
        assert "/tmp/test-project" in str_repr

    def test_project_config_validation_empty_name(self):
        """Test validation fails with empty name."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(name="", path="/tmp/test")

        assert "name" in str(exc_info.value)

    def test_project_config_validation_empty_path(self):
        """Test validation fails with empty path."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ProjectConfig(name="test", path="")

        assert "path" in str(exc_info.value)

    def test_project_config_serialization(self):
        """Test ProjectConfig serialization."""
        # Arrange
        config = ProjectConfig(
            name="test-project", path="/tmp/test-project", profile="staging"
        )

        # Act
        data = config.model_dump()

        # Assert
        assert data["name"] == "test-project"
        assert data["path"] == "/tmp/test-project"
        assert data["profile"] == "staging"

    def test_project_config_deserialization(self):
        """Test ProjectConfig deserialization."""
        # Arrange
        data = {"name": "restored-project", "path": "/tmp/restored", "profile": "dev"}

        # Act
        config = ProjectConfig(**data)

        # Assert
        assert config.name == "restored-project"
        assert config.path == "/tmp/restored"
        assert config.profile == "dev"


class TestServerConfig:
    """Test suite for ServerConfig entity."""

    def test_server_config_creation_defaults(self):
        """Test creating ServerConfig with default values."""
        # Act
        config = ServerConfig()

        # Assert
        assert config.host == "127.0.0.1"
        assert config.port == 8000
        assert config.project_dir is None
        assert config.profile_dir is None

    def test_server_config_creation_custom(self):
        """Test creating ServerConfig with custom values."""
        # Act
        config = ServerConfig(
            host="0.0.0.0",
            port=9000,
            project_dir="/app/project",
            profile_dir="/app/profiles",
        )

        # Assert
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.project_dir == "/app/project"
        assert config.profile_dir == "/app/profiles"

    def test_server_config_string_representation(self):
        """Test string representation of ServerConfig."""
        # Arrange
        config = ServerConfig(host="localhost", port=3000)

        # Act
        str_repr = str(config)

        # Assert
        assert "localhost:3000" in str_repr

    def test_server_config_port_validation_valid_range(self):
        """Test port validation with valid port numbers."""
        # Valid ports
        valid_ports = [1, 80, 443, 8000, 65535]

        for port in valid_ports:
            # Act
            config = ServerConfig(port=port)

            # Assert
            assert config.port == port

    def test_server_config_port_validation_invalid_low(self):
        """Test port validation fails with port too low."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(port=0)

        assert "port" in str(exc_info.value)

    def test_server_config_port_validation_invalid_high(self):
        """Test port validation fails with port too high."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ServerConfig(port=65536)

        assert "port" in str(exc_info.value)

    def test_server_config_host_variations(self):
        """Test ServerConfig with various host formats."""
        # Arrange
        hosts = ["127.0.0.1", "localhost", "0.0.0.0", "myserver.com", "192.168.1.100"]

        for host in hosts:
            # Act
            config = ServerConfig(host=host)

            # Assert
            assert config.host == host


class TestCLICommand:
    """Test suite for CLICommand entity."""

    def test_cli_command_creation_minimal(self):
        """Test creating CLICommand with minimal data."""
        # Act
        command = CLICommand(command_name="init")

        # Assert
        assert command.command_name == "init"
        assert command.arguments == {}
        assert command.options == {}

    def test_cli_command_creation_full(self):
        """Test creating CLICommand with full data."""
        # Act
        command = CLICommand(
            command_name="create-project",
            arguments={"name": "my-project", "template": "basic"},
            options={"verbose": True, "force": False},
        )

        # Assert
        assert command.command_name == "create-project"
        assert command.arguments == {"name": "my-project", "template": "basic"}
        assert command.options == {"verbose": True, "force": False}

    def test_cli_command_string_representation(self):
        """Test string representation of CLICommand."""
        # Arrange
        command = CLICommand(command_name="test-command")

        # Act
        str_repr = str(command)

        # Assert
        assert "test-command" in str_repr

    def test_cli_command_validation_empty_name(self):
        """Test validation fails with empty command name."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            CLICommand(command_name="")

        assert "command_name" in str(exc_info.value)

    def test_cli_command_complex_arguments(self):
        """Test CLICommand with complex arguments."""
        # Act
        command = CLICommand(
            command_name="deploy",
            arguments={
                "environment": "staging",
                "config_files": ["app.yml", "secrets.yml"],
                "replicas": 3,
                "metadata": {"version": "1.2.3", "author": "dev-team"},
            },
        )

        # Assert
        assert command.arguments["environment"] == "staging"
        assert command.arguments["config_files"] == ["app.yml", "secrets.yml"]
        assert command.arguments["replicas"] == 3
        assert command.arguments["metadata"]["version"] == "1.2.3"


class TestHostAddress:
    """Test suite for HostAddress value object."""

    def test_host_address_creation_ipv4(self):
        """Test creating HostAddress with IPv4 address."""
        # Act
        host = HostAddress(value="192.168.1.1")

        # Assert
        assert str(host) == "192.168.1.1"

    def test_host_address_creation_hostname(self):
        """Test creating HostAddress with hostname."""
        # Act
        host = HostAddress(value="localhost")

        # Assert
        assert str(host) == "localhost"

    def test_host_address_creation_fqdn(self):
        """Test creating HostAddress with FQDN."""
        # Act
        host = HostAddress(value="api.example.com")

        # Assert
        assert str(host) == "api.example.com"

    def test_host_address_validation_empty(self):
        """Test HostAddress validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            HostAddress(value="")

        assert "empty" in str(exc_info.value).lower()

    def test_host_address_equality(self):
        """Test HostAddress equality comparison."""
        # Arrange
        host1 = HostAddress(value="127.0.0.1")
        host2 = HostAddress(value="127.0.0.1")
        host3 = HostAddress(value="localhost")

        # Act & Assert
        assert host1 == host2
        assert host1 != host3


class TestPort:
    """Test suite for Port value object."""

    def test_port_creation_valid(self):
        """Test creating Port with valid port numbers."""
        # Arrange
        valid_ports = [1, 80, 443, 8000, 65535]

        for port_num in valid_ports:
            # Act
            port = Port(value=port_num)

            # Assert
            assert port.value == port_num
            assert str(port) == str(port_num)

    def test_port_validation_too_low(self):
        """Test Port validation with port number too low."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Port(value=0)

        assert "range" in str(exc_info.value).lower()

    def test_port_validation_too_high(self):
        """Test Port validation with port number too high."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            Port(value=65536)

        assert "range" in str(exc_info.value).lower()

    def test_port_equality(self):
        """Test Port equality comparison."""
        # Arrange
        port1 = Port(value=8000)
        port2 = Port(value=8000)
        port3 = Port(value=9000)

        # Act & Assert
        assert port1 == port2
        assert port1 != port3

    def test_port_common_values(self):
        """Test Port with common port values."""
        # Arrange
        common_ports = [22, 25, 53, 80, 110, 143, 443, 993, 995]

        for port_num in common_ports:
            # Act
            port = Port(value=port_num)

            # Assert
            assert port.value == port_num


class TestProjectName:
    """Test suite for ProjectName value object."""

    def test_project_name_creation_valid(self):
        """Test creating ProjectName with valid names."""
        # Arrange
        valid_names = [
            "my-project",
            "awesome_app",
            "project123",
            "MyProject",
            "web-api-v2",
        ]

        for name in valid_names:
            # Act
            project_name = ProjectName(value=name)

            # Assert
            assert str(project_name) == name

    def test_project_name_validation_empty(self):
        """Test ProjectName validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            ProjectName(value="")

        assert "empty" in str(exc_info.value).lower()

    def test_project_name_validation_whitespace_only(self):
        """Test ProjectName validation with whitespace-only string."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            ProjectName(value="   ")

        assert "empty" in str(exc_info.value).lower()

    def test_project_name_validation_invalid_characters(self):
        """Test ProjectName validation with invalid characters."""
        # Arrange
        invalid_names = [
            "project with spaces",
            "project@special",
            "project#hash",
            "project$dollar",
        ]

        for name in invalid_names:
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                ProjectName(value=name)

            assert "characters" in str(exc_info.value).lower()

    def test_project_name_equality(self):
        """Test ProjectName equality comparison."""
        # Arrange
        name1 = ProjectName(value="my-project")
        name2 = ProjectName(value="my-project")
        name3 = ProjectName(value="other-project")

        # Act & Assert
        assert name1 == name2
        assert name1 != name3

    def test_project_name_case_sensitivity(self):
        """Test ProjectName case sensitivity."""
        # Arrange
        name1 = ProjectName(value="MyProject")
        name2 = ProjectName(value="myproject")

        # Act & Assert
        assert name1 != name2  # Should be case-sensitive


@pytest.mark.unit
class TestCLIDomainIntegration:
    """Integration tests for CLI domain entities and value objects."""

    def test_project_config_with_value_objects(self):
        """Test ProjectConfig using value objects."""
        # Arrange
        project_name = ProjectName(value="awesome-project")

        # Act
        config = ProjectConfig(
            name=str(project_name), path="/tmp/awesome-project", profile="production"
        )

        # Assert
        assert config.name == "awesome-project"
        assert config.path == "/tmp/awesome-project"
        assert config.profile == "production"

    def test_server_config_with_value_objects(self):
        """Test ServerConfig using value objects."""
        # Arrange
        host = HostAddress("api.example.com")
        port = Port(value=8080)

        # Act
        config = ServerConfig(
            host=str(host), port=port.value, project_dir="/app/project"
        )

        # Assert
        assert config.host == "api.example.com"
        assert config.port == 8080
        assert config.project_dir == "/app/project"

    def test_complete_cli_command_scenario(self):
        """Test a complete CLI command scenario."""
        # Arrange
        project_name = ProjectName(value="new-web-app")
        host = HostAddress("localhost")
        port = Port(value=3000)

        # Act
        # Create project command
        create_command = CLICommand(
            command_name="create-project",
            arguments={"name": str(project_name), "template": "react"},
            options={"verbose": True},
        )

        # Server start command
        server_command = CLICommand(
            command_name="start-server",
            arguments={"host": str(host), "port": port.value},
            options={"dev": True, "hot-reload": True},
        )

        # Assert
        assert create_command.command_name == "create-project"
        assert create_command.arguments["name"] == "new-web-app"
        assert create_command.options["verbose"] is True

        assert server_command.command_name == "start-server"
        assert server_command.arguments["host"] == "localhost"
        assert server_command.arguments["port"] == 3000
        assert server_command.options["dev"] is True

    def test_configuration_objects_serialization(self):
        """Test serialization of configuration objects."""
        # Arrange
        project_config = ProjectConfig(
            name="serializable-project", path="/tmp/serializable", profile="test"
        )

        server_config = ServerConfig(
            host="127.0.0.1", port=8000, project_dir="/tmp/serializable"
        )

        # Act
        project_data = project_config.model_dump()
        server_data = server_config.model_dump()

        # Restore from serialized data
        restored_project = ProjectConfig(**project_data)
        restored_server = ServerConfig(**server_data)

        # Assert
        assert restored_project.name == project_config.name
        assert restored_project.path == project_config.path
        assert restored_project.profile == project_config.profile

        assert restored_server.host == server_config.host
        assert restored_server.port == server_config.port
        assert restored_server.project_dir == server_config.project_dir
