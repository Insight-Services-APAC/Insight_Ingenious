# Examples

This directory contains practical examples demonstrating how to use the Ingenious framework for various AI applications.

## Available Examples

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

## Running Examples

Each example can be run independently:

```bash
# Simple topic analysis
cd docs/examples
uv run python simple-topic-analysis.py "artificial intelligence"

# Business analysis
uv run python business-analysis.py "electric vehicle startup" "automotive"
```

## Configuration

Examples require proper environment configuration:

1. Set up your Azure OpenAI credentials in environment variables:
   ```bash
   export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
   export AZURE_OPENAI_API_KEY="your-api-key"
   export AZURE_OPENAI_MODEL="gpt-4"  # optional
   ```

2. Ensure Ingenious is properly installed:
   ```bash
   uv sync
   ```

3. Run examples from the project root or examples directory

## Future Examples

The following examples are planned for future releases:

### Jupyter Notebook Workflows
Interactive Jupyter notebooks showing different Ingenious workflows and analysis patterns.

### CLI Applications
Command-line applications built with Ingenious for various automation tasks.

### Configuration Examples
Complete configuration templates for different environments and use cases.

## Getting Started

1. **Choose an example** that matches your use case
2. **Set up environment variables** with your Azure OpenAI credentials
3. **Install dependencies** with `uv sync`
4. **Run the example** following the usage instructions in each file
5. **Modify and adapt** the code for your specific needs

## Current Example Structure

Each example is a standalone Python file with:

- **Complete implementation** ready to run
- **Detailed docstring** explaining the purpose and usage
- **Command-line interface** for easy execution
- **Error handling** and informative output
- **Environment variable** support for configuration

Examples are located directly in the `docs/examples/` directory:
- `simple-topic-analysis.py` - Basic multi-perspective analysis
- `business-analysis.py` - Comprehensive business analysis

## Contributing Examples

We welcome contributions of new examples! Please follow these guidelines:

1. **Clear documentation** with step-by-step instructions
2. **Working code** that can be run out-of-the-box
3. **Real-world relevance** addressing practical use cases
4. **Proper error handling** and logging
5. **Tests included** where appropriate

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.
