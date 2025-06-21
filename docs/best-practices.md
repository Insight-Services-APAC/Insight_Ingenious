# Best Practices

This guide covers recommended practices for building robust, maintainable, and efficient applications with the Ingenious framework.

## Ensemble Design Patterns

### 1. Single Responsibility Principle

Design each agent with a clear, focused responsibility:

```python
# ✓ Good: Focused agent roles
sub_prompts = [
    {
        "name": "data_analyzer",
        "role": "analyzer",
        "content": "Analyze only the quantitative data in {{ dataset }}. Focus on statistical patterns, outliers, and trends."
    },
    {
        "name": "insight_synthesizer",
        "role": "synthesizer",
        "content": "Based on the data analysis: {{ data_analyzer }}, provide 3 key business insights."
    }
]

# ✗ Avoid: Overly broad responsibilities
bad_prompt = {
    "name": "everything_agent",
    "content": "Analyze the data, find insights, create recommendations, write a report, and suggest next steps for {{ topic }}."
}
```

### 2. Template Modularity

Create reusable template components:

```python
# Base analysis template
BASE_ANALYSIS = """
Context: {{ context }}
Focus Area: {{ focus_area }}
Data: {{ data }}

Instructions:
1. Examine the provided data
2. Apply {{ methodology }} methodology
3. Present findings in {{ output_format }} format

{{ role_specific_instructions }}
"""

# Specialized templates
MARKET_ANALYSIS = BASE_ANALYSIS.replace(
    "{{ role_specific_instructions }}",
    "Focus on market trends, competitive landscape, and opportunities."
)

RISK_ANALYSIS = BASE_ANALYSIS.replace(
    "{{ role_specific_instructions }}",
    "Identify potential risks, their likelihood, and impact assessment."
)
```

### 3. Progressive Refinement

Use sequential strategies for complex reasoning:

```python
# Stage 1: Initial analysis
stage1_prompts = [
    {"name": "data_summary", "priority": 1, "role": "analyzer"},
    {"name": "initial_insights", "priority": 1, "role": "specialist"}
]

# Stage 2: Validation and critique
stage2_prompts = [
    {
        "name": "insight_validation",
        "priority": 2,
        "role": "critic",
        "dependencies": ["data_summary", "initial_insights"],
        "content": "Validate these insights: {{ initial_insights }} against the data: {{ data_summary }}"
    }
]

# Stage 3: Final synthesis
stage3_prompts = [
    {
        "name": "final_recommendations",
        "priority": 3,
        "role": "synthesizer",
        "dependencies": ["insight_validation"],
        "content": "Create actionable recommendations based on validated insights: {{ insight_validation }}"
    }
]
```

### 4. Error-Resilient Design

Build ensembles that gracefully handle failures:

```python
async def resilient_ensemble_execution():
    try:
        # Primary ensemble with all agents
        result = await ensemble_use_case.execute_ensemble(
            config_id="comprehensive_analysis",
            variables=variables
        )

        # Check if we have sufficient results
        if result.success_rate >= 0.7:
            return result

        # Fallback to simpler ensemble
        logger.warning(f"Low success rate ({result.success_rate:.1%}), using fallback")
        fallback_result = await ensemble_use_case.execute_ensemble(
            config_id="simple_analysis",
            variables=variables
        )

        return fallback_result

    except Exception as e:
        logger.error(f"Ensemble execution failed: {e}")
        # Final fallback to single agent
        return await single_agent_fallback(variables)
```

## Performance Optimization

### 1. Parallel Execution Strategy

Maximize concurrency for independent tasks:

```python
# ✓ Good: Independent analyses in parallel
parallel_config = {
    "strategy": "parallel",
    "max_concurrent_agents": 5,
    "sub_prompts": [
        {"name": "market_analysis", "role": "analyst"},
        {"name": "competitor_analysis", "role": "analyst"},
        {"name": "risk_assessment", "role": "critic"},
        {"name": "opportunity_identification", "role": "specialist"}
    ]
}

# ✗ Avoid: Sequential execution for independent tasks
sequential_config = {
    "strategy": "sequential",  # Unnecessary serialization
    "sub_prompts": parallel_config["sub_prompts"]
}
```

### 2. Token Optimization

Design prompts for efficiency:

```python
# ✓ Good: Concise, focused prompts
efficient_prompt = """
Analyze market size for {{ product }} in {{ region }}.

Output format:
- Total Addressable Market: $X
- Serviceable Market: $Y
- Key growth drivers: 3 bullet points
- Confidence level: High/Medium/Low
"""

# ✗ Avoid: Verbose, unfocused prompts
verbose_prompt = """
Please conduct a comprehensive and detailed analysis of the entire market landscape
for the product {{ product }} in the region {{ region }}. I want you to consider
all possible factors including but not limited to economic conditions, competitive
landscape, regulatory environment, customer preferences, technological trends,
social factors, and any other relevant considerations. Please provide extensive
details about market sizing, segmentation, growth projections, key players,
barriers to entry, opportunities, threats, and recommendations.
"""
```

### 3. Caching Strategies

Implement intelligent caching:

```python
from functools import lru_cache
import hashlib

class CachedEnsembleService:
    def __init__(self, ensemble_use_case):
        self.ensemble_use_case = ensemble_use_case
        self.cache = {}

    def _cache_key(self, config_id: str, variables: dict) -> str:
        """Generate cache key from config and variables."""
        content = f"{config_id}:{sorted(variables.items())}"
        return hashlib.md5(content.encode()).hexdigest()

    async def execute_with_cache(self, config_id: str, variables: dict, ttl: int = 3600):
        cache_key = self._cache_key(config_id, variables)

        # Check cache
        if cache_key in self.cache:
            cached_result, timestamp = self.cache[cache_key]
            if time.time() - timestamp < ttl:
                logger.info(f"Cache hit for {config_id}")
                return cached_result

        # Execute ensemble
        result = await self.ensemble_use_case.execute_ensemble(config_id, variables)

        # Cache result
        self.cache[cache_key] = (result, time.time())

        return result
```

### 4. Resource Management

Monitor and limit resource usage:

```python
import asyncio
from asyncio import Semaphore

class ResourceManagedEnsemble:
    def __init__(self, max_concurrent_ensembles: int = 3):
        self.semaphore = Semaphore(max_concurrent_ensembles)
        self.active_executions = {}

    async def execute_ensemble(self, config_id: str, variables: dict):
        async with self.semaphore:
            execution_id = str(uuid4())
            self.active_executions[execution_id] = {
                "config_id": config_id,
                "started_at": time.time(),
                "variables": variables
            }

            try:
                result = await ensemble_use_case.execute_ensemble(config_id, variables)
                return result
            finally:
                del self.active_executions[execution_id]
```

## Security Best Practices

### 1. Input Validation

Always validate user inputs:

```python
from pydantic import BaseModel, validator
import re

class EnsembleExecutionRequest(BaseModel):
    config_id: str
    variables: dict

    @validator('config_id')
    def validate_config_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Config ID contains invalid characters')
        if len(v) > 100:
            raise ValueError('Config ID too long')
        return v

    @validator('variables')
    def validate_variables(cls, v):
        # Limit variables size
        if len(str(v)) > 10000:
            raise ValueError('Variables payload too large')

        # Check for suspicious content
        suspicious_patterns = ['<script>', 'javascript:', 'data:']
        for key, value in v.items():
            if isinstance(value, str):
                for pattern in suspicious_patterns:
                    if pattern.lower() in value.lower():
                        raise ValueError(f'Suspicious content in variable {key}')

        return v
```

### 2. Output Sanitization

Sanitize LLM outputs before use:

```python
import html
import re

def sanitize_llm_output(text: str) -> str:
    """Sanitize LLM output for safe display."""
    # HTML escape
    text = html.escape(text)

    # Remove potential script tags
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)

    # Remove suspicious URLs
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)

    # Limit length
    if len(text) > 50000:
        text = text[:50000] + "... [truncated]"

    return text

# Apply to ensemble results
result = await ensemble_use_case.execute_ensemble(config_id, variables)
result.final_result = sanitize_llm_output(result.final_result)
```

### 3. Access Control

Implement proper authorization:

```python
from functools import wraps
from typing import List

def require_permissions(required_permissions: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user context (from JWT, session, etc.)
            user = get_current_user()

            # Check permissions
            user_permissions = await get_user_permissions(user.id)

            if not all(perm in user_permissions for perm in required_permissions):
                raise AuthorizationError("Insufficient permissions")

            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Apply to ensemble operations
@require_permissions(["ensemble:execute"])
async def execute_ensemble_with_auth(config_id: str, variables: dict):
    return await ensemble_use_case.execute_ensemble(config_id, variables)
```

### 4. Audit Logging

Log all important operations:

```python
import logging
from datetime import datetime
import json

# Configure audit logger
audit_logger = logging.getLogger('audit')
audit_handler = logging.FileHandler('audit.log')
audit_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
audit_logger.addHandler(audit_handler)
audit_logger.setLevel(logging.INFO)

async def audit_ensemble_execution(user_id: str, config_id: str, variables: dict, result: dict):
    audit_event = {
        "event_type": "ensemble_execution",
        "user_id": user_id,
        "config_id": config_id,
        "variables": variables,
        "success": result.get("success", False),
        "duration": result.get("duration_seconds"),
        "token_usage": result.get("token_usage"),
        "timestamp": datetime.utcnow().isoformat()
    }

    audit_logger.info(json.dumps(audit_event))
```

## Configuration Management

### 1. Environment-Based Configuration

Use different configurations for different environments:

```python
import os
from typing import Dict, Any

class EnvironmentConfig:
    """Environment-specific configuration management."""

    def __init__(self):
        self.env = os.getenv("INGENIOUS_ENV", "development")
        self.configs = {
            "development": self._dev_config(),
            "staging": self._staging_config(),
            "production": self._prod_config()
        }

    def _dev_config(self) -> Dict[str, Any]:
        return {
            "azure": {
                "openai": {
                    "endpoint": "http://localhost:5001",  # Mock service
                    "api_key": "dev-key"
                }
            },
            "ensemble_defaults": {
                "timeout_seconds": 60,  # Shorter timeouts for dev
                "max_concurrent_agents": 2
            },
            "features": {
                "telemetry": False,
                "audit_logging": False
            }
        }

    def _prod_config(self) -> Dict[str, Any]:
        return {
            "azure": {
                "openai": {
                    "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
                    # Use managed identity (no API key)
                }
            },
            "ensemble_defaults": {
                "timeout_seconds": 300,
                "max_concurrent_agents": 10
            },
            "features": {
                "telemetry": True,
                "audit_logging": True,
                "content_moderation": True
            }
        }

    def get_config(self) -> Dict[str, Any]:
        return self.configs[self.env]
```

### 2. Secret Management

Never store secrets in code:

```python
# ✓ Good: Use environment variables or Key Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class SecretManager:
    def __init__(self, key_vault_url: str):
        credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=key_vault_url, credential=credential)

    def get_secret(self, name: str) -> str:
        return self.client.get_secret(name).value

# ✗ Avoid: Hardcoded secrets
HARDCODED_API_KEY = "sk-1234567890abcdef"  # Never do this!
```

### 3. Configuration Validation

Validate configuration at startup:

```python
from pydantic import BaseModel, validator, ValidationError

class AzureConfig(BaseModel):
    openai_endpoint: str
    openai_api_key: str
    storage_account_url: str

    @validator('openai_endpoint')
    def validate_endpoint(cls, v):
        if not v.startswith(('https://', 'http://localhost')):
            raise ValueError('Invalid endpoint URL')
        return v

    @validator('openai_api_key')
    def validate_api_key(cls, v):
        if len(v) < 10:
            raise ValueError('API key too short')
        return v

def validate_configuration():
    try:
        config_data = load_configuration()
        azure_config = AzureConfig(**config_data['azure'])
        logger.info("✓ Configuration validation passed")
        return azure_config
    except ValidationError as e:
        logger.error(f"✗ Configuration validation failed: {e}")
        raise
```

## Error Handling Patterns

### 1. Graceful Degradation

Handle failures gracefully:

```python
async def robust_ensemble_execution(config_id: str, variables: dict):
    """Execute ensemble with multiple fallback strategies."""

    # Strategy 1: Full ensemble
    try:
        result = await ensemble_use_case.execute_ensemble(config_id, variables)
        if result.success_rate >= 0.8:
            return result
        logger.warning(f"Low success rate: {result.success_rate:.1%}")
    except Exception as e:
        logger.error(f"Full ensemble failed: {e}")

    # Strategy 2: Reduced ensemble
    try:
        reduced_config = await create_reduced_ensemble(config_id)
        result = await ensemble_use_case.execute_ensemble(reduced_config.config_id, variables)
        if result.success_rate >= 0.6:
            return result
    except Exception as e:
        logger.error(f"Reduced ensemble failed: {e}")

    # Strategy 3: Single agent fallback
    try:
        result = await single_agent_analysis(variables)
        return result
    except Exception as e:
        logger.error(f"Single agent fallback failed: {e}")
        raise IngeniousError("All execution strategies failed")
```

### 2. Circuit Breaker Pattern

Prevent cascading failures:

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
azure_openai_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=300)

async def protected_llm_call(messages):
    return await azure_openai_breaker.call(
        openai_service.generate_response,
        messages
    )
```

### 3. Retry Strategies

Implement intelligent retry logic:

```python
import asyncio
import random
from typing import Callable, Any

class RetryStrategy:
    @staticmethod
    async def exponential_backoff(
        func: Callable,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True
    ) -> Any:
        """Retry with exponential backoff."""

        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries:
                    raise

                # Calculate delay
                delay = min(base_delay * (2 ** attempt), max_delay)

                # Add jitter to prevent thundering herd
                if jitter:
                    delay *= (0.5 + random.random() * 0.5)

                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                await asyncio.sleep(delay)

# Usage
async def resilient_ensemble_execution():
    return await RetryStrategy.exponential_backoff(
        lambda: ensemble_use_case.execute_ensemble(config_id, variables),
        max_retries=3,
        base_delay=2.0
    )
```

## Testing Strategies

### 1. Unit Testing

Test individual components:

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_ensemble_configuration_creation():
    # Arrange
    mock_llm_service = AsyncMock()
    mock_storage_service = AsyncMock()

    ensemble_use_case = EnsembleManagementUseCase(
        llm_service=mock_llm_service,
        storage_service=mock_storage_service
    )

    # Act
    config = await ensemble_use_case.create_ensemble_configuration(
        name="test_ensemble",
        description="Test ensemble",
        main_prompt_template="Test {{ topic }}",
        sub_prompt_templates=[
            {"name": "analyzer", "content": "Analyze {{ topic }}", "role": "analyzer"}
        ],
        reduce_prompt_template="Synthesize: {{ analyzer }}"
    )

    # Assert
    assert config.name == "test_ensemble"
    assert len(config.sub_prompt_templates) == 1
    assert config.strategy == EnsembleStrategy.PARALLEL
```

### 2. Integration Testing

Test service integrations:

```python
@pytest.mark.asyncio
async def test_azure_openai_integration():
    # Use test Azure OpenAI resource
    service = AzureOpenAIService(
        azure_endpoint=os.getenv("TEST_AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("TEST_AZURE_OPENAI_API_KEY"),
        api_version="2024-06-01",
        model="gpt-3.5-turbo"
    )

    response = await service.generate_response([
        {"role": "user", "content": "Hello, test!"}
    ])

    assert response.content is not None
    assert len(response.content) > 0
```

### 3. Mock Testing

Test with mock services:

```python
class MockOpenAIService:
    async def generate_response(self, messages, **kwargs):
        # Return predictable mock response
        return ChatCompletionMessage(
            role="assistant",
            content=f"Mock response for: {messages[-1]['content']}"
        )

@pytest.mark.asyncio
async def test_ensemble_execution_with_mocks():
    mock_llm = MockOpenAIService()
    mock_storage = AsyncMock()

    ensemble_use_case = EnsembleManagementUseCase(
        llm_service=mock_llm,
        storage_service=mock_storage
    )

    # Test execution logic without external dependencies
    result = await ensemble_use_case.execute_ensemble(
        config_id="test_config",
        variables={"topic": "testing"}
    )

    assert result.success_rate == 1.0
    assert "Mock response" in result.final_result
```

## Monitoring and Observability

### 1. Structured Logging

Use structured logging for better observability:

```python
import structlog

logger = structlog.get_logger()

async def execute_ensemble_with_logging(config_id: str, variables: dict):
    execution_id = str(uuid4())

    logger.info(
        "ensemble_execution_started",
        execution_id=execution_id,
        config_id=config_id,
        variable_count=len(variables)
    )

    start_time = time.time()

    try:
        result = await ensemble_use_case.execute_ensemble(config_id, variables)

        logger.info(
            "ensemble_execution_completed",
            execution_id=execution_id,
            duration=time.time() - start_time,
            success_rate=result.success_rate,
            agent_count=len(result.agent_executions),
            token_usage=result.total_token_usage
        )

        return result

    except Exception as e:
        logger.error(
            "ensemble_execution_failed",
            execution_id=execution_id,
            duration=time.time() - start_time,
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

### 2. Metrics Collection

Collect custom metrics:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
ensemble_executions_total = Counter(
    'ensemble_executions_total',
    'Total ensemble executions',
    ['config_id', 'status']
)

ensemble_duration_seconds = Histogram(
    'ensemble_duration_seconds',
    'Ensemble execution duration',
    ['config_id']
)

active_ensemble_executions = Gauge(
    'active_ensemble_executions',
    'Currently active ensemble executions'
)

class MetricsCollector:
    @staticmethod
    def record_ensemble_execution(config_id: str, duration: float, success: bool):
        status = 'success' if success else 'failure'
        ensemble_executions_total.labels(config_id=config_id, status=status).inc()
        ensemble_duration_seconds.labels(config_id=config_id).observe(duration)

    @staticmethod
    def execution_started():
        active_ensemble_executions.inc()

    @staticmethod
    def execution_finished():
        active_ensemble_executions.dec()
```

### 3. Health Checks

Implement comprehensive health checks:

```python
from ingenious.diagnostics.application.services import HealthService

class HealthMonitor:
    def __init__(self, health_service: HealthService):
        self.health_service = health_service

    async def check_system_health(self) -> dict:
        """Comprehensive health check."""
        health_status = {
            "overall": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "metrics": {}
        }

        # Check Azure services
        azure_health = await self.health_service.check_azure_services()
        health_status["services"]["azure"] = azure_health

        # Check system metrics
        metrics = await self.health_service.get_metrics()
        health_status["metrics"] = {
            "memory_usage": metrics.memory_usage_percent,
            "cpu_usage": metrics.cpu_usage_percent,
            "disk_usage": metrics.disk_usage_percent
        }

        # Determine overall health
        if any(service["status"] != "healthy" for service in azure_health.values()):
            health_status["overall"] = "degraded"

        if metrics.memory_usage_percent > 90 or metrics.cpu_usage_percent > 90:
            health_status["overall"] = "degraded"

        return health_status
```

These best practices will help you build robust, secure, and maintainable applications with the Ingenious framework. For specific implementation examples, see the [Examples](examples/) directory.
