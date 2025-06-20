"""
Pytest configuration and fixtures for Insight Ingenious test suite.

This module provides shared fixtures and configuration for testing across
all bounded contexts using pytest and async testing capabilities.
"""

import asyncio
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Test data and mocks
from tests.fixtures.test_data import TestData


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_data():
    """Provide test data for use across tests."""
    return TestData()


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing."""
    return datetime(2023, 1, 1, 12, 0, 0)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp_file:
        yield Path(tmp_file.name)
    # Cleanup
    try:
        os.unlink(tmp_file.name)
    except (FileNotFoundError, OSError):
        pass


@pytest.fixture
def mock_env():
    """Mock environment variables for testing."""
    return {
        "INGENIOUS_WORKING_DIR": "/tmp/test_working_dir",
        "INGENIOUS_PROJECT_PATH": "/tmp/test_config.yml",
        "INGENIOUS_PROFILE_PATH": "/tmp/test_profiles.yml",
        "AZURE_OPENAI_API_KEY": "test_api_key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
    }


@pytest.fixture
def mock_config():
    """Mock application configuration."""
    from ingenious.configuration.domain.models import MinimalConfig

    return MinimalConfig(
        project_name="test-project", environment="test", log_level="DEBUG"
    )


# Chat Context Fixtures
@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing chat functionality."""
    mock = AsyncMock()
    mock.create_completion.return_value = {
        "text": "Mock LLM response",
        "model": "gpt-4",
        "usage": {"total_tokens": 50},
    }
    mock.generate_response.return_value = Mock(
        content="Mock response content", model="gpt-4"
    )
    mock.is_healthy.return_value = True
    return mock


@pytest.fixture
def mock_chat_service():
    """Mock chat service for testing."""
    mock = AsyncMock()
    mock.process_chat_request.return_value = Mock(
        thread_id="test-thread-123",
        agent_response="Mock chat response",
        event_type="response",
    )
    return mock


@pytest.fixture
def mock_message_repository():
    """Mock message repository."""
    return AsyncMock()


@pytest.fixture
def mock_thread_repository():
    """Mock thread repository."""
    return AsyncMock()


# CLI Context Fixtures
@pytest.fixture
def mock_project_service():
    """Mock project service for CLI testing."""
    mock = Mock()
    mock.create_project.return_value = True
    mock.get_project_config.return_value = Mock(
        name="test-project", path="/tmp/test-project", profile="dev"
    )
    return mock


@pytest.fixture
def mock_server_service():
    """Mock server service for CLI testing."""
    mock = Mock()
    mock.start_server.return_value = True
    mock.stop_server.return_value = True
    mock.is_running.return_value = False
    return mock


@pytest.fixture
def mock_template_service():
    """Mock template service for CLI testing."""
    mock = Mock()
    mock.generate_template.return_value = True
    return mock


# Configuration Context Fixtures
@pytest.fixture
def mock_configuration_repository():
    """Mock configuration repository."""
    mock = AsyncMock()
    mock.get_configuration.return_value = {
        "application": {"name": "test-app"},
        "server": {"host": "localhost", "port": 8000},
    }
    mock.save_configuration.return_value = True
    return mock


@pytest.fixture
def mock_secret_service():
    """Mock secret service."""
    mock = AsyncMock()
    mock.get_secret.return_value = "mock_secret_value"
    mock.set_secret.return_value = True
    return mock


# Diagnostics Context Fixtures
@pytest.fixture
def mock_diagnostic_service():
    """Mock diagnostic service."""
    mock = AsyncMock()
    mock.run_health_check.return_value = Mock(
        status="healthy", checks=[], overall_status="healthy"
    )
    return mock


@pytest.fixture
def mock_system_metrics_service():
    """Mock system metrics service."""
    mock = AsyncMock()
    mock.get_system_metrics.return_value = {
        "cpu_usage": 25.5,
        "memory_usage": 60.0,
        "disk_usage": 45.0,
    }
    return mock


# External Integrations Context Fixtures
@pytest.fixture
def mock_content_moderation_service():
    """Mock content moderation service."""
    mock = AsyncMock()
    mock.moderate_content.return_value = {
        "flagged": False,
        "categories": {},
        "category_scores": {},
    }
    return mock


# File Management Context Fixtures
@pytest.fixture
def mock_file_service():
    """Mock file service."""
    mock = AsyncMock()
    mock.upload_file.return_value = Mock(file_id="test-file-123")
    mock.download_file.return_value = b"test file content"
    mock.delete_file.return_value = True
    return mock


# Security Context Fixtures
@pytest.fixture
def mock_auth_service():
    """Mock authentication service."""
    mock = AsyncMock()
    mock.authenticate.return_value = Mock(
        user_id="test-user-123", username="testuser", is_authenticated=True
    )
    mock.is_authorized.return_value = True
    return mock


@pytest.fixture
def mock_user_repository():
    """Mock user repository."""
    mock = AsyncMock()
    mock.get_user.return_value = Mock(
        user_id="test-user-123", username="testuser", email="test@example.com"
    )
    mock.create_user.return_value = Mock(user_id="new-user-123")
    return mock


# API Testing Fixtures
@pytest.fixture
async def async_client():
    """Async HTTP client for API testing."""
    from ingenious.configuration.domain.models import MinimalConfig
    from ingenious.main import FastAgentAPI

    # Create test app with minimal config
    config = MinimalConfig()
    app_instance = FastAgentAPI(config)

    async with AsyncClient(app=app_instance.app, base_url="http://test") as client:
        yield client


@pytest.fixture
def test_client():
    """Synchronous test client for FastAPI testing."""
    from ingenious.configuration.domain.models import MinimalConfig
    from ingenious.main import FastAgentAPI

    config = MinimalConfig()
    app_instance = FastAgentAPI(config)

    with TestClient(app_instance.app) as client:
        yield client


# Database and Repository Fixtures
@pytest.fixture
def in_memory_database():
    """In-memory database for testing."""
    return {}


@pytest.fixture
def mock_container():
    """Mock dependency injection container."""
    container = Mock()
    container.get_service.return_value = Mock()
    container.register_service.return_value = None
    return container


# Integration Test Fixtures
@pytest.fixture
def integration_test_env(mock_env, temp_dir):
    """Set up environment for integration tests."""
    # Set up test environment variables
    for key, value in mock_env.items():
        os.environ[key] = value

    # Create test directories and files
    test_config_dir = temp_dir / "config"
    test_config_dir.mkdir(exist_ok=True)

    config_file = test_config_dir / "config.yml"
    config_file.write_text("""
application:
  name: test-project
  environment: test
server:
  host: 127.0.0.1
  port: 8000
""")

    profiles_file = test_config_dir / "profiles.yml"
    profiles_file.write_text("""
- name: test
  models:
    - model: gpt-4
      api_key: test_key
      base_url: https://test.openai.azure.com
""")

    os.environ["INGENIOUS_PROJECT_PATH"] = str(config_file)
    os.environ["INGENIOUS_PROFILE_PATH"] = str(profiles_file)
    os.environ["INGENIOUS_WORKING_DIR"] = str(temp_dir)

    yield {
        "config_dir": test_config_dir,
        "config_file": config_file,
        "profiles_file": profiles_file,
        "working_dir": temp_dir,
    }

    # Cleanup environment
    for key in mock_env.keys():
        if key in os.environ:
            del os.environ[key]


# Error and Exception Testing Fixtures
@pytest.fixture
def mock_error_service():
    """Mock service that raises errors for testing error handling."""
    mock = AsyncMock()
    mock.failing_method.side_effect = Exception("Test error")
    return mock


# Performance Testing Fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None

    return Timer()
