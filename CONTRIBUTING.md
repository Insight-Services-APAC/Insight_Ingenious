# Contributing to Insight Ingenious

Thank you for your interest in contributing to Insight Ingenious! This document provides comprehensive guidelines for contributing to our GenAI accelerator platform.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Architecture](#project-architecture)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)
- [Issue Guidelines](#issue-guidelines)

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.13+** installed
- **uv** package manager ([installation guide](https://github.com/astral-sh/uv))
- **Git** for version control
- Basic understanding of **Domain-Driven Design (DDD)** principles
- Familiarity with **FastAPI** and **Typer**

### Initial Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Install pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

5. **Verify the setup**:
   ```bash
   uv run pytest --asyncio-mode=auto --tb=short -q
   uv run ruff check
   ```

## Development Environment

### Package Management

This project uses **uv** for dependency management. Key commands:

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add package-name --dev

# Remove a dependency
uv remove package-name

# Sync environment with lockfile
uv sync

# Run commands in the environment
uv run command
```

### Environment Configuration

Create a local `.env` file for development:

```bash
INGENIOUS_WORKING_DIR="$(pwd)"
INGENIOUS_PROJECT_PATH="$(pwd)/config.yml"
INGENIOUS_PROFILE_PATH="$(pwd)/profiles.yml"
AZURE_OPENAI_API_KEY="your-development-key"
AZURE_OPENAI_ENDPOINT="your-development-endpoint"
```

### Running the Application

```bash
# Initialize a test project
uv run ingen init

# Start the development server
uv run ingen dev

# Run with custom options
uv run ingen run --host 0.0.0.0 --port 8080
```

## Project Architecture

### Domain-Driven Design Structure

The project follows DDD principles with clear bounded contexts:

```
ingenious/
├── chat/                    # Chat and conversation management
├── cli/                     # Command-line interface
├── configuration/           # System configuration
├── core/                    # Core infrastructure
├── diagnostics/            # Health monitoring
├── external_integrations/   # Third-party services
├── file_management/        # File operations
├── prompt_management/      # Prompt templates
├── security/               # Authentication & authorization
└── shared/                 # Cross-cutting concerns
```

### Layer Architecture

Each bounded context follows clean architecture:

```
bounded_context/
├── domain/              # Pure business logic
│   ├── entities.py      # Core business entities
│   ├── services.py      # Domain service interfaces
│   ├── models.py        # Domain models
│   └── value_objects.py # Value objects
├── application/         # Application layer
│   ├── services.py      # Application services
│   └── use_cases.py     # Specific use cases
├── infrastructure/      # External implementations
│   ├── repositories.py  # Data access implementations
│   └── services.py      # External service implementations
└── interfaces/          # Interface adapters
    ├── rest_controllers.py # REST API endpoints
    └── cli_controllers.py  # CLI command handlers
```

### Dependency Flow

- **Interfaces** → **Application** → **Domain** ← **Infrastructure**
- Dependencies point inward toward the domain
- Infrastructure depends on domain abstractions
- Domain layer has no external dependencies

## Code Standards

### Python Style Guide

We follow **PEP 8** with additional project-specific conventions:

#### General Conventions

- **Line length**: Maximum 88 characters (Black's default)
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Type hints**: Required for all public functions and methods
- **Docstrings**: Use Google-style docstrings for all public APIs

#### Naming Conventions

```python
# Classes: PascalCase
class UserService:
    pass

# Functions and variables: snake_case
def create_user_account():
    user_name = "example"

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Private members: leading underscore
def _internal_method():
    pass
```

#### Domain-Specific Conventions

```python
# Domain entities: Clear business names
class ConversationThread:
    pass

# Use cases: Descriptive action names
class CreateNewProjectUseCase:
    pass

# Services: Interface prefix for abstractions
class IUserRepository(ABC):
    pass

class DatabaseUserRepository(IUserRepository):
    pass
```

### Code Organization

#### File Structure

```python
"""
Module docstring describing the bounded context and layer.

This module contains [description of contents].
"""

# Standard library imports
import os
from typing import Any, Optional

# Third-party imports
from fastapi import APIRouter
from pydantic import BaseModel

# Local imports
from ..domain.entities import User
from ..application.services import UserService

# Constants
DEFAULT_PAGE_SIZE = 20

# Implementation
class UserController:
    """Controller for user management operations."""

    def __init__(self, user_service: UserService):
        """Initialize the controller with required services."""
        self._user_service = user_service
```

#### Error Handling

```python
# Domain-specific exceptions
class UserNotFoundError(Exception):
    """Raised when a requested user cannot be found."""
    pass

# Use structured error handling
try:
    user = await self._user_service.get_user(user_id)
except UserNotFoundError as e:
    logger.warning(f"User not found: {user_id}")
    raise HTTPException(status_code=404, detail="User not found")
```

### Dependencies and Imports

#### Dependency Injection

```python
# Use constructor injection
class UserApplicationService:
    def __init__(
        self,
        user_repository: IUserRepository,
        email_service: IEmailService,
    ):
        self._user_repository = user_repository
        self._email_service = email_service
```

#### Import Organization

```python
# 1. Standard library
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

# 2. Third-party libraries
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# 3. Local application imports
from ..domain.entities import User
from ..application.services import UserService
from ...shared.exceptions import ValidationError
```

## Testing

### Testing Strategy

We follow a comprehensive testing approach:

- **Unit Tests**: Domain logic and individual components
- **Integration Tests**: Service interactions and database operations
- **API Tests**: HTTP endpoint functionality
- **CLI Tests**: Command-line interface behavior

### Test Structure

```
tests/
├── unit/                # Fast, isolated tests
│   ├── domain/         # Domain logic tests
│   ├── application/    # Application service tests
│   └── infrastructure/ # Infrastructure tests
├── integration/        # Cross-component tests
│   ├── api/           # API integration tests
│   └── cli/           # CLI integration tests
└── fixtures/          # Shared test data and utilities
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from unittest.mock import Mock, AsyncMock

from ingenious.chat.domain.entities import ConversationThread
from ingenious.chat.application.services import ChatApplicationService


class TestChatApplicationService:
    """Test suite for ChatApplicationService."""

    @pytest.fixture
    def mock_chat_repository(self):
        """Mock chat repository for testing."""
        return AsyncMock()

    @pytest.fixture
    def chat_service(self, mock_chat_repository):
        """Create ChatApplicationService with mocked dependencies."""
        return ChatApplicationService(chat_repository=mock_chat_repository)

    async def test_create_conversation_success(self, chat_service, mock_chat_repository):
        """Test successful conversation creation."""
        # Arrange
        user_id = "user-123"
        expected_thread = ConversationThread(id="thread-456", user_id=user_id)
        mock_chat_repository.create_conversation.return_value = expected_thread

        # Act
        result = await chat_service.create_conversation(user_id)

        # Assert
        assert result.id == "thread-456"
        assert result.user_id == user_id
        mock_chat_repository.create_conversation.assert_called_once_with(user_id)
```

#### Integration Test Example

```python
import pytest
from httpx import AsyncClient

from ingenious.main import app


class TestChatAPI:
    """Integration tests for Chat API endpoints."""

    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

    async def test_chat_endpoint_success(self, client):
        """Test successful chat request."""
        # Arrange
        chat_request = {
            "message": "Hello, how are you?",
            "conversation_flow": "general",
            "thread_id": "test-thread"
        }

        # Act
        response = await client.post("/api/v1/chat", json=chat_request)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "thread_id" in data
```

### Running Tests

```bash
# Run all tests (recommended default)
uv run pytest --asyncio-mode=auto --tb=short -q

# Run all tests with verbose output
uv run pytest --asyncio-mode=auto --tb=short -v

# Run specific test categories
uv run pytest tests/unit/ --asyncio-mode=auto --tb=short
uv run pytest tests/integration/ --asyncio-mode=auto --tb=short

# Run with coverage
uv run pytest --asyncio-mode=auto --tb=short --cov=ingenious --cov-report=html

# Run tests for specific bounded context
uv run pytest tests/unit/chat/ --asyncio-mode=auto --tb=short

# Run tests matching a pattern
uv run pytest -k "test_chat" --asyncio-mode=auto --tb=short
```

### Test Guidelines

1. **Test Naming**: Use descriptive names that explain the scenario
2. **AAA Pattern**: Arrange, Act, Assert structure
3. **Mock External Dependencies**: Isolate units under test
4. **Test Edge Cases**: Include boundary conditions and error scenarios
5. **Keep Tests Fast**: Unit tests should complete in milliseconds
6. **Maintain Test Data**: Use fixtures for reusable test setup

## Submitting Changes

### Branch Naming

Use descriptive branch names following these patterns:

```bash
# Feature branches
feature/add-user-authentication
feature/improve-chat-response-time

# Bug fixes
bugfix/fix-file-upload-validation
bugfix/resolve-configuration-loading

# Refactoring
refactor/modernize-dependency-injection
refactor/simplify-error-handling

# Documentation
docs/update-api-documentation
docs/add-deployment-guide
```

### Commit Messages

Follow conventional commit format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(chat): add message feedback functionality

Implement user feedback collection for chat messages including
thumbs up/down ratings and optional text comments.

Closes #123

fix(cli): resolve configuration file loading issue

The CLI was failing to load configuration files when run from
different directories. This fix ensures relative paths are
resolved correctly.

Fixes #456

docs(api): update REST API documentation

Add comprehensive examples for all chat endpoints and improve
error response documentation.
```

### Pull Request Process

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**: Implement your feature following code standards

3. **Write Tests**: Ensure adequate test coverage

4. **Run Quality Checks**:
   ```bash
   uv run pytest
   uv run ruff check
   uv run ruff format
   uv run pre-commit run --all-files
   ```

5. **Update Documentation**: Add or update relevant documentation

6. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat(scope): descriptive message"
   ```

7. **Push Branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create Pull Request**: Open a PR with a clear description

### Pull Request Template

```markdown
## Description
Brief description of the changes and their purpose.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Test coverage maintained or improved

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] No new warnings introduced

## Related Issues
Closes #(issue number)
```

## Review Process

### Code Review Guidelines

**For Authors:**
- Ensure all checks pass before requesting review
- Provide clear PR description and context
- Respond promptly to review feedback
- Keep changes focused and atomic

**For Reviewers:**
- Review code for correctness, readability, and maintainability
- Check adherence to architecture and DDD principles
- Verify test coverage and quality
- Provide constructive, actionable feedback
- Approve when satisfied with quality

### Review Criteria

1. **Functionality**: Does the code work as intended?
2. **Architecture**: Does it follow DDD principles and layer separation?
3. **Code Quality**: Is it readable, maintainable, and well-structured?
4. **Testing**: Are there adequate tests with good coverage?
5. **Documentation**: Is the code and API properly documented?
6. **Performance**: Are there any performance concerns?
7. **Security**: Are there any security implications?

## Issue Guidelines

### Reporting Bugs

Use the bug report template:

```markdown
## Bug Description
Clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., macOS 14.0]
- Python version: [e.g., 3.13.0]
- Package version: [e.g., 0.1.0]

## Additional Context
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
## Feature Description
Clear and concise description of the feature.

## Problem Statement
What problem would this feature solve?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered.

## Additional Context
Any other context or mockups.
```

### Issue Labels

- `bug`: Something isn't working
- `feature`: New feature request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `enhancement`: Improvement to existing feature
- `question`: Further information requested

## Development Tips

### Domain-Driven Design Guidelines

1. **Keep Domain Pure**: Domain layer should have no external dependencies
2. **Use Ubiquitous Language**: Business terms should be consistent across code and documentation
3. **Respect Bounded Context Boundaries**: Avoid direct dependencies between contexts
4. **Model Business Concepts**: Entities and value objects should represent real business concepts
5. **Implement Business Rules in Domain**: Business logic belongs in the domain layer

### Performance Considerations

- Use async/await for I/O operations
- Implement proper caching strategies
- Consider database query optimization
- Monitor memory usage in long-running processes
- Use connection pooling for external services

### Security Best Practices

- Validate all inputs at API boundaries
- Use environment variables for secrets
- Implement proper authentication and authorization
- Follow OWASP security guidelines
- Regularly update dependencies

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussions
- **Pull Requests**: Code review and technical discussions

### Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please read and follow our Code of Conduct.

### Getting Help

1. **Check Documentation**: Review README and inline documentation
2. **Search Issues**: Look for existing discussions
3. **Ask Questions**: Open a GitHub Discussion for help
4. **Join Community**: Participate in project discussions

Thank you for contributing to Insight Ingenious! Your contributions help make this project better for everyone.
