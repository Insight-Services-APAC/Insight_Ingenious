# Installation Guide

This guide provides detailed instructions for installing and setting up Insight Ingenious.

## Prerequisites

Before installing Insight Ingenious, ensure you have the following prerequisites:

- Python 3.13 or higher (as specified in pyproject.toml)
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Git (for cloning the repository)
- [pre-commit](https://pre-commit.com/) (for development, code linting, and formatting)

## Installation Methods

### Method 1: Using uv (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. **Install uv** if you don't have it already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Create a virtual environment and install the package**:
   ```bash
   uv venv
   uv pip install -e .
   ```

4. **Initialize a new project**:
   ```bash
   ingen init
   ```

5. **Verify installation**:
   ```bash
   ingen run-test-batch
   ```

   This command will run the test suite to verify that everything is working correctly.

### Method 2: Using pip

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**:
   ```bash
   pip install -e .
   ```

4. **(Recommended for development) Install pre-commit hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Initialize a new project**:
   ```bash
   ingen init
   ```

## Docker Installation

For containerized deployment, you can use Docker:

1. **Build the Docker image**:
   ```bash
   docker build -t insight-ingenious -f utils/docker/production_images/Dockerfile .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 -v ./config.yml:/app/config.yml -v ~/.ingenious:/root/.ingenious insight-ingenious
   ```

## Configuration

After installing Insight Ingenious, you'll need to configure it:

### 1. Project Configuration

The framework uses a `config.yml` file for its main configuration. When you run `ingen_cli init`, a template configuration file is created in your current directory.

### 2. Profile Configuration

Profiles are used to store sensitive information such as API keys. By default, the profile configuration is stored at `~/.ingenious/profiles.yml`.

A typical profile configuration looks like:

```yaml
profiles:
  - name: default
    openai:
      api_key: your_openai_api_key
      organization: your_organization_id
    azure_openai:
      api_key: your_azure_openai_key
      api_base: your_azure_openai_endpoint
```

### 3. Environment Variables

You can also configure Insight Ingenious using environment variables:

- `INGENIOUS_PROJECT_PATH`: Path to your project's configuration file
- `INGENIOUS_PROFILE_PATH`: Path to your profiles configuration file
- `INGENIOUS_WORKING_DIR`: Working directory for the application
- `KEY_VAULT_NAME`: (Optional) Azure Key Vault name for secret management

## Development Installation

For developers who want to contribute to the project:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. **Install with development dependencies**:
   ```bash
   uv venv
   uv pip install -e .
   uv pip install -e ".[dev]"  # Install development dependencies
   ```

3. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Initialize a new project**:
   ```bash
   ingen init
   ```

## Troubleshooting

### Common Issues

1. **Missing dependencies**:
   If you encounter errors about missing dependencies, try running:
   ```bash
   uv pip install -e .
   ```

2. **Configuration issues**:
   Ensure that your configuration files are correctly set up and that the environment variables point to the right locations.

3. **Python version issues**:
   Verify that you're using Python 3.13 or higher:
   ```bash
   python --version
   ```

### Getting Help

If you encounter issues during installation:

1. Check the documentation in the `docs/` directory
2. Look for examples in the `ingenious_extensions_template` directory
3. Refer to the code comments in the relevant modules
4. Create an issue on GitHub and label it `question`
