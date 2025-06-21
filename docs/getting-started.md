# Getting Started with Insight Ingenious

This guide will help you set up and start using Insight Ingenious for AI-powered applications.

## Quick Setup

### 1. Installation

First, ensure you have Python 3.13+ and uv installed:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd Insight_Ingenious

# Install dependencies
uv sync
```

### 2. Initialize Your First Project

```bash
# Initialize a new project
uv run ingen init
```

This creates:
- `config.yml` - Main application configuration
- `profiles.yml` - API keys and secrets template
- `.gitignore` - Git ignore rules
- `SETUP.md` - Detailed setup instructions
- Directory structure (data/, files/, .tmp/)

### 3. Configure Azure OpenAI

Edit the `profiles.yml` file to add your Azure OpenAI credentials:

```yaml
- name: dev
  models:
    - model: gpt-4o
      api_key: "YOUR_AZURE_OPENAI_API_KEY"
      base_url: "https://YOUR_RESOURCE_NAME.openai.azure.com/"
      api_version: "2023-05-15"
```

### 4. Start the Server

```bash
# Start in development mode
uv run ingen dev

# Or start with custom options
uv run ingen run --host 127.0.0.1 --port 8000
```

Visit http://localhost:8000/docs to explore the API.

## Your First API Request

Once the server is running, you can make your first chat request:

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -u "testuser:testpass" \
  -d '{
    "user_prompt": "Hello! Can you help me understand AI?",
    "conversation_flow": "general",
    "user_id": "user-123"
  }'
```

## Working with Ensembles

Insight Ingenious supports prompt ensembles for complex analysis tasks.

### Creating an Ensemble Configuration

```bash
# Create a simple ensemble
uv run ingen ensemble create my-analysis --config analysis-config.json
```

Example `analysis-config.json`:

```json
{
  "description": "Multi-perspective topic analysis",
  "main_prompt_template": "Analyze {{ topic }} comprehensively.",
  "sub_prompt_templates": [
    {
      "name": "strengths_analyzer",
      "content": "Analyze the strengths of {{ topic }}.",
      "role": "analyzer",
      "priority": 1
    },
    {
      "name": "challenges_critic",
      "content": "Identify challenges with {{ topic }}.",
      "role": "critic",
      "priority": 1
    }
  ],
  "reduce_prompt_template": "Synthesize: {{ strengths_analyzer }} {{ challenges_critic }}",
  "variables": {
    "topic": "renewable energy"
  }
}
```

### Executing Ensembles

```bash
# Execute an ensemble
uv run ingen ensemble execute config-id --input analysis-data.json

# List your ensembles
uv run ingen ensemble list
```

## Programming with the API

### Python Client Example

    # Execute the ensemble
    result = await ensemble_use_case.execute_ensemble(
        config_id=config.config_id,
        variables={"topic": topic}
    )

    print(f"Analysis of '{topic}':")
    print(f"Execution Time: {result.total_duration_seconds:.2f} seconds")
    print(f"Success Rate: {result.success_rate:.1%}")
    print(f"\nFinal Result:\n{result.final_result}")

    # Show individual agent results
    for execution in result.agent_executions:
        if execution.is_successful:
            print(f"\n{execution.agent_role.value.title()} Analysis:")
            print(execution.response[:200] + "..." if len(execution.response) > 200 else execution.response)

# Run the analysis
if __name__ == "__main__":
    asyncio.run(analyze_topic("renewable energy adoption"))
```

## Using the CLI

Ingenious provides a powerful CLI for quick operations:

### Initialize a New Project

```bash
# Create a new Ingenious project
ingen init my-ai-project
cd my-ai-project
```

### Create Ensemble Configurations

```bash
# Create a new ensemble configuration
ingen ensemble create topic-analysis --config ensemble-config.json

# Create a predefined ensemble
ingen ensemble create-predefined multi_perspective_analysis topic-analysis

# List available ensembles
ingen ensemble list

# Execute an ensemble
ingen ensemble execute config-id --input '{"topic": "artificial intelligence"}'
```

### Start the Development Server

```bash
# Start the FastAPI development server
ingen dev

# Start production server
ingen run --host 0.0.0.0 --port 8000
```

## Configuration Patterns

### Environment Variables

```bash
# Azure OpenAI Configuration
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_API_VERSION="2024-06-01"
export AZURE_OPENAI_MODEL="gpt-4"

# Azure Blob Storage
export AZURE_STORAGE_ACCOUNT_URL="https://youraccount.blob.core.windows.net"
export AZURE_STORAGE_CREDENTIAL="your-credential"

# Working Directory
export INGENIOUS_WORKING_DIR="/path/to/your/project"
```

### Configuration File

Create a `config.json` file:

```json
{
  "azure_openai": {
    "endpoint": "https://your-endpoint.openai.azure.com",
    "api_key": "your-api-key",
    "api_version": "2024-06-01",
    "model": "gpt-4"
  },
  "azure_storage": {
    "account_url": "https://youraccount.blob.core.windows.net",
    "credential": "your-credential"
  },
  "ensemble_defaults": {
    "strategy": "parallel",
    "max_concurrent_agents": 5,
    "timeout_seconds": 300,
    "retry_count": 3
  }
}
```

## Execution Strategies

Ingenious supports three execution strategies:

### Parallel Execution

```python
# All sub-prompts execute simultaneously
strategy = EnsembleStrategy.PARALLEL
```

Best for: Independent analyses, multiple perspectives, speed

### Sequential Execution

```python
# Sub-prompts execute in priority order
strategy = EnsembleStrategy.SEQUENTIAL
```

Best for: Dependent tasks, building context, iterative refinement

### Hierarchical Execution

```python
# Sub-prompts execute in tree structure based on dependencies
strategy = EnsembleStrategy.HIERARCHICAL
```

Best for: Complex workflows, conditional logic, specialized roles

## Error Handling

Ingenious provides comprehensive error handling:

```python
from ingenious.shared.exceptions import BusinessLogicError, ValidationError

try:
    result = await ensemble_use_case.execute_ensemble(
        config_id="invalid-config",
        variables={"topic": "test"}
    )
except ValidationError as e:
    print(f"Validation error: {e}")
except BusinessLogicError as e:
    print(f"Business logic error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

Now that you have a basic understanding of Ingenious:

1. Explore [Prompt Ensembles](prompt-ensembles.md) for advanced ensemble patterns
2. Learn about [Azure Integration](azure-integration.md) for production deployments
3. Check out [Examples](examples/) for real-world use cases
4. Review [Best Practices](best-practices.md) for optimization tips

## Common Patterns

### Multi-Agent Analysis

```python
# Create specialized agents for different analysis types
agents = [
    {"role": "analyzer", "focus": "technical aspects"},
    {"role": "critic", "focus": "potential issues"},
    {"role": "synthesizer", "focus": "actionable insights"}
]
```

### Template Variables

```python
# Use rich template variables for dynamic prompts
variables = {
    "topic": "machine learning",
    "depth": "detailed",
    "audience": "technical professionals",
    "length": "comprehensive"
}
```

### Result Processing

```python
# Access detailed execution metrics
print(f"Total tokens used: {result.total_token_usage}")
print(f"Average response time: {result.average_response_time}")
print(f"Most successful agent: {result.best_performing_agent}")
```
