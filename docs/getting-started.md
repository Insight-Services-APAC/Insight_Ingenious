# Getting Started with Ingenious

This guide will help you build your first Ingenious application and understand the core concepts.

## Your First Ensemble

Let's create a simple prompt ensemble that analyzes a topic from multiple perspectives.

### Step 1: Basic Setup

```python
import asyncio
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService
from ingenious.external_integrations.infrastructure.blob_storage_service import AzureBlobStorageService
from ingenious.prompt_management.application.ensemble_use_cases import EnsembleManagementUseCase
from ingenious.prompt_management.domain.ensemble import (
    EnsemblePromptTemplate,
    AgentRole,
    EnsembleStrategy
)

# Configure Azure OpenAI
openai_service = AzureOpenAIService(
    azure_endpoint="https://your-endpoint.openai.azure.com",
    api_key="your-api-key",
    api_version="2024-06-01",
    model="gpt-4"
)

# Configure Azure Blob Storage (optional)
blob_service = AzureBlobStorageService(
    account_url="https://youraccount.blob.core.windows.net",
    credential="your-credential"
)

# Create ensemble use case
ensemble_use_case = EnsembleManagementUseCase(
    llm_service=openai_service,
    storage_service=blob_service
)
```

### Step 2: Define Your Ensemble

```python
async def create_topic_analysis_ensemble():
    # Define sub-prompt templates
    sub_prompts = [
        {
            "name": "strengths_analyzer",
            "content": "Analyze the strengths and benefits of {{ topic }}. Focus on positive aspects and opportunities. Provide specific examples.",
            "role": "analyzer",
            "priority": 1
        },
        {
            "name": "challenges_critic",
            "content": "Critically examine the challenges and limitations of {{ topic }}. What are the main obstacles and concerns?",
            "role": "critic",
            "priority": 1
        },
        {
            "name": "implementation_specialist",
            "content": "Provide practical implementation advice for {{ topic }}. How can this be applied in real-world scenarios?",
            "role": "specialist",
            "priority": 2
        }
    ]

    # Create ensemble configuration
    config = await ensemble_use_case.create_ensemble_configuration(
        name="topic_analysis",
        description="Multi-perspective analysis of any topic",
        main_prompt_template="Analyze {{ topic }} comprehensively from multiple angles.",
        sub_prompt_templates=sub_prompts,
        reduce_prompt_template="""
        Based on the following analyses, provide a balanced and comprehensive summary:

        Strengths Analysis: {{ strengths_analyzer }}

        Challenges Analysis: {{ challenges_critic }}

        Implementation Advice: {{ implementation_specialist }}

        Create a balanced overview that acknowledges both opportunities and challenges,
        with practical next steps.
        """,
        strategy="parallel",
        max_concurrent_agents=3,
        timeout_seconds=300
    )

    return config
```

### Step 3: Execute Your Ensemble

```python
async def analyze_topic(topic: str):
    # Create the ensemble configuration
    config = await create_topic_analysis_ensemble()

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
