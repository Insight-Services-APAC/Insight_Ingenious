# Insight Ingenious Test Suite

This directory contains the test suite for the Insight Ingenious framework. Tests are organized into the following categories:

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Integration tests for component interactions
- `functional/`: Functional tests for end-to-end workflows

## Running Tests

To run the tests, use the `pytest` command:

```bash
# Install test dependencies
uv add pytest pytest-asyncio pytest-cov --dev

# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=ingenious

# Run a specific test file
uv run pytest tests/unit/common/errors/test_error_utilities.py

# Run tests matching a specific pattern
uv run pytest -k "error"
```

## Test Configuration

The test suite uses fixtures defined in `conftest.py` to provide common test setup, including:

- Sample configuration files
- Mock environments
- Temporary test directories

## Writing Tests

When writing new tests:

1. Follow the existing directory structure
2. Use appropriate pytest fixtures for setup and teardown
3. Mock external dependencies when appropriate
4. Include both positive and negative test cases
5. For asynchronous code, use the `@pytest.mark.asyncio` decorator

## Code Coverage

Aim for high test coverage, especially for critical components:

- Error handling utilities
- Configuration management
- Core services
- Repository implementations

## Integration with CI

Tests are automatically run as part of the CI pipeline. Ensure your tests pass before submitting a pull request.

## Test Data

Test data files are stored in fixtures and temporary files created during test execution. Avoid adding large data files to the repository.
