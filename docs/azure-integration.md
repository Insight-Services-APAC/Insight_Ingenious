# Azure Integration

Ingenious provides comprehensive integration with Azure services, enabling production-ready AI applications with enterprise-grade security, scalability, and reliability.

## Supported Azure Services

### Azure OpenAI Service
- **Purpose**: LLM inference for prompt processing
- **Features**: GPT-4, GPT-3.5, embedding models
- **Integration**: Native async support with rate limiting

### Azure Blob Storage
- **Purpose**: Store conversation history, ensemble results, templates
- **Features**: Hierarchical storage, versioning, encryption
- **Integration**: Automatic serialization and metadata management

### Azure SQL Database
- **Purpose**: Structured data storage for configurations and analytics
- **Features**: Query optimization, connection pooling, migrations
- **Integration**: Async ORM with relationship mapping

### Azure Cognitive Services
- **Purpose**: Content moderation, translation, analysis
- **Features**: Multi-modal content processing
- **Integration**: Configurable content filtering and validation

## Azure OpenAI Configuration

### Basic Setup

```python
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService

# Configure Azure OpenAI service
openai_service = AzureOpenAIService(
    azure_endpoint="https://your-resource.openai.azure.com",
    api_key="your-api-key",
    api_version="2024-06-01",
    model="gpt-4"
)

# Test connection
response = await openai_service.generate_response([
    {"role": "user", "content": "Hello, Azure OpenAI!"}
])
print(response.content)
```

### Environment Configuration

```bash
# Azure OpenAI Settings
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_API_VERSION="2024-06-01"
export AZURE_OPENAI_MODEL="gpt-4"

# Optional: Model-specific settings
export AZURE_OPENAI_TEMPERATURE="0.2"
export AZURE_OPENAI_MAX_TOKENS="2048"
```

### Advanced Features

#### Multiple Model Support

```python
# Configure different models for different tasks
services = {
    "analysis": AzureOpenAIService(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-06-01",
        model="gpt-4"  # Complex analysis
    ),
    "summarization": AzureOpenAIService(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-06-01",
        model="gpt-3.5-turbo"  # Fast summarization
    )
}
```

#### Rate Limiting and Retry Logic

```python
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService

# Built-in rate limiting and retries
service = AzureOpenAIService(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version="2024-06-01",
    model="gpt-4",
    # Additional configuration options
    request_timeout=30,
    max_retries=3,
    retry_delay=1.0
)
```

#### Token Usage Monitoring

```python
# Monitor token usage across ensemble execution
async def monitor_token_usage():
    result = await ensemble_use_case.execute_ensemble(
        config_id="analysis-ensemble",
        variables={"topic": "AI governance"}
    )

    print(f"Total tokens used: {result.total_token_usage}")
    print(f"Average tokens per agent: {result.average_token_usage}")

    # Per-agent breakdown
    for execution in result.agent_executions:
        print(f"{execution.agent_role}: {execution.token_usage} tokens")
```

## Azure Blob Storage Integration

### Basic Configuration

```python
from ingenious.external_integrations.infrastructure.blob_storage_service import AzureBlobStorageService

# Configure Blob Storage
blob_service = AzureBlobStorageService(
    account_url="https://youraccount.blob.core.windows.net",
    credential="your-access-key"  # or managed identity
)
```

### Authentication Methods

#### Shared Access Key

```python
blob_service = AzureBlobStorageService(
    account_url="https://youraccount.blob.core.windows.net",
    credential="your-account-key"
)
```

#### Managed Identity (Recommended for Production)

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
blob_service = AzureBlobStorageService(
    account_url="https://youraccount.blob.core.windows.net",
    credential=credential
)
```

#### SAS Token

```python
blob_service = AzureBlobStorageService(
    account_url="https://youraccount.blob.core.windows.net",
    credential="your-sas-token"
)
```

### Storage Operations

#### Store Ensemble Results

```python
async def store_ensemble_results():
    # Execute ensemble
    result = await ensemble_use_case.execute_ensemble(
        config_id="market-analysis",
        variables={"company": "TechCorp", "market": "AI tools"}
    )

    # Automatically stored in blob storage
    # Format: ensembles/{config_id}/{execution_id}/result.json
    blob_path = f"ensembles/{result.config_id}/{result.execution_id}/result.json"

    # Results include metadata
    metadata = {
        "execution_date": result.executed_at.isoformat(),
        "success_rate": result.success_rate,
        "total_duration": result.total_duration_seconds,
        "agent_count": len(result.agent_executions)
    }

    print(f"Results stored at: {blob_path}")
```

#### Retrieve Historical Data

```python
async def retrieve_historical_results(config_id: str):
    # List all executions for a configuration
    executions = await blob_service.list_executions(config_id)

    for execution in executions:
        result = await blob_service.get_execution_result(
            config_id, execution.execution_id
        )
        print(f"Execution {execution.execution_id}: {result.success_rate:.1%} success")
```

#### Backup and Archive

```python
async def backup_configurations():
    # Export all ensemble configurations
    configs = await ensemble_use_case.list_configurations()

    for config in configs:
        backup_data = {
            "config": config.dict(),
            "created_at": config.created_at.isoformat(),
            "version": "1.0"
        }

        await blob_service.store_backup(
            f"backups/configs/{config.name}.json",
            backup_data
        )
```

## Azure SQL Database Integration

### Connection Configuration

```python
from ingenious.external_integrations.infrastructure.sql_service import AzureSQLService

# Configure SQL Database connection
sql_service = AzureSQLService(
    server="your-server.database.windows.net",
    database="ingenious-db",
    username="your-username",
    password="your-password",  # or use managed identity
    driver="ODBC Driver 18 for SQL Server"
)
```

### Environment Configuration

```bash
# Azure SQL Database Settings
export AZURE_SQL_SERVER="your-server.database.windows.net"
export AZURE_SQL_DATABASE="ingenious-db"
export AZURE_SQL_USERNAME="your-username"
export AZURE_SQL_PASSWORD="your-password"
export AZURE_SQL_DRIVER="ODBC Driver 18 for SQL Server"
```

### Data Storage Patterns

#### Ensemble Execution Tracking

```sql
-- Execution history table
CREATE TABLE ensemble_executions (
    execution_id UNIQUEIDENTIFIER PRIMARY KEY,
    config_id UNIQUEIDENTIFIER NOT NULL,
    config_name VARCHAR(255) NOT NULL,
    variables NVARCHAR(MAX), -- JSON
    started_at DATETIME2 NOT NULL,
    completed_at DATETIME2,
    success_rate DECIMAL(5,4),
    total_duration_seconds DECIMAL(10,3),
    total_tokens INT,
    error_message NVARCHAR(MAX),
    created_at DATETIME2 DEFAULT GETUTCDATE()
);

-- Agent execution details
CREATE TABLE agent_executions (
    agent_execution_id UNIQUEIDENTIFIER PRIMARY KEY,
    ensemble_execution_id UNIQUEIDENTIFIER NOT NULL,
    agent_role VARCHAR(50) NOT NULL,
    template_id UNIQUEIDENTIFIER NOT NULL,
    started_at DATETIME2,
    completed_at DATETIME2,
    duration_seconds DECIMAL(10,3),
    token_usage INT,
    success BIT NOT NULL,
    error_message NVARCHAR(MAX),
    FOREIGN KEY (ensemble_execution_id) REFERENCES ensemble_executions(execution_id)
);
```

#### Analytics and Reporting

```python
async def generate_performance_report():
    query = """
    SELECT
        config_name,
        COUNT(*) as execution_count,
        AVG(success_rate) as avg_success_rate,
        AVG(total_duration_seconds) as avg_duration,
        SUM(total_tokens) as total_tokens_used
    FROM ensemble_executions
    WHERE created_at >= DATEADD(day, -30, GETUTCDATE())
    GROUP BY config_name
    ORDER BY execution_count DESC
    """

    results = await sql_service.execute_query(query)
    return results
```

## Content Moderation with Azure Cognitive Services

### Configuration

```python
from ingenious.external_integrations.infrastructure.content_moderation_service import AzureContentModerationService

# Configure content moderation
moderation_service = AzureContentModerationService(
    endpoint="https://your-region.api.cognitive.microsoft.com",
    subscription_key="your-subscription-key"
)
```

### Automatic Content Filtering

```python
async def safe_ensemble_execution():
    # Content is automatically moderated before LLM processing
    result = await ensemble_use_case.execute_ensemble(
        config_id="content-analysis",
        variables={"content": user_provided_content}
    )

    # Check for content moderation flags
    if result.content_moderation_flags:
        print("Content moderation flags detected:")
        for flag in result.content_moderation_flags:
            print(f"- {flag.category}: {flag.severity}")
```

## Production Deployment Patterns

### High Availability Configuration

```python
# Multiple region configuration for high availability
from ingenious.configuration.application.services import ConfigurationService

config = {
    "azure_regions": {
        "primary": {
            "openai_endpoint": "https://eastus-openai.openai.azure.com",
            "storage_account": "https://eastusstorage.blob.core.windows.net",
            "sql_server": "eastus-sql.database.windows.net"
        },
        "secondary": {
            "openai_endpoint": "https://westus-openai.openai.azure.com",
            "storage_account": "https://westusstorage.blob.core.windows.net",
            "sql_server": "westus-sql.database.windows.net"
        }
    },
    "failover": {
        "enabled": True,
        "timeout_seconds": 30,
        "retry_attempts": 3
    }
}
```

### Security Best Practices

#### Managed Identity Setup

```python
# Use managed identity for production deployments
from azure.identity import ManagedIdentityCredential

# Configure managed identity
credential = ManagedIdentityCredential()

# All services use the same credential
openai_service = AzureOpenAIService(
    azure_endpoint=endpoint,
    credential=credential,  # Instead of API key
    api_version="2024-06-01",
    model="gpt-4"
)

blob_service = AzureBlobStorageService(
    account_url=storage_url,
    credential=credential
)
```

#### Key Vault Integration

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Retrieve secrets from Azure Key Vault
credential = DefaultAzureCredential()
secret_client = SecretClient(
    vault_url="https://your-keyvault.vault.azure.net",
    credential=credential
)

# Configure services with secrets
openai_api_key = secret_client.get_secret("openai-api-key").value
sql_password = secret_client.get_secret("sql-password").value
```

### Monitoring and Observability

#### Application Insights Integration

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

# Configure Application Insights
configure_azure_monitor(
    connection_string="InstrumentationKey=your-key;..."
)

tracer = trace.get_tracer(__name__)

# Trace ensemble executions
async def traced_ensemble_execution():
    with tracer.start_as_current_span("ensemble_execution") as span:
        span.set_attribute("config_id", config_id)
        span.set_attribute("variables", json.dumps(variables))

        result = await ensemble_use_case.execute_ensemble(
            config_id=config_id,
            variables=variables
        )

        span.set_attribute("success_rate", result.success_rate)
        span.set_attribute("duration", result.total_duration_seconds)

        return result
```

#### Custom Metrics

```python
# Track custom metrics for monitoring
async def log_ensemble_metrics(result):
    metrics = {
        "ensemble_duration": result.total_duration_seconds,
        "ensemble_success_rate": result.success_rate,
        "ensemble_token_usage": result.total_token_usage,
        "ensemble_agent_count": len(result.agent_executions)
    }

    # Send to Application Insights
    telemetry_client.track_event("ensemble_completed", properties=metrics)
```

## Cost Optimization

### Token Usage Optimization

```python
# Monitor and optimize token usage
async def cost_optimized_execution():
    # Use token estimation before execution
    estimated_tokens = await ensemble_use_case.estimate_token_usage(
        config_id="analysis-ensemble",
        variables=variables
    )

    if estimated_tokens > 10000:  # Cost threshold
        # Use more efficient strategy or smaller models
        await ensemble_use_case.optimize_for_cost(config_id)

    result = await ensemble_use_case.execute_ensemble(
        config_id="analysis-ensemble",
        variables=variables
    )

    return result
```

### Storage Lifecycle Management

```python
# Implement storage lifecycle policies
storage_policies = {
    "hot_tier_days": 30,      # Recent results in hot tier
    "cool_tier_days": 90,     # Older results in cool tier
    "archive_tier_days": 365, # Very old results in archive
    "delete_after_days": 2555 # Legal retention period
}

await blob_service.configure_lifecycle_policy(storage_policies)
```

## Testing with Mock Services

For development and testing, Ingenious supports mock Azure services:

```python
# Use mock services for development
if environment == "development":
    openai_service = AzureOpenAIService(
        azure_endpoint="http://localhost:5001",  # Mock OpenAI
        api_key="mock-key",
        api_version="2024-06-01",
        model="gpt-4"
    )

    blob_service = AzureBlobStorageService(
        account_url="http://localhost:5002",  # Mock Blob Storage
        credential="mock-credential"
    )
```

See the [Development Setup Guide](development.md) for detailed mock service configuration.

## Troubleshooting

### Common Azure Integration Issues

#### Authentication Errors

```python
# Diagnose authentication issues
try:
    await openai_service.generate_response([{"role": "user", "content": "test"}])
except Exception as e:
    if "401" in str(e):
        print("Authentication failed - check API key or managed identity")
    elif "403" in str(e):
        print("Authorization failed - check RBAC permissions")
    elif "429" in str(e):
        print("Rate limited - implement backoff strategy")
```

#### Network Connectivity

```python
# Test network connectivity
async def test_azure_connectivity():
    services = {
        "OpenAI": openai_service,
        "Blob Storage": blob_service,
        "SQL Database": sql_service
    }

    for name, service in services.items():
        try:
            await service.health_check()
            print(f"✓ {name}: Connected")
        except Exception as e:
            print(f"✗ {name}: {e}")
```

For more troubleshooting guidance, see the [Troubleshooting Guide](troubleshooting.md).
