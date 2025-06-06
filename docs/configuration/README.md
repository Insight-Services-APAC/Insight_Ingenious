# Configuration Guide

This guide explains how to configure Insight Ingenious for your project.

## Configuration Overview

Insight Ingenious uses a two-file configuration approach:

1. `config.yml`: Project-specific, non-sensitive configuration
2. `profiles.yml`: Environment-specific, sensitive configuration (API keys, credentials)

## Setting Up Configuration Files

### Initial Setup

When you run `ingen_cli initialize-new-project`, template configuration files are generated:

- `config.yml` in your project directory
- `profiles.yml` in `~/.ingenious/` directory

### Environment Variables

Set these environment variables to specify configuration locations:

- `INGENIOUS_PROJECT_PATH`: Path to your project's `config.yml`
- `INGENIOUS_PROFILE_PATH`: Path to your `profiles.yml`

Alternatively, for Azure deployments:
- `APPSETTING_INGENIOUS_CONFIG`: JSON configuration string
- `APPSETTING_INGENIOUS_PROFILE`: JSON profile string

## Configuration File Structure

### config.yml

```yaml
chat_history:
  database_type: "sqlite"  # or "cosmos"
  database_name: "chat_history"
  memory_path: "./tmp"

profile: "development"  # Name of the profile to use from profiles.yml

models:
  - model: "gpt-4"
    deployment_name: "gpt4"
  - model: "gpt-3.5-turbo"
    deployment_name: "gpt35turbo"

logging:
  root_log_level: "INFO"
  log_level: "DEBUG"

tool_service:
  enable: true

chat_service:
  type: "multi_agent"  # The type of chat service to use

chainlit_configuration:
  enable: true

azure_search_services:
  - service: "knowledge-base"
    endpoint: "https://your-search-service.search.windows.net"

web_configuration:
  authentication:
    type: "basic"
    enable: true

local_sql_db:
  connection_string: "sqlite:///sample.db"

azure_sql_services:
  database_name: "your_database"
  table_name: "your_table"

file_storage:
  enable: true
  storage_type: "local"  # or "azure"
  path: "./files"
```

### profiles.yml

```yaml
- name: "development"
  models:
    - model: "gpt-4"
      api_key: "your-api-key"
      base_url: "https://your-openai-endpoint.openai.azure.com"
    - model: "gpt-3.5-turbo"
      api_key: "your-api-key"
      base_url: "https://your-openai-endpoint.openai.azure.com"

  chat_history:
    database_connection_string: ""

  azure_search_services:
    - service: "knowledge-base"
      key: "your-search-key"

  azure_sql_services:
    database_connection_string: ""

  web_configuration:
    authentication:
      username: "admin"
      password: "your-secure-password"

  receiver_configuration:
    enable: false
    api_url: ""
    api_key: ""

  chainlit_configuration:
    authentication:
      enable: false
      github_client_id: ""
      github_secret: ""

  file_storage:
    enable: true
    storage_type: "local"
    container_name: ""
```

## Configuration Options Explained

### Chat History

Controls how conversation history is stored:

```yaml
chat_history:
  database_type: "sqlite"  # Options: "sqlite", "cosmos"
  database_name: "chat_history"
  memory_path: "./tmp"  # Where context memory files are stored
```

### Models

Configures LLM models:

```yaml
models:
  - model: "gpt-4"  # Model identifier
    deployment_name: "gpt4"  # Azure OpenAI deployment name
```

In `profiles.yml`:

```yaml
models:
  - model: "gpt-4"
    api_key: "your-api-key"  # OpenAI or Azure OpenAI API key
    base_url: "https://your-endpoint.openai.azure.com"  # API endpoint
```

### Logging

Controls logging levels:

```yaml
logging:
  root_log_level: "INFO"  # Global logging level
  log_level: "DEBUG"  # Application-specific logging level
```

### Chat Service

Specifies the chat service implementation:

```yaml
chat_service:
  type: "multi_agent"  # The conversation service to use
```

### Chainlit Configuration

Controls the web UI:

```yaml
chainlit_configuration:
  enable: true  # Whether to enable the Chainlit UI
```

In `profiles.yml`:

```yaml
chainlit_configuration:
  authentication:
    enable: false  # Whether to require authentication
    github_client_id: ""  # For GitHub OAuth
    github_secret: ""  # For GitHub OAuth
```

### Azure Search Services

Configures Azure Cognitive Search for knowledge bases:

```yaml
azure_search_services:
  - service: "knowledge-base"  # Service identifier
    endpoint: "https://your-search-service.search.windows.net"
```

In `profiles.yml`:

```yaml
azure_search_services:
  - service: "knowledge-base"
    key: "your-search-key"  # Azure Search API key
```

### Web Configuration

Controls API authentication:

```yaml
web_configuration:
  authentication:
    type: "basic"  # Authentication type
    enable: true  # Whether authentication is required
```

In `profiles.yml`:

```yaml
web_configuration:
  authentication:
    username: "admin"  # Basic auth username
    password: "your-secure-password"  # Basic auth password
```

### File Storage

Configures file storage:

```yaml
file_storage:
  enable: true
  storage_type: "local"  # Options: "local", "azure"
  path: "./files"  # Local storage path
```

For Azure Blob Storage:

```yaml
file_storage:
  enable: true
  storage_type: "azure"
  container_name: "your-container"
```

## Multiple Environments

You can define multiple profiles in `profiles.yml` for different environments:

```yaml
- name: "development"
  # Development settings

- name: "production"
  # Production settings
```

Then specify which profile to use in `config.yml`:

```yaml
profile: "development"  # or "production"
```
