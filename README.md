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

5. Set environment variables (copy from the output above):
    ```bash
    export INGENIOUS_PROJECT_PATH="$(pwd)/config.yml"
    export INGENIOUS_PROFILE_PATH="$(pwd)/profiles.yml"
    ```

6. **IMPORTANT**: Edit `profiles.yml` and add your Azure OpenAI API key:
    ```yaml
    - name: dev
      models:
        - model: gpt-4o
          api_key: "YOUR_ACTUAL_API_KEY_HERE"  # ← Replace this!
          base_url: "https://YOUR_RESOURCE_NAME.openai.azure.com/..."  # ← And this!
    ```

7. Start the server:
    ```bash
    uv run ingen run-project
    ```

8. Open your browser and go to: http://localhost:8000/chainlit

9. **Try your first chat**: "Hello! Can you help me learn about bicycles?"

📖 **For detailed setup instructions, see the generated `SETUP.md` file in your project directory.**

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
- [Optional Dependencies](docs/optional_dependencies/README.md)
  - [Dataprep Crawler](docs/optional_dependencies/dataprep/README.md) – Scrapfly-powered scraping CLI

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.
