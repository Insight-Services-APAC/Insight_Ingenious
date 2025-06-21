# Documentation Summary

This directory contains comprehensive documentation for the Ingenious framework, a production-ready Python library for building AI-powered applications with prompt ensemble orchestration and Azure service integration.

## Documentation Structure

### Core Documentation
- **[README.md](README.md)** - Main overview and navigation
- **[Installation Guide](installation.md)** - Setup instructions for pip/uv installation
- **[Getting Started](getting-started.md)** - First steps and basic examples
- **[Configuration](configuration.md)** - Complete configuration reference

### Feature Documentation
- **[Prompt Ensembles](prompt-ensembles.md)** - Core ensemble functionality and patterns
- **[Azure Integration](azure-integration.md)** - Azure services setup and usage
- **[CLI Usage](cli-usage.md)** - Command-line interface guide
- **[API Reference](api-reference.md)** - Complete API documentation

### Operational Documentation
- **[Best Practices](best-practices.md)** - Recommended patterns and practices
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Examples](examples/)** - Practical usage examples and tutorials

## Key Framework Features

### Prompt Ensemble Orchestration
The core innovation of Ingenious is its ability to decompose complex AI tasks into specialized sub-tasks:

```python
# Create an ensemble that analyzes topics from multiple perspectives
config = await ensemble_use_case.create_ensemble_configuration(
    name="topic_analysis",
    strategy="parallel",  # or "sequential" or "hierarchical"
    sub_prompt_templates=[
        {"role": "analyzer", "content": "Analyze strengths of {{ topic }}"},
        {"role": "critic", "content": "Identify challenges with {{ topic }}"},
        {"role": "synthesizer", "content": "Synthesize insights from analysis"}
    ]
)
```

### Azure Service Integration
Production-ready integration with Azure services:

- **Azure OpenAI**: LLM inference with rate limiting and retry logic
- **Azure Blob Storage**: Conversation and result persistence
- **Azure SQL Database**: Structured data storage and analytics
- **Azure Cognitive Services**: Content moderation and validation

### Domain-Driven Design Architecture
Clean, maintainable codebase with clear bounded contexts:

- **Chat**: Conversation management
- **Configuration**: Settings and environment management
- **Diagnostics**: Health monitoring and metrics
- **External Integrations**: Azure service integrations
- **File Management**: File operations and storage
- **Prompt Management**: Ensemble orchestration
- **Security**: Authentication and authorization
- **Shared**: Cross-cutting concerns

## Installation and Setup

### Quick Installation
```bash
pip install insight-ingenious
```

### Basic Configuration
```bash
# Set required environment variables
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_MODEL="gpt-4"
```

### Verify Installation
```bash
ingen --help
python -c "import ingenious; print('Ingenious installed successfully')"
```

## Common Use Cases

### 1. Topic Analysis
Analyze any topic from multiple perspectives:
```bash
python docs/examples/simple-topic-analysis.py "renewable energy"
```

### 2. Business Analysis
Comprehensive business opportunity assessment:
```bash
python docs/examples/business-analysis.py "AI startup" "technology"
```

### 3. Content Creation
Multi-stage content creation and review workflows

### 4. Research Synthesis
Academic research analysis and literature review

### 5. Code Review
Automated code quality assessment and recommendations

## CLI Quick Reference

```bash
# Initialize new project
ingen init my-project

# Start development server
ingen dev

# Create ensemble configuration
ingen ensemble create analysis-config --config config.json

# Execute ensemble
ingen ensemble run analysis-config --variables '{"topic": "AI"}'

# Check system health
ingen health

# View configuration
ingen config show
```

## Python API Quick Reference

```python
from ingenious.prompt_management.application.ensemble_use_cases import EnsembleManagementUseCase
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService

# Setup services
openai_service = AzureOpenAIService(...)
ensemble_use_case = EnsembleManagementUseCase(llm_service=openai_service)

# Create and execute ensemble
config = await ensemble_use_case.create_ensemble_configuration(...)
result = await ensemble_use_case.execute_ensemble(config_id, variables)
```

## Development Workflow

Based on the testing conducted in the development workspace, the recommended workflow is:

1. **Project Setup**: Use `ingen init` to create project structure
2. **Configuration**: Set up Azure services and environment variables
3. **Ensemble Design**: Create specialized agents with clear roles
4. **Testing**: Use `uv run python -c ...` for iterative testing
5. **Deployment**: Use production configuration with managed identity
6. **Monitoring**: Implement health checks and metrics collection

## Lessons Learned from Testing

### Performance Optimization
- Use parallel execution for independent tasks
- Implement proper timeout and retry strategies
- Monitor token usage and optimize prompt length
- Use caching for repeated requests

### Error Handling
- Implement graceful degradation for partial failures
- Use circuit breaker patterns for external services
- Provide meaningful error messages and logging
- Design fallback strategies for critical paths

### Security Best Practices
- Never store secrets in configuration files
- Use Azure Managed Identity in production
- Implement proper input validation and output sanitization
- Enable audit logging for compliance

### Azure Integration
- Test with mock services during development
- Use appropriate retry and backoff strategies
- Monitor rate limits and quotas
- Implement proper health checks

## Getting Help

### Documentation Navigation
- Start with [Getting Started](getting-started.md) for your first application
- Use [API Reference](api-reference.md) for detailed implementation
- Check [Troubleshooting](troubleshooting.md) for common issues
- Review [Examples](examples/) for practical implementations

### Community Resources
- GitHub Issues for bug reports and feature requests
- Documentation feedback and improvements
- Example contributions and use cases

### Support Channels
- Technical documentation covers 90% of use cases
- Examples provide working implementations
- Troubleshooting guide addresses common issues
- API reference covers all public interfaces

## What's Next?

After reading this documentation, you should be able to:

1. **Install and configure** Ingenious in your environment
2. **Create prompt ensembles** for your specific use cases
3. **Integrate with Azure services** for production deployment
4. **Implement best practices** for security and performance
5. **Troubleshoot common issues** and optimize performance
6. **Scale your applications** using the framework's patterns

The framework is designed to be production-ready while remaining developer-friendly. The Domain-Driven Design architecture ensures maintainability, while the comprehensive Azure integration provides enterprise-grade capabilities.

For the most up-to-date information and examples, refer to the individual documentation files and the examples directory.
