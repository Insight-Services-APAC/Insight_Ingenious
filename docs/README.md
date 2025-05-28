# Insight Ingenious Documentation

Welcome to the Insight Ingenious documentation. This guide provides comprehensive information about setting up, configuring, and using the Insight Ingenious framework for building, managing, and deploying multi-agent AI conversations.

## Documentation Sections

- [Architecture](./architecture.md) - Understand the system architecture and components
- [Installation](./installation.md) - Detailed installation instructions
- [Quickstart](./quickstart.md) - Get up and running quickly
- [API Documentation](./api.md) - REST API reference
- [Configuration](./configuration.md) - Configuration options and settings
- [Agents](./agents.md) - Working with AI agents
- [Extensions](./extensions.md) - Extending the framework
- [Error Handling](./error_handling.md) - Error handling system
- [Testing](./testing.md) - Testing framework and best practices
- [Code Quality](./code_quality.md) - Code quality tools and standards
- [CLI](./cli.md) - Command line interface reference

## About Insight Ingenious

Insight Ingenious is a powerful framework designed to build, manage, and deploy multi-agent AI conversations. It provides:

- **Multi-agent orchestration**: Create and manage conversations between multiple AI agents
- **Extensibility**: Add custom agents, templates, and APIs
- **Database and file storage integration**: Store conversations and files
- **Multiple interfaces**: Access via CLI, REST API, or web UI

The framework is built on modern Python technologies including FastAPI, Pydantic, and integrations with AI platforms.

## Key Features

- **Flexible Agent System**: Define and customize AI agents with different roles and capabilities
- **Multi-modal Conversations**: Support for text, images, and other content types
- **Extensible Architecture**: Easy to extend with custom components
- **Database Integration**: Store conversation history in SQLite, DuckDB, or Azure Cosmos DB
- **Package Management with uv**: Modern Python package and environment management
- **Web Interface**: Built-in web interface using ChainLit
- **Prompt Tuner**: Dedicated interface for tuning prompts

## Getting Help

If you need assistance with Insight Ingenious, you can:

1. Check the relevant documentation section
2. Look for examples in the `ingenious_extensions_template` directory
3. Refer to the code comments in the relevant modules
4. Create an issue and label it `question`

## Contributing

Contributions to Insight Ingenious are welcome! Please refer to the [CONTRIBUTING.md](../CONTRIBUTING.md) file for detailed contribution guidelines.

### Development Standards

- This project uses [pre-commit](https://pre-commit.com/) to enforce code quality and formatting standards.
- After cloning the repository, run:
  ```bash
  pre-commit install
  ```
- To manually check all files, run:
  ```bash
  pre-commit run --all-files
  ```
- Please ensure all pre-commit hooks pass before submitting a pull request.
