# Code Quality

This document outlines the code quality standards, tools, and best practices for the Insight Ingenious project.

## Code Style and Standards

Insight Ingenious follows Python's PEP 8 style guide along with additional project-specific standards:

1. **Consistency**: Use consistent naming conventions, formatting, and patterns throughout the codebase.
2. **Documentation**: Include docstrings for all public modules, classes, and functions.
3. **Type Hints**: Use type hints for function and method signatures.
4. **Error Handling**: Implement proper error handling with specific exception types.
5. **Testability**: Write code that is easily testable, with clear separation of concerns.

## Pre-commit Hooks

The project uses [pre-commit](https://pre-commit.com/) hooks to enforce code quality and formatting standards automatically. These hooks run before each commit to ensure code quality.

### Setting Up Pre-commit

```bash
# Install pre-commit
uv add pre-commit --dev

# Install the pre-commit hooks
pre-commit install
```

### Running Pre-commit Manually

```bash
# Run pre-commit on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run black --all-files
```

### Pre-commit Configuration

The pre-commit configuration is defined in `.pre-commit-config.yaml` and includes hooks for:

- Trailing whitespace
- End-of-file fixes
- Code formatting (black, ruff)
- Import sorting
- Type checking

## Code Linting with Ruff

Insight Ingenious uses [Ruff](https://beta.ruff.rs/docs/) for fast Python linting. Ruff can identify and fix many common code issues.

### Configuration

Ruff is configured in `pyproject.toml`:

```toml
[tool.ruff.lint]
extend-select = ["I"]
ignore = ["E402"]
```

### Running Ruff

```bash
# Check code with Ruff
uv run ruff check ingenious/

# Fix issues automatically
uv run ruff check --fix ingenious/
```

## Finding Dead Code with Vulture

[Vulture](https://github.com/jendrikseipp/vulture) is used to identify unused code in the codebase, helping to maintain a cleaner, more maintainable project.

### Installation

```bash
uv add vulture --dev
```

### Usage

```bash
# Run Vulture on the project
vulture ingenious/ --min-confidence 80

# Exclude specific files or directories
vulture ingenious/ --exclude "*/tests/*,*/migrations/*" --min-confidence 80

# Create whitelists for false positives
vulture ingenious/ --make-whitelist > whitelist.py
vulture ingenious/ whitelist.py
```

## Type Checking

Type hints are used throughout the codebase and can be checked with mypy.

### Installation

```bash
uv add mypy --dev
```

### Usage

```bash
# Run mypy on the project
mypy ingenious/
```

## Code Complexity

To keep code maintainable, complex functions and methods should be split into smaller, more focused ones. Consider using tools like [complexity](https://complexity.readthedocs.io/) to measure cyclomatic complexity.

```bash
uv add complexity --dev
complexity --max-complexity 10 ingenious/
```

## Testing Coverage

Code coverage is an important aspect of code quality. The project uses pytest-cov to measure test coverage.

```bash
# Run tests with coverage
uv run pytest --cov=ingenious

# Generate HTML coverage report
uv run pytest --cov=ingenious --cov-report=html
```

Aim for high test coverage, especially for critical components.

## Code Review Guidelines

When reviewing code, consider the following aspects:

1. **Functionality**: Does the code correctly implement the intended functionality?
2. **Maintainability**: Is the code easy to understand and maintain?
3. **Performance**: Are there any performance issues or potential bottlenecks?
4. **Error Handling**: Are errors properly handled and reported?
5. **Documentation**: Is the code properly documented?
6. **Testing**: Are there appropriate tests for the code?
7. **Security**: Are there any security vulnerabilities?
8. **Compatibility**: Does the code maintain compatibility with the rest of the codebase?

## Documentation Standards

### Docstrings

Use Google-style docstrings for Python code:

```python
def function_name(arg1, arg2):
    """Short description of the function.

    Longer description that explains the function in more detail.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ExceptionType: When and why this exception is raised
    """
    # Function implementation
```

### README and Documentation Files

- Use Markdown for documentation files
- Include a table of contents for longer documents
- Use headings to organize content
- Include examples where appropriate
- Keep documentation up-to-date with code changes

## Dependency Management

The project uses [uv](https://docs.astral.sh/uv/) for dependency management and environment isolation.

### Adding Dependencies

```bash
# Add a runtime dependency
uv add package-name

# Add a development dependency
uv add package-name --dev
```

### Updating Dependencies

```bash
# Update all dependencies
uv pip freeze --all | xargs -n1 uv add -y

# Update a specific dependency
uv add package-name -U
```

## Continuous Integration

Continuous Integration (CI) runs all code quality checks and tests automatically on each pull request.

The CI pipeline includes:

1. Running pre-commit hooks
2. Linting with Ruff
3. Running tests with pytest
4. Checking code coverage
5. Building documentation

## Security Best Practices

1. **Input Validation**: Validate all user inputs to prevent injection attacks.
2. **Authentication and Authorization**: Implement proper authentication and authorization checks.
3. **Secrets Management**: Use environment variables or secure storage for secrets, never hardcode them.
4. **Content Security**: Filter and validate user-generated content.

## Performance Considerations

1. **Profiling**: Use profiling tools to identify bottlenecks.
2. **Asynchronous Code**: Use asynchronous programming appropriately for I/O-bound operations.
3. **Database Optimization**: Optimize database queries and use indexing where appropriate.
4. **Caching**: Implement caching for expensive operations.

## Conclusion

Maintaining high code quality is essential for the long-term success of the Insight Ingenious project. By following these standards and using the provided tools, contributors can ensure that the codebase remains clean, maintainable, and robust.
