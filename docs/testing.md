# Testing Framework

This document describes the testing framework and best practices for the Insight Ingenious project.

## Test Structure

The Insight Ingenious test suite is organized into three main categories:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test interactions between components
3. **Functional Tests**: Test end-to-end workflows

All tests are located in the `tests/` directory, which follows this structure:

```
tests/
├── conftest.py          # Common test fixtures
├── README.md           # Test documentation
├── functional/         # Functional tests
│   └── test_cli.py     # CLI functional tests
├── integration/        # Integration tests
│   └── test_chat_service.py  # Chat service integration tests
└── unit/               # Unit tests
    ├── __init__.py
    ├── application/    # Tests for application layer
    ├── common/         # Tests for common utilities
    ├── domain/         # Tests for domain models
    ├── extensions/     # Tests for extensions
    └── presentation/   # Tests for presentation layer
```

## Test Environment

### Dependencies

The testing framework requires the following dependencies:

- pytest
- pytest-asyncio
- pytest-cov
- pytest-mock
- pytest-timeout

These can be installed using uv:

```bash
uv add pytest pytest-asyncio pytest-cov pytest-mock pytest-timeout --dev
```

### Configuration

The test configuration is defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "functional: Functional tests",
    "slow: Slow running tests",
]
```

## Running Tests

### Running All Tests

To run all tests in the project:

```bash
uv run pytest
```

### Running with Coverage

To run tests with coverage reporting:

```bash
uv run pytest --cov=ingenious
```

For a detailed HTML coverage report:

```bash
uv run pytest --cov=ingenious --cov-report=html
```

### Running Specific Tests

To run a specific test file:

```bash
uv run pytest tests/unit/common/errors/test_error_utilities.py
```

To run tests matching a specific pattern:

```bash
uv run pytest -k "error"
```

### Running Tests by Category

To run tests with a specific marker:

```bash
uv run pytest -m "unit"
uv run pytest -m "integration"
uv run pytest -m "functional"
```

## Writing Tests

### Test Fixtures

Common test fixtures are defined in `conftest.py` and are available to all tests. These include:

- Sample configuration files
- Mock environments
- Temporary test directories

Example fixture:

```python
# conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_config():
    return {
        "api_key": "test_key",
        "profile": "default",
        "log_level": "INFO"
    }

@pytest.fixture
def temp_test_dir(tmp_path):
    return tmp_path
```

### Unit Tests

Unit tests should test individual components in isolation, using mocks for dependencies.

Example unit test:

```python
# tests/unit/common/errors/test_error_utilities.py
import pytest
from ingenious.common.errors import ValidationError, handle_exception

def test_validation_error():
    # Arrange
    fields = {"username": "Must be at least 3 characters"}

    # Act
    error = ValidationError("Invalid input", fields=fields)

    # Assert
    assert error.message == "Invalid input"
    assert error.fields == fields

    # Test conversion to dict
    error_dict = error.to_dict()
    assert error_dict["message"] == "Invalid input"
    assert error_dict["fields"] == fields

def test_handle_exception():
    # Arrange
    exception = ValueError("Test error")

    # Act
    result = handle_exception(exception)

    # Assert
    assert result["error"]["message"] == "Test error"
    assert result["error"]["type"] == "ValueError"
```

### Integration Tests

Integration tests should test interactions between components.

Example integration test:

```python
# tests/integration/test_chat_service.py
import pytest
from ingenious.services.chat_service import ChatService
from ingenious.models.chat import ChatRequest
from ingenious.db.chat_history_repository import ChatHistoryRepository

@pytest.mark.asyncio
@pytest.mark.integration
async def test_chat_service_integration(mock_config, mock_chat_repository):
    # Arrange
    chat_service = ChatService(mock_config, mock_chat_repository, "default")
    request = ChatRequest(
        conversation_id="test-conversation",
        message="Hello, world!",
        conversation_flow="default"
    )

    # Act
    response = await chat_service.get_chat_response(request)

    # Assert
    assert response.conversation_id == "test-conversation"
    assert response.response != ""
    assert response.message_id is not None
```

### Functional Tests

Functional tests should test end-to-end workflows.

Example functional test:

```python
# tests/functional/test_cli.py
import pytest
import subprocess
from pathlib import Path

@pytest.mark.functional
def test_cli_initialization(temp_test_dir):
    # Arrange
    os.chdir(temp_test_dir)

    # Act
    result = subprocess.run(
        ["ingen_cli", "init"],
        capture_output=True,
        text=True
    )

    # Assert
    assert result.returncode == 0
    assert Path(temp_test_dir / "config.yml").exists()
    assert "Folder generation process completed" in result.stdout
```

### Asynchronous Tests

For testing asynchronous code, use the `pytest.mark.asyncio` decorator:

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    # Test an asynchronous function
    result = await my_async_function()
    assert result == expected_value
```

### Mock Objects

Use pytest-mock to create mock objects:

```python
def test_with_mocks(mocker):
    # Create a mock
    mock_service = mocker.MagicMock()
    mock_service.get_data.return_value = {"key": "value"}

    # Use the mock
    result = function_under_test(mock_service)

    # Assert
    assert result == expected_value
    mock_service.get_data.assert_called_once()
```

## Testing Best Practices

1. **Test Coverage**: Aim for high test coverage, especially for critical components like error handling utilities, configuration management, core services, and repository implementations.

2. **Arrange-Act-Assert**: Structure tests using the Arrange-Act-Assert pattern:
   - Arrange: Set up the test data and environment
   - Act: Call the function or method being tested
   - Assert: Verify the expected outcomes

3. **Isolation**: Ensure that tests are isolated from each other and do not depend on external resources like databases or API services without proper mocking.

4. **Descriptive Names**: Use descriptive test names that indicate what is being tested and what the expected outcome is.

5. **Test Edge Cases**: Include tests for edge cases, boundary conditions, and error scenarios.

6. **Clean Up**: Clean up any resources created during tests, especially in integration and functional tests.

7. **Test Data**: Keep test data separate from production data. Use fixtures and factories to create test data.

8. **CI Integration**: Ensure tests are part of the CI pipeline and run before merging code.

## Code Coverage

To check code coverage:

```bash
uv run pytest --cov=ingenious
```

For a detailed HTML report:

```bash
uv run pytest --cov=ingenious --cov-report=html
```

The coverage report will show which parts of the code are covered by tests and which are not.

## Continuous Integration

Tests are automatically run as part of the CI pipeline. Ensure your tests pass before submitting a pull request.

The CI pipeline configuration should include:

1. Running all tests
2. Checking code coverage
3. Running code quality checks

## Test Data

Test data files are stored in fixtures and temporary files created during test execution. Avoid adding large data files to the repository.

For sample data that is needed across multiple tests, use the `sample_data` directory in your extension.
