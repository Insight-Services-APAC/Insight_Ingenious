# Ingenious Framework Documentation

Welcome to the Ingenious Framework documentation. Ingenious is a production-ready Python library for building AI-powered applications with prompt ensemble orchestration and Azure service integration.

## Quick Navigation

- [Installation Guide](installation.md) - Get started with installing and setting up Ingenious
- [Getting Started](getting-started.md) - Your first steps with the framework
- [API Reference](api-reference.md) - Complete API documentation
- [CLI Usage](cli-usage.md) - Command-line interface guide
- [Configuration](configuration.md) - Framework configuration options
- [Prompt Ensembles](prompt-ensembles.md) - Core ensemble functionality
- [Azure Integration](azure-integration.md) - Working with Azure services
- [Examples](examples/) - Practical examples and tutorials
- [Best Practices](best-practices.md) - Recommended patterns and practices
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## What is Insight Ingenious?

Insight Ingenious is a Domain-Driven Design (DDD) based framework that enables developers to create sophisticated AI applications using prompt ensemble patterns and comprehensive service integration. It provides:

- **AI Agent Integration**: Built-in support for Azure OpenAI and other LLM services
- **Chat Management**: Advanced conversation handling with message feedback and thread management
- **File Management**: Comprehensive file operations including upload, download, and directory management
- **Configuration Management**: Flexible configuration system with secret management
- **Security**: Authentication, authorization, and user management
- **Prompt Ensemble Orchestration**: Decompose complex prompts, process in parallel/sequential patterns, and aggregate results
- **Production-Ready Architecture**: Clean architecture with dependency injection, comprehensive error handling, and monitoring
- **Developer-Friendly**: Rich CLI experience, FastAPI integration, and extensible design

## Core Concepts

### Bounded Contexts

Insight Ingenious follows Domain-Driven Design principles with clear bounded contexts:

- **Chat**: Conversation management and AI interactions
- **CLI**: Command-line interface and project management
- **Configuration**: System settings and configuration management
- **Diagnostics**: Health monitoring and system diagnostics
- **External Integrations**: Third-party service integrations (Azure OpenAI, etc.)
- **File Management**: File operations and storage management
- **Prompt Management**: Prompt templates and ensemble orchestration
- **Security**: Authentication, authorization, and security features
- **Shared**: Cross-cutting concerns and shared utilities

### Architecture Principles

Each bounded context follows clean architecture with:
- **Domain Layer**: Pure business logic and rules
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: External implementations (databases, APIs, etc.)
- **Interface Layer**: REST controllers and CLI handlers

### Current Status

**Note**: Insight Ingenious is actively developed with some features in various stages of implementation:

- ✅ **Core CLI and API**: Fully functional
- ✅ **Chat endpoints**: Basic functionality available
- ✅ **File management**: Complete CRUD operations
- ✅ **Configuration management**: File-based configuration
- 🚧 **Prompt ensembles**: CLI available, some services use mock implementations
- 🚧 **Security features**: Basic authentication, advanced features in development
- 🚧 **Azure integrations**: Some endpoints use mock services for development
5. **Result Aggregation**: Intelligent synthesis of sub-prompt outputs

## Quick Example

```python
from ingenious.prompt_management.application.ensemble_use_cases import EnsembleManagementUseCase
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService

# Setup services
openai_service = AzureOpenAIService(
    azure_endpoint="https://your-endpoint.openai.azure.com",
    api_key="your-api-key",
    api_version="2024-06-01",
    model="gpt-4"
)

# Create ensemble
ensemble_use_case = EnsembleManagementUseCase(
    llm_service=openai_service,
    storage_service=blob_service
)

# Execute ensemble
result = await ensemble_use_case.execute_ensemble(
    config_id="my-ensemble",
    variables={"topic": "climate change", "depth": "detailed"}
)
```

## License

This project is licensed under the terms specified in the LICENSE file.
