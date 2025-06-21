# Examples

This directory contains practical examples demonstrating how to use the Ingenious framework for various AI applications.

## Basic Examples

### [Simple Topic Analysis](simple-topic-analysis.py)
A straightforward example showing how to create and execute a basic prompt ensemble that analyzes any topic from multiple perspectives.

**Features:**
- Parallel execution strategy
- Multiple agent roles (analyzer, critic, synthesizer)
- Template variables
- Result aggregation

**Use case:** General topic analysis for research or decision-making

### [Business Analysis Ensemble](business-analysis.py)
Comprehensive business analysis using specialized agents for market research, competitive analysis, and strategic recommendations.

**Features:**
- Hierarchical execution with dependencies
- Domain-specific agent roles
- Complex template inheritance
- Financial and market analysis

**Use case:** Business planning and market research

### [Content Creation Pipeline](content-creation.py)
Multi-stage content creation workflow that generates, reviews, and refines content using different AI agents.

**Features:**
- Sequential execution for iterative refinement
- Content quality assurance
- Style and tone consistency
- Multi-format output

**Use case:** Content marketing and documentation

## Advanced Examples

### [Multi-Language Translation](translation-ensemble.py)
Translation and localization workflow that handles context, cultural adaptation, and quality assurance.

**Features:**
- Parallel translation to multiple languages
- Cultural context adaptation
- Quality review and validation
- Terminology consistency

**Use case:** International content localization

### [Code Review Ensemble](code-review.py)
Automated code review system using specialized AI agents for different aspects of code quality.

**Features:**
- Security analysis agent
- Performance optimization agent
- Code style and maintainability review
- Documentation quality assessment

**Use case:** Software development workflows

### [Research Synthesis](research-synthesis.py)
Academic research analysis and synthesis from multiple sources and perspectives.

**Features:**
- Literature review and analysis
- Methodology evaluation
- Finding synthesis and comparison
- Citation and reference management

**Use case:** Academic research and systematic reviews

## Integration Examples

### [FastAPI Web Application](fastapi-integration/)
Complete web application demonstrating how to integrate Ingenious into a FastAPI backend.

**Includes:**
- REST API endpoints
- Authentication and authorization
- Real-time execution monitoring
- Result caching and storage

### [Jupyter Notebook Workflows](jupyter-notebooks/)
Interactive Jupyter notebooks showing different Ingenious workflows and analysis patterns.

**Includes:**
- Data analysis ensembles
- Visualization of results
- Parameter tuning examples
- Performance benchmarking

### [CLI Applications](cli-applications/)
Command-line applications built with Ingenious for various automation tasks.

**Includes:**
- Batch processing scripts
- Configuration management tools
- Monitoring and reporting utilities
- Integration with external systems

## Configuration Examples

### [Development Setup](config-examples/development.yaml)
Complete development environment configuration with mock services.

### [Production Deployment](config-examples/production.yaml)
Production-ready configuration with Azure services and security settings.

### [Multi-Environment](config-examples/)
Examples showing how to manage configurations across different environments.

## Testing Examples

### [Unit Testing](testing/unit-tests.py)
Comprehensive unit tests for ensemble configurations and executions.

### [Integration Testing](testing/integration-tests.py)
Integration tests with real Azure services and mock alternatives.

### [Performance Testing](testing/performance-tests.py)
Load testing and performance benchmarking examples.

## Getting Started

1. **Choose an example** that matches your use case
2. **Install dependencies** as specified in each example
3. **Configure Azure services** using the configuration templates
4. **Run the example** following the instructions in each file
5. **Modify and adapt** the code for your specific needs

## Example Structure

Each example follows this structure:

```
example-name/
├── README.md           # Detailed instructions and explanation
├── main.py            # Main implementation
├── config.yaml        # Configuration template
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
└── tests/             # Example-specific tests
```

## Contributing Examples

We welcome contributions of new examples! Please follow these guidelines:

1. **Clear documentation** with step-by-step instructions
2. **Working code** that can be run out-of-the-box
3. **Real-world relevance** addressing practical use cases
4. **Proper error handling** and logging
5. **Tests included** where appropriate

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.
