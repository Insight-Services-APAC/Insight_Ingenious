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

## What is Ingenious?

Ingenious is a Domain-Driven Design (DDD) based framework that enables developers to create sophisticated AI applications using prompt ensemble patterns. It provides:

- **Prompt Ensemble Orchestration**: Decompose complex prompts into sub-prompts, process them in parallel/sequential/hierarchical patterns, and aggregate results
- **Azure Service Integration**: Built-in support for Azure OpenAI, Blob Storage, SQL Database, and Cognitive Services
- **Production-Ready Architecture**: Clean architecture with dependency injection, comprehensive error handling, and monitoring
- **Flexible Configuration**: Python API, CLI, and template-based configuration
- **Developer-Friendly**: Rich CLI experience, comprehensive documentation, and extensible design

## Core Concepts

### Bounded Contexts

Ingenious follows Domain-Driven Design principles with clear bounded contexts:

- **Chat**: Conversation management and chat interfaces
- **Configuration**: System settings and configuration management
- **Diagnostics**: Health monitoring and system diagnostics
- **External Integrations**: Third-party service integrations (Azure, etc.)
- **File Management**: File operations and storage management
- **Prompt Management**: Prompt templates and ensemble orchestration
- **Security**: Authentication, authorization, and security features
- **Shared**: Cross-cutting concerns and shared utilities

### Prompt Ensembles

The core innovation of Ingenious is its prompt ensemble capability:

1. **Main Prompt**: A complex task description
2. **Sub-Prompts**: Decomposed tasks using Jinja2 templates
3. **Agent Roles**: Specialized roles (analyzer, critic, synthesizer, etc.)
4. **Execution Strategies**: Parallel, sequential, or hierarchical processing
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
