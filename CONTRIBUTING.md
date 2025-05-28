# Contributing to Insight Ingenious

Thank you for your interest in contributing to Insight Ingenious! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style and Standards](#code-style-and-standards)
- [Branching Strategy](#branching-strategy)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Documentation](#documentation)
- [Extension Development](#extension-development)
- [License](#license)
- [Getting Help](#getting-help)

## Code of Conduct

We want everyone to feel welcome here! Please:

- Use friendly, inclusive language
- Respect different opinions and experiences
- Take feedback in stride and keep it positive
- Focus on making the community better for everyone
- Be kind and considerate to others

Let’s work together to keep things respectful and supportive.

## Prerequisites

Before contributing, ensure you have:

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Git
- [pre-commit](https://pre-commit.com/)

## Getting Started

1. Fork the repository on GitHub
2. Clone your forked repository:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Insight_Ingenious.git
   cd Insight_Ingenious
   ```
3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   ```
4. Install the project dependencies:
   ```bash
   uv venv
   uv pip install -e .
   uv pip install -e ".[dev]"  # Install development dependencies
   ```
5. Initialize the project:
   ```bash
   ingen initialize-new-project
   ```

## Development Environment

### Setting up pre-commit

We use pre-commit hooks to enforce code quality and formatting standards:

```bash
uv run pre-commit install
```

Run all pre-commit hooks manually:

```bash
uv run pre-commit run --all-files
```

### Configuration

Create configuration files:

1. Project configuration (`config.yml`) - Created during initialization
2. Profiles configuration:
   ```bash
   mkdir -p ~/.ingenious
   touch ~/.ingenious/profiles.yml
   ```

## Code Style and Standards

We adhere to the following coding standards:

- Use consistent naming conventions
- Follow Python PEP 8 style guidelines
- Write comprehensive docstrings for public APIs
- Include type hints where appropriate

The pre-commit hooks will automatically check and fix many formatting issues.

## Branching Strategy

- `main` - Contains the stable, released code
- `develop` - Integration branch for new features
- Feature branches - Named `feature/description` for new features
- Bugfix branches - Named `bugfix/issue-number` for bug fixes

Always create new branches from `develop`.

## Pull Request Process

1. Update your fork with the latest changes from the upstream repository
   ```bash
   git fetch upstream
   git checkout develop
   git merge upstream/develop
   ```

2. Create a feature branch from `develop`
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Make your changes and commit them
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

4. Ensure pre-commit hooks pass
   ```bash
   pre-commit run --all-files
   ```

5. Push your changes to your fork
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request to the `develop` branch of the main repository

7. Wait for code review and address any feedback

## Testing

When adding new features, include appropriate tests. See [Testing Documentation](./docs/testing.md) for more details.

## Code Quality

### Finding Dead Code with Vulture

We use [Vulture](https://github.com/jendrikseipp/vulture) to identify unused code in our codebase. This helps maintain a cleaner, more maintainable project.

1. Install Vulture:
   ```bash
   uv add vulture --dev
   ```

2. Run Vulture on the project:
   ```bash
   uv run vulture ingenious/ --min-confidence 80
   ```

3. To exclude specific files or directories:
   ```bash
   uv run vulture ingenious/ --exclude "*/tests/*,*/migrations/*" --min-confidence 80
   ```

4. Create whitelists for false positives:
   ```bash
   uv run vulture ingenious/ --make-whitelist > whitelist.py
   uv run vulture ingenious/ whitelist.py
   ```

For detailed usage and configuration options, refer to the [Code Quality Documentation](./docs/code_quality.md).

## Documentation

For any new feature or change:

1. Update relevant documentation in the `docs/` directory
2. Add inline code comments for complex logic
3. Update README.md if necessary

Documentation should be clear, concise, and follow Markdown best practices.

## Extension Development

When developing extensions for Insight Ingenious:

1. Follow the extension structure outlined in the [Extensions documentation](./docs/extensions.md)
2. Maintain compatibility with the core framework
3. Use consistent naming patterns for your extension components
4. Include tests for your extension functionality
5. Add a README for your extension
6. Minimize dependencies
7. Implement proper error handling
8. Version your extensions appropriately

## License

By contributing to Insight Ingenious, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

## Getting Help

If you need assistance:

1. Check the documentation in the `docs/` directory
2. Look for examples in the `ingenious_extensions_template` directory
3. Refer to the code comments in the relevant modules
4. Create an issue and label it `question`

Thank you for contributing to Insight Ingenious!
