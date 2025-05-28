# Configuration Guide

This document explains how to configure Insight Ingenious for your needs.

## Configuration Files

Insight Ingenious uses two main configuration files:

1. **config.yml** - Main application configuration
2. **profiles.yml** - Sensitive information like API keys

### Configuration Locations

- **config.yml**: By default, this file should be in your project's root directory
- **profiles.yml**: By default, this file is located at `~/.ingenious/profiles.yml`

### Environment Variables

You can override the config paths using environment variables:

- `INGENIOUS_PROJECT_PATH`: Path to your project's configuration file
- `INGENIOUS_PROFILE_PATH`: Path to your profiles configuration file
- `INGENIOUS_WORKING_DIR`: Working directory for the application

## Main Configuration (config.yml)

The `config.yml` file contains the main configuration for your Insight Ingenious application. Here's a sample configuration with explanations:

```yaml
# General configuration
api_key: ""  # Your API key (if not using profiles)
profile: "default"  # The name of the profile to use from profiles.yml
log_level: "INFO"  # Log level: DEBUG, INFO, WARNING, ERROR

# Web server configuration
web_configuration:
  ip_address: "0.0.0.0"  # IP address to bind to
  port: 8000  # Port to listen on
  authentication:
    enabled: false  # Enable HTTP Basic Authentication
    username: "admin"  # Username for authentication
    password: "password"  # Password for authentication
  rate_limit:
    enabled: false  # Enable rate limiting
    requests_per_minute: 60  # Requests allowed per minute

# Database configuration
database:
  type: "sqlite"  # Database type: sqlite, cosmos
  connection_string: "conversations.db"  # Connection string or file path
  auto_create: true  # Automatically create the database

# File storage configuration
file_storage:
  type: "local"  # Storage type: local, azure_blob
  path: "files"  # Path for local storage

# ChainLit configuration
chainlit_configuration:
  enable: true  # Enable ChainLit web interface

# Agent configuration
agents:
  - name: "default_agent"  # Name of the agent
    model_config:
      model: "gpt-4o"  # Model to use
      temperature: 0.7  # Temperature for generation
      max_tokens: 1000  # Maximum tokens to generate
    system_prompt: "You are a helpful assistant."  # System prompt for the agent

# Conversation flows
conversation_flows:
  - name: "default"  # Name of the flow
    description: "Default conversation flow"  # Description
    chat_service: "basic"  # Service type: basic, multi_agent, router
    agents:
      - "default_agent"  # Agents to use in this flow

# Extensions configuration
extensions:
  enabled: true  # Enable extensions
  custom_routes: true  # Enable custom API routes
  custom_agents: true  # Enable custom agents
  custom_services: true  # Enable custom services
```

## Profile Configuration (profiles.yml)

The `profiles.yml` file contains sensitive information like API keys. This should be kept secure and not committed to version control.

```yaml
profiles:
  - name: "default"  # Profile name
    openai:
      api_key: "your_openai_api_key"  # OpenAI API key
      organization: "your_organization_id"  # Optional OpenAI organization ID
    azure_openai:
      api_key: "your_azure_openai_key"  # Azure OpenAI API key
      api_base: "your_azure_openai_endpoint"  # Azure OpenAI endpoint
    azure_storage:
      connection_string: "your_azure_storage_connection_string"  # For Azure Blob storage
    database:
      connection_string: "your_database_connection_string"  # Database connection string
```

## Configuration Options

### Agent Configuration

Agents can be configured with different models, prompts, and settings:

```yaml
agents:
  - name: "customer_service"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
      max_tokens: 1000
      top_p: 1.0
      frequency_penalty: 0.0
      presence_penalty: 0.0
    system_prompt: "You are a helpful customer service agent."
    functions:
      - name: "get_customer_info"
        description: "Get information about a customer"
        parameters: { ... }
```

### Conversation Flows

Conversation flows define how agents interact within a conversation:

```yaml
conversation_flows:
  - name: "customer_support"
    description: "Customer support conversation flow"
    chat_service: "multi_agent"
    agents:
      - "customer_service"
      - "technical_support"
    routing:
      default: "customer_service"
      rules:
        - pattern: "technical|error|bug"
          agent: "technical_support"
```

### Database Configuration

Configure different database backends:

```yaml
database:
  type: "sqlite"  # Or "cosmos"
  connection_string: "conversations.db"
  auto_create: true
  pool_size: 5
  timeout: 30
```

### File Storage Configuration

Configure file storage options:

```yaml
file_storage:
  type: "local"  # Or "azure_blob"
  path: "files"  # For local storage
  azure:
    container_name: "ingenious-files"  # For Azure Blob storage
```

## Using Azure Key Vault

For enhanced security, you can store sensitive information in Azure Key Vault:

```yaml
key_vault:
  enabled: true
  name: "your-key-vault-name"
  keys:
    - name: "openai-api-key"
      config_path: "profiles[0].openai.api_key"
    - name: "database-connection-string"
      config_path: "profiles[0].database.connection_string"
```

Set the environment variable `KEY_VAULT_NAME` to your Key Vault name:

```bash
export KEY_VAULT_NAME=your-key-vault-name
```

## CLI Configuration

Configure CLI behavior in the configuration:

```yaml
cli:
  default_log_level: "INFO"
  rich_console: true
  progress_bar: true
```

## Advanced Configuration

### Content Filtering

Enable content filtering to prevent inappropriate content:

```yaml
content_filtering:
  enabled: true
  sensitivity: "medium"  # "low", "medium", "high"
  action: "block"  # "block", "flag", "ignore"
```

### Custom Templates

Configure custom prompt templates:

```yaml
templates:
  path: "templates"
  default_extension: ".j2"
  cache: true
```

### Logging Configuration

Configure detailed logging:

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "ingenious.log"
  rotation: true
  max_size: 10485760  # 10 MB
  backup_count: 5
```

## Environment-specific Configuration

You can create environment-specific configurations using profiles:

```yaml
profiles:
  - name: "development"
    # Development settings
  - name: "production"
    # Production settings
```

Then specify which profile to use:

```yaml
profile: "development"  # Or "production"
```

## Configuration Validation

The configuration is validated using Pydantic models to ensure all required fields are present and have the correct types. If configuration errors are found, detailed error messages will be displayed.
