# Configuration Guide

Ingenious provides flexible configuration options through environment variables, configuration files, and programmatic APIs. This guide covers all configuration methods and options.

## Configuration Methods

### 1. Environment Variables (Recommended for Production)

The simplest way to configure Ingenious is through environment variables:

```bash
# Core Application Settings
export INGENIOUS_WORKING_DIR="/path/to/your/project"
export INGENIOUS_ENV="production"
export INGENIOUS_DEBUG="false"
export INGENIOUS_LOG_LEVEL="INFO"

# Azure OpenAI Configuration
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_API_VERSION="2024-06-01"
export AZURE_OPENAI_MODEL="gpt-4"

# Azure Blob Storage
export AZURE_STORAGE_ACCOUNT_URL="https://youraccount.blob.core.windows.net"
export AZURE_STORAGE_CREDENTIAL="your-access-key"
export AZURE_STORAGE_CONTAINER="ingenious-data"

# Azure SQL Database
export AZURE_SQL_SERVER="your-server.database.windows.net"
export AZURE_SQL_DATABASE="ingenious-db"
export AZURE_SQL_USERNAME="your-username"
export AZURE_SQL_PASSWORD="your-password"
```

### 2. Configuration Files

Create a `config.yaml` or `config.json` file in your project directory:

#### YAML Configuration

```yaml
# config.yaml
application:
  name: "My Ingenious App"
  version: "1.0.0"
  environment: "production"
  debug: false
  log_level: "INFO"

azure:
  openai:
    endpoint: "https://your-resource.openai.azure.com"
    api_key: "your-api-key"
    api_version: "2024-06-01"
    model: "gpt-4"
    temperature: 0.2
    max_tokens: 2048

  storage:
    account_url: "https://youraccount.blob.core.windows.net"
    credential: "your-access-key"
    container: "ingenious-data"

  sql:
    server: "your-server.database.windows.net"
    database: "ingenious-db"
    username: "your-username"
    password: "your-password"
    driver: "ODBC Driver 18 for SQL Server"

ensemble_defaults:
  strategy: "parallel"
  max_concurrent_agents: 5
  timeout_seconds: 300
  retry_count: 3

features:
  content_moderation: true
  telemetry: true
  caching: true
```

#### JSON Configuration

```json
{
  "application": {
    "name": "My Ingenious App",
    "version": "1.0.0",
    "environment": "production",
    "debug": false,
    "log_level": "INFO"
  },
  "azure": {
    "openai": {
      "endpoint": "https://your-resource.openai.azure.com",
      "api_key": "your-api-key",
      "api_version": "2024-06-01",
      "model": "gpt-4"
    },
    "storage": {
      "account_url": "https://youraccount.blob.core.windows.net",
      "credential": "your-access-key",
      "container": "ingenious-data"
    }
  },
  "ensemble_defaults": {
    "strategy": "parallel",
    "max_concurrent_agents": 5,
    "timeout_seconds": 300
  }
}
```

### 3. Programmatic Configuration

Configure Ingenious directly in your Python code:

```python
from ingenious.configuration.application.services import ConfigurationService
from ingenious.configuration.domain.models import AppConfiguration

# Create configuration programmatically
config = AppConfiguration(
    name="My AI Application",
    version="1.0.0",
    environment="production",
    debug=False,
    log_level="INFO"
)

# Add Azure settings
config.set("azure.openai.endpoint", "https://your-resource.openai.azure.com")
config.set("azure.openai.api_key", "your-api-key")
config.set("azure.openai.model", "gpt-4")

# Configure ensemble defaults
config.set("ensemble.default_strategy", "parallel")
config.set("ensemble.max_agents", 5)
config.set("ensemble.timeout", 300)

# Initialize configuration service
config_service = ConfigurationService(config)
```

## Configuration Loading Priority

Ingenious loads configuration in the following order (later sources override earlier ones):

1. **Default values** (built into the framework)
2. **Configuration files** (`config.yaml`, `config.json`)
3. **Environment variables**
4. **Programmatic configuration** (runtime)
5. **Command-line arguments** (CLI only)

## Configuration Sections

### Application Settings

```yaml
application:
  name: "My Ingenious App"          # Application name
  version: "1.0.0"                  # Version identifier
  environment: "production"         # Environment (development/staging/production)
  debug: false                      # Enable debug mode
  log_level: "INFO"                # Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
  working_dir: "/app/data"         # Working directory for file operations
  secret_key: "your-secret-key"    # Secret key for encryption/signing
```

### Azure OpenAI Configuration

```yaml
azure:
  openai:
    endpoint: "https://your-resource.openai.azure.com"  # Azure OpenAI endpoint
    api_key: "your-api-key"                             # API key or use managed identity
    api_version: "2024-06-01"                           # API version
    model: "gpt-4"                                      # Default model
    temperature: 0.2                                    # Default temperature (0.0-2.0)
    max_tokens: 2048                                    # Default max tokens
    top_p: 1.0                                         # Top-p sampling
    frequency_penalty: 0.0                             # Frequency penalty
    presence_penalty: 0.0                              # Presence penalty
    request_timeout: 30                                # Request timeout in seconds
    max_retries: 3                                     # Maximum retry attempts
    retry_delay: 1.0                                   # Delay between retries
```

### Azure Storage Configuration

```yaml
azure:
  storage:
    account_url: "https://youraccount.blob.core.windows.net"  # Storage account URL
    credential: "your-access-key"                             # Access key, SAS token, or managed identity
    container: "ingenious-data"                               # Default container name
    blob_prefix: "ensembles/"                                 # Prefix for blob paths
    timeout: 30                                               # Operation timeout
    max_retries: 3                                           # Maximum retry attempts
    chunk_size: 4194304                                      # Upload chunk size (4MB)
```

### Azure SQL Configuration

```yaml
azure:
  sql:
    server: "your-server.database.windows.net"         # SQL server hostname
    database: "ingenious-db"                           # Database name
    username: "your-username"                          # Username (or use managed identity)
    password: "your-password"                          # Password
    driver: "ODBC Driver 18 for SQL Server"           # ODBC driver
    connection_timeout: 30                             # Connection timeout
    command_timeout: 300                               # Command timeout
    pool_size: 10                                      # Connection pool size
    max_overflow: 20                                   # Maximum pool overflow
    encrypt: true                                      # Enable encryption
    trust_server_certificate: false                   # Trust server certificate
```

### Ensemble Defaults

```yaml
ensemble_defaults:
  strategy: "parallel"              # Default execution strategy (parallel/sequential/hierarchical)
  max_concurrent_agents: 5          # Maximum concurrent agents
  timeout_seconds: 300              # Default timeout for ensemble execution
  retry_count: 3                    # Number of retries for failed agents
  temperature: 0.2                  # Default LLM temperature
  max_tokens: 2048                  # Default max tokens per agent
  enable_monitoring: true           # Enable execution monitoring
  save_intermediate_results: false  # Save individual agent results
```

### Feature Flags

```yaml
features:
  content_moderation: true          # Enable Azure Content Moderator integration
  telemetry: true                   # Enable Application Insights telemetry
  caching: true                     # Enable response caching
  rate_limiting: true               # Enable rate limiting
  health_checks: true               # Enable health check endpoints
  metrics_collection: true         # Enable metrics collection
  audit_logging: true              # Enable audit logging
```

### Security Settings

```yaml
security:
  authentication:
    enabled: true                   # Enable authentication
    provider: "azure_ad"           # Authentication provider
    tenant_id: "your-tenant-id"   # Azure AD tenant ID
    client_id: "your-client-id"   # Azure AD client ID

  authorization:
    enabled: true                   # Enable authorization
    default_role: "user"           # Default user role
    admin_users:                   # List of admin users
      - "admin@company.com"

  encryption:
    enabled: true                   # Enable data encryption
    key_vault_url: "https://your-keyvault.vault.azure.net"  # Key Vault URL
    key_name: "ingenious-encryption-key"                    # Encryption key name
```

## Environment-Specific Configuration

### Development Configuration

```yaml
# config.development.yaml
application:
  environment: "development"
  debug: true
  log_level: "DEBUG"

azure:
  openai:
    endpoint: "http://localhost:5001"  # Mock OpenAI service
    api_key: "mock-key"

  storage:
    account_url: "http://localhost:5002"  # Mock storage service
    credential: "mock-credential"

features:
  content_moderation: false         # Disable in development
  telemetry: false                 # Disable telemetry
```

### Production Configuration

```yaml
# config.production.yaml
application:
  environment: "production"
  debug: false
  log_level: "WARNING"

azure:
  openai:
    endpoint: "https://prod-openai.openai.azure.com"
    # Use managed identity (no API key)

  storage:
    account_url: "https://prodstg.blob.core.windows.net"
    # Use managed identity (no credential)

security:
  authentication:
    enabled: true
  authorization:
    enabled: true
  encryption:
    enabled: true

features:
  content_moderation: true
  telemetry: true
  audit_logging: true
```

## Configuration Validation

Ingenious automatically validates configuration at startup:

```python
from ingenious.configuration.application.services import ConfigurationService

# Validate configuration
try:
    config_service = ConfigurationService.from_file("config.yaml")
    await config_service.validate()
    print("✓ Configuration is valid")
except ValidationError as e:
    print(f"✗ Configuration error: {e}")
```

### Manual Validation

```bash
# Validate configuration using CLI
ingen config validate

# Validate specific configuration file
ingen config validate --config custom-config.yaml

# Show validation details
ingen config validate --verbose
```

## Configuration Management

### View Current Configuration

```python
# Programmatically
config = await config_service.get_current_config()
print(config.dict())

# CLI
ingen config show
ingen config show --section azure.openai
```

### Update Configuration

```python
# Programmatically
await config_service.update_setting("azure.openai.model", "gpt-4-turbo")

# CLI
ingen config set azure.openai.model gpt-4-turbo
```

### Reset Configuration

```python
# Reset to defaults
await config_service.reset_to_defaults()

# CLI
ingen config reset
igen config reset --section azure
```

## Configuration Templates

### Minimal Configuration

For simple use cases:

```yaml
# minimal-config.yaml
azure:
  openai:
    endpoint: "https://your-resource.openai.azure.com"
    api_key: "your-api-key"
    model: "gpt-4"
```

### Full Production Configuration

Complete production-ready configuration:

```yaml
# production-config.yaml
application:
  name: "Production Ingenious App"
  environment: "production"
  log_level: "WARNING"

azure:
  openai:
    endpoint: "https://prod-openai.openai.azure.com"
    api_version: "2024-06-01"
    model: "gpt-4"
    temperature: 0.1
    request_timeout: 45
    max_retries: 5

  storage:
    account_url: "https://prodstg.blob.core.windows.net"
    container: "ingenious-prod"
    timeout: 60

  sql:
    server: "prod-sql.database.windows.net"
    database: "ingenious-prod"
    connection_timeout: 30
    pool_size: 20

ensemble_defaults:
  strategy: "parallel"
  max_concurrent_agents: 10
  timeout_seconds: 600
  retry_count: 5

security:
  authentication:
    enabled: true
    provider: "azure_ad"
  authorization:
    enabled: true
  encryption:
    enabled: true

features:
  content_moderation: true
  telemetry: true
  caching: true
  health_checks: true
  metrics_collection: true
  audit_logging: true
```

## Configuration Best Practices

### 1. Use Environment Variables for Secrets

Never store secrets in configuration files:

```yaml
# ✗ Don't do this
azure:
  openai:
    api_key: "sk-actual-api-key-here"

# ✓ Do this instead
azure:
  openai:
    api_key: "${AZURE_OPENAI_API_KEY}"
```

### 2. Environment-Specific Configurations

Use separate configuration files for different environments:

```
configs/
  ├── config.base.yaml      # Common settings
  ├── config.development.yaml
  ├── config.staging.yaml
  └── config.production.yaml
```

### 3. Validate Configuration Early

Always validate configuration at application startup:

```python
async def startup():
    try:
        await config_service.validate()
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        sys.exit(1)
```

### 4. Use Managed Identity in Production

Avoid API keys and passwords in production:

```yaml
# Production configuration with managed identity
azure:
  openai:
    endpoint: "https://prod-openai.openai.azure.com"
    # No api_key - uses managed identity

  storage:
    account_url: "https://prodstg.blob.core.windows.net"
    # No credential - uses managed identity
```

### 5. Monitor Configuration Changes

Log configuration changes for audit purposes:

```python
@config_service.on_config_change
async def log_config_change(key: str, old_value: Any, new_value: Any):
    logger.info(f"Configuration changed: {key} = {new_value}")
```

## Troubleshooting Configuration

### Common Issues

**Configuration File Not Found**
```bash
# Check file path and permissions
ls -la config.yaml
ingen config validate --config config.yaml
```

**Environment Variable Not Set**
```bash
# Check environment variables
echo $AZURE_OPENAI_API_KEY
env | grep AZURE
```

**Validation Errors**
```bash
# Get detailed validation information
ingen config validate --verbose
```

**Permission Errors**
```bash
# Check Azure permissions
az account show
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

For more troubleshooting help, see the [Troubleshooting Guide](troubleshooting.md).
