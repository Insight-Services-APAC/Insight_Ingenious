# Insight Ingenious

A powerful framework for building, managing, and deploying multi-agent AI conversations.

## Overview
Insight Ingenious lets you orchestrate multiple AI agents and deploy them as an API for seamless integration into your applications.

## Quickstart

1. Clone the repository:
    ```bash
    git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
    cd Insight_Ingenious
    ```

2. Install [uv](https://docs.astral.sh/uv/) for Python package and environment management (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

3. Set up the project and install dependencies:
    ```bash
    uv sync
    uv run pre-commit install
    uv pip install -e .
    ```

4. Initialize a new project:
    ```bash
    uv run ingen initialize-new-project
    ```

5. Run pre-commit hooks on all files:
    ```bash
    uv run pre-commit run --all-files
    ```

## Project Structure

- `ingenious/`: Core framework code
  - `api/`: API endpoints and routes
  - `chainlit/`: Web UI components
  - `config/`: Configuration management
  - `db/`: Database integration
  - `files/`: File storage utilities
  - `models/`: Data models and schemas
  - `services/`: Core services including chat and agent services
  - `templates/`: Prompt templates and HTML templates
  - `utils/`: Utility functions

- `ingenious_extensions_template/`: Template for custom extensions
  - `api/`: Custom API routes
  - `models/`: Custom data models
  - `sample_data/`: Sample data for testing
  - `services/`: Custom agent services
  - `templates/`: Custom prompt templates
  - `tests/`: Test harness for agent prompts

- `ingenious_prompt_tuner/`: Tool for tuning and testing prompts

## Documentation

For detailed documentation, see the [docs/](docs/) directory:

- [Architecture Overview](docs/architecture/README.md)
- [Configuration Guide](docs/configuration/README.md)
- [Usage Examples](docs/usage/README.md)
- [Development Guide](docs/development/README.md)
- [Components Reference](docs/components/README.md)
- **Optional Dependencies**
  &nbsp;&nbsp;&nbsp;• [Optional Dependencies Index](docs/optional_dependencies/README.md)
  &nbsp;&nbsp;&nbsp;• [Dataprep Crawler](docs/optional_dependencies/dataprep/README.md) – Scrapfly-powered scraping CLI

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
