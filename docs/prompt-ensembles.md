# Prompt Ensembles

Prompt ensembles are the core innovation of the Ingenious framework. They allow you to decompose complex AI tasks into smaller, specialized sub-tasks that are processed by multiple AI agents and then intelligently aggregated.

## Core Concepts

### What is a Prompt Ensemble?

A prompt ensemble consists of:

1. **Main Prompt**: The original complex task or query
2. **Sub-Prompts**: Decomposed tasks created from Jinja2 templates
3. **Agent Roles**: Specialized roles for different types of analysis
4. **Execution Strategy**: How sub-prompts are processed (parallel/sequential/hierarchical)
5. **Aggregation Logic**: How individual results are synthesized into a final answer

### Benefits of Ensemble Approach

- **Specialization**: Each agent focuses on a specific aspect
- **Robustness**: Multiple perspectives reduce bias and increase accuracy
- **Scalability**: Parallel processing for improved performance
- **Flexibility**: Easy to modify individual components
- **Transparency**: Clear visibility into decision-making process

## Ensemble Components

### Agent Roles

Ingenious defines several standard agent roles:

```python
from ingenious.prompt_management.domain.ensemble import AgentRole

# Available roles
AgentRole.ANALYZER      # Examines and breaks down information
AgentRole.CRITIC        # Identifies problems and limitations
AgentRole.SYNTHESIZER   # Combines information from multiple sources
AgentRole.SPECIALIST    # Domain-specific expert analysis
AgentRole.REVIEWER      # Quality assurance and validation
```

### Execution Strategies

#### Parallel Strategy

All sub-prompts execute simultaneously for maximum speed:

```python
from ingenious.prompt_management.domain.ensemble import EnsembleStrategy

strategy = EnsembleStrategy.PARALLEL
```

**Use Cases:**
- Independent analysis tasks
- Multiple perspectives on the same topic
- When speed is prioritized
- Brainstorming and ideation

**Example:**
```python
# Analyzing a business proposal from multiple angles
sub_prompts = [
    {"role": "analyzer", "content": "Analyze market potential for {{ proposal }}"},
    {"role": "critic", "content": "Identify risks in {{ proposal }}"},
    {"role": "specialist", "content": "Assess technical feasibility of {{ proposal }}"}
]
```

#### Sequential Strategy

Sub-prompts execute in priority order, allowing later prompts to build on earlier results:

```python
strategy = EnsembleStrategy.SEQUENTIAL
```

**Use Cases:**
- Building complex arguments
- Iterative refinement
- When context accumulation is important
- Step-by-step problem solving

**Example:**
```python
# Research paper analysis
sub_prompts = [
    {"role": "analyzer", "priority": 1, "content": "Summarize key findings in {{ paper }}"},
    {"role": "critic", "priority": 2, "content": "Based on {{ analyzer_result }}, identify methodological issues"},
    {"role": "synthesizer", "priority": 3, "content": "Synthesize {{ analyzer_result }} and {{ critic_result }} into recommendations"}
]
```

#### Hierarchical Strategy

Sub-prompts execute based on dependency relationships:

```python
strategy = EnsembleStrategy.HIERARCHICAL
```

**Use Cases:**
- Complex workflows with dependencies
- Conditional execution paths
- Expert systems with specialized knowledge domains

**Example:**
```python
# Medical diagnosis ensemble
sub_prompts = [
    {"id": "symptoms", "role": "analyzer", "content": "Analyze symptoms: {{ patient_data }}"},
    {"id": "differential", "role": "specialist", "dependencies": ["symptoms"],
     "content": "Generate differential diagnosis based on {{ symptoms }}"},
    {"id": "tests", "role": "specialist", "dependencies": ["differential"],
     "content": "Recommend tests for {{ differential }}"}
]
```

## Creating Ensembles

### Basic Ensemble Configuration

```python
from ingenious.prompt_management.application.ensemble_use_cases import EnsembleManagementUseCase
from ingenious.prompt_management.domain.ensemble import EnsemblePromptTemplate, AgentRole

async def create_analysis_ensemble():
    # Define sub-prompt templates
    sub_prompts = [
        {
            "name": "strengths_analyzer",
            "content": """
            Analyze the strengths and positive aspects of {{ topic }}.
            Consider:
            - Unique advantages
            - Potential benefits
            - Success factors

            Topic: {{ topic }}
            Focus: {{ focus_area }}
            """,
            "role": "analyzer",
            "priority": 1,
            "variables": {"focus_area": "comprehensive"}
        },
        {
            "name": "weaknesses_critic",
            "content": """
            Critically examine potential weaknesses and challenges of {{ topic }}.
            Consider:
            - Limitations and constraints
            - Potential risks
            - Implementation challenges

            Topic: {{ topic }}
            """,
            "role": "critic",
            "priority": 1
        },
        {
            "name": "recommendations_synthesizer",
            "content": """
            Based on the strengths and weaknesses analysis, provide actionable recommendations.

            Strengths: {{ strengths_analyzer }}
            Weaknesses: {{ weaknesses_critic }}

            Provide specific, actionable recommendations that leverage strengths and address weaknesses.
            """,
            "role": "synthesizer",
            "priority": 2,
            "dependencies": ["strengths_analyzer", "weaknesses_critic"]
        }
    ]

    # Create ensemble configuration
    config = await ensemble_use_case.create_ensemble_configuration(
        name="comprehensive_analysis",
        description="Comprehensive analysis with strengths, weaknesses, and recommendations",
        main_prompt_template="Analyze {{ topic }} comprehensively from multiple perspectives.",
        sub_prompt_templates=sub_prompts,
        reduce_prompt_template="""
        Create a comprehensive analysis report based on the following components:

        ## Strengths Analysis
        {{ strengths_analyzer }}

        ## Challenges and Limitations
        {{ weaknesses_critic }}

        ## Recommendations
        {{ recommendations_synthesizer }}

        ## Executive Summary
        Provide a balanced executive summary that integrates all perspectives and highlights the most critical insights and actionable next steps.
        """,
        strategy="hierarchical",
        max_concurrent_agents=5,
        timeout_seconds=300,
        variables={"analysis_depth": "detailed", "output_format": "structured"}
    )

    return config
```

### Advanced Template Features

#### Template Inheritance

```python
# Base template for common analysis pattern
base_analysis = """
Context: {{ context }}
Topic: {{ topic }}
Perspective: {{ perspective }}

{{ specific_instructions }}

Format your response as:
1. Key Insights
2. Supporting Evidence
3. Implications
4. Confidence Level (1-10)
"""

# Specialized templates
market_analysis = base_analysis.replace(
    "{{ specific_instructions }}",
    "Focus on market dynamics, competition, and commercial viability."
)

technical_analysis = base_analysis.replace(
    "{{ specific_instructions }}",
    "Focus on technical implementation, scalability, and engineering challenges."
)
```

#### Conditional Logic

```python
# Template with conditional content
conditional_template = """
Analyze {{ topic }} from a {{ role }} perspective.

{% if depth == "detailed" %}
Provide in-depth analysis with specific examples and evidence.
Include quantitative metrics where possible.
{% else %}
Provide a high-level overview focusing on key points.
{% endif %}

{% if include_recommendations %}
End with 3-5 specific recommendations.
{% endif %}

{% if target_audience == "technical" %}
Use technical terminology and include implementation details.
{% elif target_audience == "executive" %}
Focus on business impact and strategic implications.
{% endif %}
"""
```

#### Dynamic Agent Assignment

```python
# Role assignment based on content type
def assign_agent_role(content_type: str) -> AgentRole:
    role_mapping = {
        "data": AgentRole.ANALYZER,
        "risk": AgentRole.CRITIC,
        "opportunity": AgentRole.SPECIALIST,
        "summary": AgentRole.SYNTHESIZER,
        "quality": AgentRole.REVIEWER
    }
    return role_mapping.get(content_type, AgentRole.ANALYZER)
```

## Execution and Monitoring

### Execute Ensemble

```python
async def execute_comprehensive_analysis():
    # Execute ensemble
    result = await ensemble_use_case.execute_ensemble(
        config_id=config.config_id,
        variables={
            "topic": "sustainable energy transition",
            "context": "corporate strategy planning",
            "depth": "detailed",
            "include_recommendations": True,
            "target_audience": "executive"
        }
    )

    return result
```

### Monitor Execution

```python
async def monitor_ensemble_execution(result):
    print(f"Ensemble Execution Results")
    print(f"========================")
    print(f"Total Duration: {result.total_duration_seconds:.2f} seconds")
    print(f"Success Rate: {result.success_rate:.1%}")
    print(f"Agents Executed: {len(result.agent_executions)}")
    print(f"Total Tokens: {result.total_token_usage}")

    # Individual agent performance
    for execution in result.agent_executions:
        print(f"\n{execution.agent_role.value.title()} Agent:")
        print(f"  Duration: {execution.duration_seconds:.2f}s")
        print(f"  Success: {'✓' if execution.is_successful else '✗'}")
        print(f"  Tokens: {execution.token_usage}")

        if execution.error:
            print(f"  Error: {execution.error}")
```

## Best Practices

### Template Design

1. **Clear Instructions**: Make agent instructions specific and actionable
2. **Context Provision**: Include sufficient context for decision-making
3. **Output Format**: Specify expected output structure
4. **Variable Usage**: Leverage template variables for flexibility

```python
# Good template example
good_template = """
Role: {{ role }}
Task: Analyze {{ topic }} focusing on {{ focus_area }}

Instructions:
1. Review the topic from your assigned perspective
2. Identify 3-5 key insights
3. Provide supporting evidence for each insight
4. Rate your confidence (1-10) for each insight

Context: {{ context }}

Output Format:
- Insight 1: [description] (Confidence: X/10)
- Insight 2: [description] (Confidence: X/10)
- etc.
"""
```

### Performance Optimization

1. **Agent Specialization**: Assign clear, non-overlapping roles
2. **Parallel Processing**: Use parallel strategy when possible
3. **Timeout Management**: Set appropriate timeouts for complex tasks
4. **Token Optimization**: Design concise but comprehensive prompts

```python
# Optimized configuration
optimized_config = {
    "strategy": "parallel",  # Faster execution
    "max_concurrent_agents": 3,  # Balance speed vs. resource usage
    "timeout_seconds": 120,  # Reasonable timeout
    "retry_count": 2,  # Limited retries
}
```

### Error Handling

```python
from ingenious.shared.exceptions import BusinessLogicError, ValidationError

async def robust_ensemble_execution():
    try:
        result = await ensemble_use_case.execute_ensemble(
            config_id="analysis-ensemble",
            variables={"topic": "AI ethics"}
        )

        # Check for partial failures
        if result.success_rate < 0.8:
            logger.warning(f"Low success rate: {result.success_rate:.1%}")

        return result

    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

    except BusinessLogicError as e:
        logger.error(f"Business logic error: {e}")
        # Potentially retry with different configuration
        raise

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

## Advanced Patterns

### Multi-Stage Ensembles

```python
# Stage 1: Analysis
analysis_result = await execute_analysis_ensemble(topic)

# Stage 2: Validation (using analysis results)
validation_result = await execute_validation_ensemble(
    analysis_result.final_result
)

# Stage 3: Recommendations (using both results)
recommendations = await execute_recommendation_ensemble(
    analysis_result.final_result,
    validation_result.final_result
)
```

### Adaptive Ensembles

```python
async def adaptive_ensemble(topic: str, complexity: str):
    if complexity == "high":
        # Use more agents and hierarchical strategy
        return await execute_detailed_ensemble(topic)
    elif complexity == "medium":
        # Balanced approach
        return await execute_standard_ensemble(topic)
    else:
        # Quick analysis
        return await execute_simple_ensemble(topic)
```

### Ensemble Chains

```python
async def ensemble_chain(topics: List[str]):
    results = []
    context = ""

    for topic in topics:
        result = await ensemble_use_case.execute_ensemble(
            config_id="cumulative-analysis",
            variables={
                "topic": topic,
                "previous_context": context
            }
        )

        results.append(result)
        context += f"\nPrevious analysis: {result.final_result}"

    return results
```

## Integration Examples

See the [Examples](examples/) directory for complete integration examples including:

- **Business Analysis Ensemble**: Market research and competitive analysis
- **Content Creation Ensemble**: Multi-perspective content generation
- **Technical Review Ensemble**: Code review and architecture analysis
- **Research Synthesis Ensemble**: Academic paper analysis and synthesis
