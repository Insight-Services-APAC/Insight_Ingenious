# Installation Guide

This guide covers installation of the Ingenious framework using `uv`, the recommended package manager for this project.

## Prerequisites

- Python 3.13 or higher
- [uv package manager](https://github.com/astral-sh/uv) (recommended)

## Installation Methods

### Using uv (Recommended)

For new projects using Ingenious:

```bash
# Create a new project
uv init my-ingenious-project
cd my-ingenious-project

# Add Ingenious as a dependency
uv add insight-ingenious

# Initialize Ingenious project structure
uv run ingen init
```

### Using pip (Alternative)

If you prefer using pip:

```bash
pip install insight-ingenious
```

### Development Installation

If you're contributing to the framework or need the latest development version:

```bash
# Clone the repository
git clone https://github.com/your-org/insight-ingenious.git
cd insight-ingenious

# Install dependencies with uv
uv sync

# Install in development mode (optional)
uv pip install -e .
```

## Verify Installation

After installation, verify that Ingenious is correctly installed:

```bash
# Check CLI availability
uv run ingen --help

# Check Python import
uv run python -c "import ingenious; print(f'Ingenious {ingenious.__version__} installed successfully')"

# Alternative with pip installation
ingen --help
python -c "import ingenious; print(f'Ingenious {ingenious.__version__} installed successfully')"
```

## Optional Dependencies

Ingenious has several optional dependency groups for specific use cases:

### Development Dependencies

For contributors and developers:

```bash
pip install insight-ingenious[dev]
```

Includes:
- pre-commit hooks
- ruff linter
- setuptools

### Testing Dependencies

For running tests:

```bash
pip install insight-ingenious[test]
```

Includes:
- pytest and pytest plugins
- httpx for HTTP testing
- freezegun for time mocking

## Azure Services Setup

Ingenious integrates with Azure services. You'll need:

### Azure OpenAI

1. Create an Azure OpenAI resource in the Azure portal
2. Deploy a model (e.g., GPT-4)
3. Note your endpoint URL and API key

### Azure Blob Storage (Optional)

1. Create a Storage Account in Azure
2. Create a container for your data
3. Note your account URL and access credentials

### Azure SQL Database (Optional)

1. Create an Azure SQL Database
2. Configure firewall rules
3. Note connection string details

## Configuration

After installation, you can configure Ingenious through:

1. Environment variables
2. Configuration files
3. Python API

See the [Configuration Guide](configuration.md) for detailed setup instructions.

## Next Steps

- Follow the [Getting Started Guide](getting-started.md) for your first Ingenious application
- Explore [Examples](examples/) for practical use cases
- Read about [Prompt Ensembles](prompt-ensembles.md) to understand the core concepts

## Troubleshooting

### Common Installation Issues

**Python Version Error**
```
ERROR: Python 3.13 or higher is required
```
Update your Python installation to 3.13+.

**Import Error**
```
ImportError: No module named 'ingenious'
```
Ensure you're using the correct Python environment and that the package was installed successfully.

**CLI Not Found**
```
ingen: command not found
```
Ensure your Python scripts directory is in your PATH, or use `python -m ingenious.cli` instead.

For more troubleshooting help, see the [Troubleshooting Guide](troubleshooting.md).
