# Prompt Ensemble Framework

The Prompt Ensemble Framework is a sophisticated system for orchestrating multiple AI agents to work together on complex tasks. It allows you to decompose a main prompt into specialized sub-prompts, execute them using different strategies, and aggregate the results into a comprehensive final output.

## Key Concepts

### Ensemble Configuration
An ensemble configuration defines how multiple AI agents work together:
- **Main Prompt Template**: The primary prompt that defines the overall task
- **Sub-Prompt Templates**: Specialized prompts for individual agents with specific roles
- **Reduce Prompt Template**: Template for aggregating individual agent responses
- **Execution Strategy**: How agents are coordinated (parallel, sequential, hierarchical)

### Agent Roles
Different types of agents can participate in an ensemble:
- **Analyzer**: Focuses on analytical assessment and data interpretation
- **Critic**: Provides critical evaluation and identifies issues/limitations
- **Synthesizer**: Combines and integrates information from multiple sources
- **Specialist**: Brings domain-specific expertise to the analysis
- **Reviewer**: Provides comprehensive review and quality assessment

### Execution Strategies

#### Parallel Execution
All agents execute simultaneously with no dependencies:
```json
{
  "strategy": "parallel",
  "max_concurrent_agents": 5
}
```

#### Sequential Execution
Agents execute in priority order, one after another:
```json
{
  "strategy": "sequential"
}
```

#### Hierarchical Execution
Agents execute based on dependency relationships:
```json
{
  "strategy": "hierarchical",
  "sub_prompt_templates": [
    {
      "name": "base_analysis",
      "dependencies": [],
      "priority": 1
    },
    {
      "name": "dependent_review",
      "dependencies": ["base_analysis"],
      "priority": 2
    }
  ]
}
```

## Getting Started

### Installation

Ensure you have the required dependencies:

```bash
uv add azure-storage-blob azure-identity
```

### Basic Usage

#### 1. Create an Ensemble Configuration

```python
from ingenious.prompt_management.domain.ensemble import (
    EnsembleConfiguration,
    EnsemblePromptTemplate,
    AgentRole,
    EnsembleStrategy
)

# Define sub-prompt templates
sub_templates = [
    EnsemblePromptTemplate(
        name="content_analyzer",
        content="Analyze the following content: {{ content }}\\n\\nFocus on structure, clarity, and completeness.",
        role=AgentRole.ANALYZER,
        priority=1,
    ),
    EnsemblePromptTemplate(
        name="critical_reviewer",
        content="Critically evaluate: {{ content }}\\n\\nIdentify weaknesses, biases, and areas for improvement.",
        role=AgentRole.CRITIC,
        priority=1,
    ),
]

# Create configuration
config = EnsembleConfiguration(
    name="document_analysis",
    description="Multi-perspective document analysis",
    strategy=EnsembleStrategy.PARALLEL,
    main_prompt_template="Analyze this document: {{ content }}",
    sub_prompt_templates=sub_templates,
    reduce_prompt_template="Synthesize the following analyses:\\n\\n{% for role, response in agent_responses.items() %}**{{ role }}**: {{ response }}\\n\\n{% endfor %}",
    max_concurrent_agents=3,
)
```

#### 2. Execute the Ensemble

```python
from ingenious.prompt_management.application.ensemble_use_cases import EnsembleManagementUseCase

# Setup services (see configuration section)
ensemble_service = EnsembleManagementUseCase(llm_service, storage_service)

# Execute ensemble
input_data = {
    "content": "Your document content here..."
}

result = await ensemble_service.execute_ensemble(
    config_id=config.config_id,
    input_data=input_data,
    store_results=True
)

print(f"Final Response: {result.final_response}")
print(f"Individual Responses: {result.agent_responses}")
```

## CLI Usage

The framework includes a comprehensive CLI for managing ensembles:

### Creating Ensembles

#### From Configuration File
```bash
# Create ensemble from JSON configuration
ingen ensemble create my_analysis_ensemble --config examples/document_analysis_ensemble.json

# Create with custom parameters
ingen ensemble create custom_ensemble --config my_config.json --strategy sequential --max-agents 3
```

#### Predefined Ensembles
```bash
# Create predefined ensemble types
ingen ensemble create-predefined multi_perspective_analysis "Content Analysis"
ingen ensemble create-predefined document_review "Document Review System"
ingen ensemble create-predefined code_review "Code Quality Assessment"
ingen ensemble create-predefined research_synthesis "Research Synthesis Tool"
```

### Executing Ensembles

```bash
# Execute with input file
ingen ensemble execute config_id_here --input input_data.json --output results.json

# Execute with direct text input
ingen ensemble execute config_id_here --text "Content to analyze" --output analysis_results.json
```

### Managing Ensembles

```bash
# List available configurations
ingen ensemble list --limit 20

# Get configuration details
ingen ensemble get config_id_here --templates

# List executions
ingen ensemble executions --config-id config_id_here --status completed

# Get execution results
ingen ensemble result execution_id_here --agents --output detailed_results.json
```

### Sample Configurations

```bash
# Generate sample configuration files
ingen ensemble sample-config basic_example.json --ensemble-type basic
ingen ensemble sample-config advanced_example.json --ensemble-type advanced
```

## Configuration Examples

### Multi-Perspective Analysis

```json
{
  "description": "Comprehensive multi-perspective analysis",
  "main_prompt_template": "Analyze: {{ content }}",
  "sub_prompt_templates": [
    {
      "name": "analytical_perspective",
      "content": "Provide analytical assessment of: {{ content }}\\n\\nFocus on logic, evidence, and methodology.",
      "role": "analyzer",
      "priority": 1
    },
    {
      "name": "critical_perspective",
      "content": "Critically evaluate: {{ content }}\\n\\nIdentify assumptions, limitations, and biases.",
      "role": "critic",
      "priority": 1
    }
  ],
  "reduce_prompt_template": "Synthesize perspectives: {% for role, response in agent_responses.items() %}{{ response }}{% endfor %}",
  "variables": {
    "analysis_depth": "comprehensive"
  }
}
```

### Hierarchical Document Review

```json
{
  "description": "Hierarchical document review with dependencies",
  "strategy": "hierarchical",
  "sub_prompt_templates": [
    {
      "name": "initial_review",
      "content": "Initial review of: {{ document }}",
      "role": "reviewer",
      "priority": 1,
      "dependencies": []
    },
    {
      "name": "detailed_analysis",
      "content": "Detailed analysis based on initial review: {{ document }}",
      "role": "analyzer",
      "priority": 2,
      "dependencies": ["initial_review"]
    },
    {
      "name": "final_synthesis",
      "content": "Final synthesis of review and analysis: {{ document }}",
      "role": "synthesizer",
      "priority": 3,
      "dependencies": ["initial_review", "detailed_analysis"]
    }
  ]
}
```

## Advanced Features

### Template Variables

Templates support Jinja2 templating with custom variables:

```json
{
  "name": "specialized_analysis",
  "content": "Analyze {{ content }} with {{ analysis_style }} approach, focusing on {{ focus_area }}",
  "role": "specialist",
  "variables": {
    "analysis_style": "detailed",
    "focus_area": "technical_accuracy"
  }
}
```

### Error Handling and Resilience

The framework provides robust error handling:
- Individual agent failures don't stop the ensemble
- Partial results are aggregated when some agents fail
- Detailed execution statistics and error reporting
- Configurable retry mechanisms

### Azure Integration

#### Blob Storage
All configurations, executions, and results are stored in Azure Blob Storage:
- Automatic container management
- Metadata tagging for efficient querying
- JSON serialization with timestamps
- Scalable storage for large-scale operations

#### Azure OpenAI Integration
Native integration with Azure OpenAI services:
- Support for chat completions and embeddings
- Token usage tracking and cost estimation
- Content filtering and safety measures
- Rate limiting and concurrent execution control

### Monitoring and Analytics

Track ensemble performance with detailed metrics:
- Execution duration and timing
- Token usage and cost estimates
- Success/failure rates per agent role
- Performance trends over time

```python
# Access execution statistics
result = await ensemble_service.execute_ensemble(config_id, input_data)
stats = result.execution_stats

print(f"Duration: {stats['total_duration_seconds']}s")
print(f"Total Tokens: {stats['total_tokens_used']}")
print(f"Success Rate: {stats['successful_agents']}/{stats['successful_agents'] + stats['failed_agents']}")
```

## Best Practices

### Template Design
1. **Clear Role Definition**: Each agent should have a distinct, well-defined role
2. **Specific Instructions**: Provide detailed, actionable instructions for each agent
3. **Context Variables**: Use template variables to customize behavior
4. **Output Format**: Specify expected output format and structure

### Execution Strategy Selection
- **Parallel**: Use for independent analyses that can run simultaneously
- **Sequential**: Use when later agents need context from earlier ones
- **Hierarchical**: Use for complex dependency relationships

### Performance Optimization
1. **Concurrent Limits**: Set appropriate `max_concurrent_agents` based on API limits
2. **Timeout Management**: Configure reasonable timeouts for your use case
3. **Error Recovery**: Design reduce templates to handle partial results gracefully
4. **Caching**: Consider caching strategies for repeated executions

### Configuration Management
1. **Version Control**: Store configurations in version control systems
2. **Environment Variables**: Use variables for environment-specific settings
3. **Testing**: Test configurations with sample data before production use
4. **Documentation**: Document the purpose and expected behavior of each ensemble

## Troubleshooting

### Common Issues

#### Configuration Errors
```bash
# Validate configuration before creation
ingen ensemble create test_config --config invalid_config.json
# Error: Invalid agent role: 'unknown_role'
```

#### Execution Failures
```bash
# Check execution status and errors
ingen ensemble executions --status failed
ingen ensemble result failed_execution_id --agents
```

#### Performance Issues
- Monitor token usage and costs
- Adjust concurrent agent limits
- Optimize prompt templates for efficiency
- Consider using sequential execution for better control

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.getLogger('ingenious.prompt_management').setLevel(logging.DEBUG)
```

### Support

For additional support:
1. Check the test suite for usage examples
2. Review sample configurations in the `examples/` directory
3. Enable debug logging for detailed execution traces
4. Monitor Azure service health and API limits

## Migration Guide

### From Simple Prompts

If you're currently using single prompts, here's how to migrate to ensembles:

1. **Identify Perspectives**: Break down your single prompt into different analytical perspectives
2. **Define Roles**: Assign appropriate roles (analyzer, critic, synthesizer, etc.)
3. **Create Templates**: Convert each perspective into a template with specific instructions
4. **Design Aggregation**: Create a reduce template that synthesizes individual responses
5. **Test and Iterate**: Start with parallel execution and refine based on results

### Configuration Schema Evolution

The framework supports configuration versioning to handle schema changes:
- Old configurations remain supported
- New features are opt-in
- Migration utilities help upgrade configurations
- Backward compatibility is maintained
