# Insight Ingenious

A powerful framework for building, managing, and deploying multi-agent AI conversations with modern Python.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Key Features

- **Multi-Agent Orchestration**: Create and manage conversations between multiple AI agents
- **Extensible Architecture**: Easily extend with custom agents, templates, and APIs
- **Database Integration**: Store conversations in SQLite or Azure Cosmos DB
- **Modern Package Management**: Built with [uv](https://docs.astral.sh/uv/) for fast dependency management
- **Web Interfaces**: Access via REST API, ChainLit UI, or Prompt Tuner
- **Comprehensive Documentation**: Detailed guides and references

## Quickstart

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. **Install dependencies** with uv:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh   # If you don't have uv installed
   uv venv
   uv pip install -e .
   ```

3. **Initialize a new project**:
   ```bash
   ingen init
   ```

4. **Configure API keys** in `~/.ingenious/profiles.yml`:
   ```yaml
   profiles:
     - name: default
       openai:
         api_key: your_openai_api_key
   ```

5. **Start the API server**:
   ```bash
   ingen run-rest-api-server --host 127.0.0.1 --port 8000
   ```

6. **Access the interfaces**:
   - REST API: http://127.0.0.1:8000/api/v1
   - ChainLit UI: http://127.0.0.1:8000/chainlit
   - Prompt Tuner: http://127.0.0.1:8000/prompt-tuner

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- [Architecture Overview](docs/architecture.md)
- [Installation Guide](docs/installation.md)
- [Quickstart Guide](docs/quickstart.md)
- [API Documentation](docs/api.md)
- [Configuration Guide](docs/configuration.md)
- [Working with Agents](docs/agents.md)
- [Extension System](docs/extensions.md)
- [Testing Framework](docs/testing.md)
- [CLI Reference](docs/cli.md)

## Core Components

- **FastAgentAPI**: The main application class that initializes the system
- **Agent System**: Define and orchestrate conversations between AI agents
- **Chat Services**: Handle different types of agent conversations
- **Storage Layer**: Persist conversations and files
- **Extension System**: Customize and extend functionality

## Contributing

Contributions to Insight Ingenious are welcome! Please refer to the [CONTRIBUTING.md](./CONTRIBUTING.md) file for detailed contribution guidelines including code standards, pull request process, and development setup.

## License

<<<<<<< HEAD
9. **CLI Test Harness**:
   ```bash
   python ingenious_extensions/tests/run_ingen_cli.py
   ```

## Getting Started (For New Projects)

To set up a new project:

1. Run `ingen_cli initialize-new-project` to create the necessary folder structure
2. Configure your application in `config.yml` and profiles in `~/.ingenious/profiles.yml`
3. Develop your extensions in the `ingenious_extensions` directory
4. Run your application with `ingen_cli run-rest-api-server`

The framework includes templates and examples to help you get started quickly with your own AI applications.
=======
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
>>>>>>> origin/main
