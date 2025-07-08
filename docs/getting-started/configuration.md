---
title: "⚙️ Configuration Guide"
layout: single
permalink: /getting-started/configuration/
sidebar:
  nav: "docs"
toc: true
toc_label: "Configuration Options"
toc_icon: "cogs"
---

# Configuration Guide

This guide explains how to configure Insight Ingenious - an enterprise-grade Python library for AI agent APIs - for your specific deployment and Microsoft Azure service integrations. The library provides comprehensive configuration options for enterprise environments, debugging tools, and customization requirements.

## Configuration Overview

Insight Ingenious uses a two-file configuration approach:

1. `config.yml`: Project-specific, non-sensitive configuration
2. `profiles.yml`: Environment-specific, sensitive configuration (API keys, credentials)

## Setting Up Configuration Files

### Initial Setup

When you run `ingen init`, template configuration files are generated:

- `config.yml` and `profiles.yml` in your project directory

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
  database_type: "sqlite"  # or "azuresql"
  database_path: "./.tmp/high_level_logs.db"  # Path to SQLite database file
  database_name: "chat_history"  # Name of the database (used for Azure SQL)
  memory_path: "./.tmp"  # Location for temporary memory/cache files (used by ChromaDB)

profile: "dev"  # Name of the profile to use from profiles.yml

models:
  - model: "gpt-4.1-nano"
    api_type: "azure"
    api_version: "2024-12-01-preview"

logging:
  root_log_level: "debug"
  log_level: "debug"

tool_service:
  enable: false

chat_service:
  type: "multi_agent"  # The type of chat service to use

chainlit_configuration:
  enable: false

azure_search_services:
  - service: "default"
    endpoint: "https://your-search-service.search.windows.net"

azure_sql_services:
  database_name: "dbo"
  table_name: "sample_table"

web_configuration:
  type: "fastapi"
  ip_address: "0.0.0.0"
  port: 80
  authentication:
    type: "basic"
    enable: true

local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./ingenious/sample_dataset/cleaned_students_performance.csv"
  sample_database_name: "sample_data"

prompt_tuner:
  mode: "fast_api"  # Mount in fast_api or standalone flask

file_storage:
  revisions:
    enable: true
    storage_type: "local"
    container_name: "jrsrevisions"
    path: ".files"
    add_sub_folders: true
  data:
    enable: true
    storage_type: "local"
    container_name: "jrsdata"
    path: ".files"
    add_sub_folders: true
```

### profiles.yml

```yaml
- name: "dev"
  models:
    - model: "gpt-4.1-nano"
      api_key: "your-api-key"
      base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-12-01-preview"

  chat_history:
    database_connection_string: "AccountEndpoint=..."

  azure_search_services:
    - service: "default"
      key: "your-search-key"

  azure_sql_services:
    database_connection_string: ""

  receiver_configuration:
    enable: false
    api_url: "https://your-api.azurewebsites.net/api/ai-response/publish"
    api_key: "DevApiKey"

  chainlit_configuration:
    enable: false
    authentication:
      enable: false
      github_client_id: ""
      github_secret: ""

  web_configuration:
    authentication:
      enable: false
      username: "admin"
      password: "your-secure-password"

  file_storage:
    revisions:
      url: "https://your-storage.blob.core.windows.net/"
      authentication_method: "default_credential"  # or "msi"
    data:
      url: "https://your-storage.blob.core.windows.net/"
      authentication_method: "default_credential"  # or "msi"
```

## Configuration Options Explained

### Chat History

Controls how conversation history is stored. Ingenious supports both SQLite (development) and Azure SQL (production) for chat history storage.

```yaml
chat_history:
  database_type: "sqlite"  # Options: "sqlite", "azuresql"
  database_path: "./.tmp/high_level_logs.db"  # SQLite database file path
  database_name: "chat_history"  # Database name (used for Azure SQL)
  memory_path: "./.tmp"  # Path for context memory files (used by ChromaDB)
```

#### SQLite Setup (Development)

For development environments, use SQLite (default):

```yaml
# config.yml
chat_history:
  database_type: "sqlite"
  database_path: "./.tmp/high_level_logs.db"
  database_name: "chat_history"
```

No additional configuration required in `profiles.yml`.

#### Azure SQL Setup (Production)

For production environments, use Azure SQL Database:

**Step 1: Install Prerequisites**

On macOS:
```bash
# Install Microsoft ODBC Driver 18 for SQL Server
brew tap microsoft/mssql-release
brew install msodbcsql18 mssql-tools18

# Verify installation
odbcinst -q -d
```

On Ubuntu/Debian:
```bash
# Install Microsoft ODBC Driver 18 for SQL Server
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install msodbcsql18
```

On Windows:
Download and install the ODBC Driver 18 for SQL Server from the Microsoft website.

**Step 2: Configure Environment Variables**

Add the Azure SQL connection string to your `.env` file:

```bash
# .env
AZURE_SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

# Also required for sample data functionality
LOCAL_SQL_CSV_PATH=./sample_data.csv

# Azure OpenAI credentials (if not already set)
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_BASE_URL=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_MODEL_NAME=gpt-4.1-nano
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-nano
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

**Important Notes:**
- Use double quotes around the connection string to handle special characters
- Install `python-dotenv` dependency: `uv add python-dotenv`
- The connection string format is critical - ensure all parameters are correct

**Step 3: Update Configuration Files**

```yaml
# config.yml
chat_history:
  database_type: "azuresql"
  database_name: "your_database_name"
```

```yaml
# profiles.yml
chat_history:
  database_connection_string: ${AZURE_SQL_CONNECTION_STRING}
```

**Environment Variable Substitution:**
The `${VARIABLE_NAME}` syntax enables environment variable substitution in configuration files. This allows you to keep sensitive credentials in environment variables while referencing them in configuration.

**Step 4: Validate Configuration**

```bash
uv run ingen validate
```

The Azure SQL database tables will be automatically created by Ingenious when first accessed. The following tables are created:
- `chat_history` - Main conversation messages
- `chat_history_summary` - Memory/summary storage
- `users` - User management
- `threads` - Thread/conversation management
- `steps`, `elements`, `feedbacks` - Chainlit UI integration

**Security Note**: Always use environment variables for sensitive connection strings. Never commit database credentials to version control.

### Models

Configures LLM models:

```yaml
models:
  - model: "gpt-4.1-nano"  # Model identifier
    api_type: "azure"  # API type (azure, openai)
    api_version: "2024-12-01-preview"  # API version
```

In `profiles.yml`:

```yaml
models:
  - model: "gpt-4.1-nano"
    api_key: "your-api-key"  # OpenAI or Azure OpenAI API key
    base_url: "https://your-endpoint.openai.azure.com/openai/deployments/gpt-4.1-nano/chat/completions?api-version=2024-12-01-preview"  # API endpoint
```

### Logging

Controls logging levels:

```yaml
logging:
  root_log_level: "debug"  # Global logging level (debug, info, warning, error)
  log_level: "debug"  # Application-specific logging level
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
  - service: "default"  # Service identifier
    endpoint: "https://your-search-service.search.windows.net"
```

In `profiles.yml`:

```yaml
azure_search_services:
  - service: "default"
    key: "your-search-key"  # Azure Search API key
```

### Web Configuration

Controls API authentication and server settings:

```yaml
web_configuration:
  type: "fastapi"  # Web framework type
  ip_address: "0.0.0.0"  # IP address to bind to
  port: 80  # Port number
  authentication:
    type: "basic"  # Authentication type
    enable: true  # Whether authentication is required
```

In `profiles.yml`:

```yaml
web_configuration:
  authentication:
    enable: false  # Whether to enable authentication
    username: "admin"  # Basic auth username
    password: "your-secure-password"  # Basic auth password
```

### File Storage

Configures file storage with support for both local and Azure Blob Storage backends. This affects prompt template storage, memory management, and data persistence.

#### Local Storage Configuration

```yaml
file_storage:
  revisions:
    enable: true
    storage_type: "local"
    container_name: "revisions"  # Not used for local storage
    path: ".files"  # Local directory path
    add_sub_folders: true
  data:
    enable: true
    storage_type: "local"
    container_name: "data"  # Not used for local storage
    path: ".files"  # Local directory path
    add_sub_folders: true
```

#### Azure Blob Storage Configuration

```yaml
file_storage:
  revisions:
    enable: true
    storage_type: "azure"  # Use Azure Blob Storage
    container_name: "revisions"  # Azure container name
    path: "ingenious-files"  # Base path within container
    add_sub_folders: true
  data:
    enable: true
    storage_type: "azure"  # Use Azure Blob Storage
    container_name: "data"  # Azure container name
    path: "ingenious-files"  # Base path within container
    add_sub_folders: true
```

#### Azure Blob Storage profiles.yml Configuration

Configure authentication and connection details in `profiles.yml`:

```yaml
file_storage:
  revisions:
    url: "https://your-storage.blob.core.windows.net/"
    token: "${AZURE_STORAGE_CONNECTION_STRING:}"  # Connection string
    authentication_method: "token"  # Use connection string auth
  data:
    url: "https://your-storage.blob.core.windows.net/"
    token: "${AZURE_STORAGE_CONNECTION_STRING:}"  # Connection string
    authentication_method: "token"  # Use connection string auth
```

#### Authentication Methods

Azure Blob Storage supports multiple authentication methods:

1. **Connection String (Development)**:
   ```yaml
   authentication_method: "token"
   token: "DefaultEndpointsProtocol=https;AccountName=..."
   ```

2. **Managed Identity (Production)**:
   ```yaml
   authentication_method: "msi"
   client_id: "your-managed-identity-client-id"
   ```

3. **Service Principal**:
   ```yaml
   authentication_method: "client_id_and_secret"
   client_id: "your-app-registration-client-id"
   token: "your-client-secret"
   ```

4. **Default Azure Credential**:
   ```yaml
   authentication_method: "default_credential"
   ```

#### Environment Variables for Azure Blob Storage

Set these in your `.env` file:

```bash
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=ingendev;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net"
AZURE_STORAGE_ACCOUNT_NAME="ingendev"
AZURE_STORAGE_ACCOUNT_KEY="YOUR_ACCOUNT_KEY"
AZURE_STORAGE_REVISIONS_URL="https://ingendev.blob.core.windows.net"
AZURE_STORAGE_DATA_URL="https://ingendev.blob.core.windows.net"
```

#### Features Enabled by File Storage

- **Prompt Template Management**: Store and version prompt templates
- **Memory Management**: Persist conversation context across sessions
- **Data Persistence**: Store functional test outputs and analysis results
- **API Integration**: `/api/v1/prompts` routes for prompt management
- **Multi-Environment Support**: Same codebase works with local or cloud storage

For detailed setup instructions, see the [Azure Blob Storage Setup Guide](../guides/azure-blob-storage-setup.md).

### Local SQL Database

Configures local SQL database for testing and development:

```yaml
local_sql_db:
  database_path: "/tmp/sample_sql.db"  # Path to SQLite database
  sample_csv_path: "./ingenious/sample_dataset/cleaned_students_performance.csv"
  sample_database_name: "sample_data"
```

### Azure SQL Services

Configures Azure SQL Database:

```yaml
azure_sql_services:
  database_name: "dbo"  # Database name
  table_name: "sample_table"  # Table name
```

In `profiles.yml`:

```yaml
azure_sql_services:
  database_connection_string: "Server=..."  # Azure SQL connection string
```

### Prompt Tuner

Configures the prompt tuning interface:

```yaml
prompt_tuner:
  mode: "fast_api"  # Options: "fast_api", "flask"
```

### Receiver Configuration

Configures external API integration in `profiles.yml`:

```yaml
receiver_configuration:
  enable: false
  api_url: "https://your-api.azurewebsites.net/api/ai-response/publish"
  api_key: "DevApiKey"
```

## Multi-Agent Conversation Flows

Insight Ingenious supports several built-in conversation flows for different use cases:

### Available Conversation Flows

| Workflow | Description | External Services Required | Configuration Complexity | Availability |
|----------|-------------|----------------------------|--------------------------|--------------|
| `classification-agent` | Routes input to specialized agents | Azure OpenAI only | ✅ Minimal | Core library |
| `knowledge-base-agent` | Search knowledge bases | Azure OpenAI only (uses local ChromaDB) | ✅ Minimal | Core library (stable local implementation) |
| `sql-manipulation-agent` | Execute SQL queries | Azure OpenAI only (uses local SQLite) | ✅ Minimal | Core library (stable local implementation) |
| `bike-insights` | Sample domain-specific analysis | Azure OpenAI only | ✅ Minimal | Extension template* |

*Created when you run `ingen init` - part of project template, not core library.

> **Note**: Only local implementations (ChromaDB for knowledge-base-agent, SQLite for sql-manipulation-agent) are currently stable. Azure Search and Azure SQL integrations are experimental and may contain bugs.

### Workflow-Specific Configuration

#### 🚀 Quick Start: Minimal Configuration Workflows

For `classification-agent` and `bike-insights` (if created via `ingen init`), you only need basic Azure OpenAI setup:

```yaml
# config.yml
profile: dev
models:
  - model: ${AZURE_OPENAI_MODEL_NAME:gpt-4.1-nano}  # Environment variable substitution
    api_type: azure
    api_version: ${AZURE_OPENAI_API_VERSION:2024-12-01-preview}
    deployment: ${AZURE_OPENAI_DEPLOYMENT:gpt-4.1-nano}
chat_service:
  type: multi_agent
```

```yaml
# profiles.yml
- name: "dev"
  models:
    - model: "gpt-4.1-nano"
      api_key: "your-api-key"
      base_url: "https://your-endpoint.openai.azure.com/..."
```

#### 🔍 Knowledge Base Workflows

For `knowledge-base-agent`, the local ChromaDB implementation is used by default and is stable:

**Local ChromaDB Implementation (Recommended - Stable)**
```yaml
# No additional configuration needed!
# The knowledge-base-agent uses local ChromaDB storage automatically
# Simply add documents to: ./.tmp/knowledge_base/
```

**Experimental Azure Search (May contain bugs)**
```yaml
# config.yml (additional)
azure_search_services:
  - service: "default"
    endpoint: "https://your-search-service.search.windows.net"

# profiles.yml (additional)
azure_search_services:
  - service: "default"
    key: "your-search-key"
```

> **Recommendation**: Use the local ChromaDB implementation, which requires no additional configuration and is stable.

#### 📊 Database Workflows (SQL Manipulation Agent)

For `sql-manipulation-agent` workflow, you have two database options:

**Local SQLite (Recommended - Stable)**
```yaml
# config.yml
local_sql_db:
  database_path: "/tmp/sample_sql.db"
  sample_csv_path: "./data/your_data.csv"

# profiles.yml
azure_sql_services:
  database_name: "skip"  # This enables SQLite mode
```

**Experimental Azure SQL (May contain bugs)**
```yaml
# config.yml
azure_sql_services:
  database_name: "your_database"
  server_name: "your-server.database.windows.net"
  driver: "ODBC Driver 18 for SQL Server"

# profiles.yml
azure_sql_services:
  connection_string: "Driver={ODBC Driver 18 for SQL Server};Server=tcp:yourserver.database.windows.net,1433;Database=your_database;Uid=your_username;Pwd=your_password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
```

**Quick SQLite Setup:**
```bash
# Create sample database
uv run python -c "
from ingenious.utils.load_sample_data import sqlite_sample_db
sqlite_sample_db()
print('✅ Sample SQLite database created')
"

# Test SQL agent
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me all tables",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

> **Recommendation**: Use the local SQLite implementation, which is simpler to set up and stable.

> 📖 **For complete SQL agent setup instructions**, see the [SQL Agent Setup Guide](../guides/sql-agent-setup.md)

### Testing Workflows

Use the CLI to check requirements and test workflows:

```bash
# Check what configuration is needed
uv run ingen workflows knowledge-base-agent

# Test a workflow
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_prompt": "Hello", "conversation_flow": "classification-agent"}'
```

### Configuring Conversation Flows

The conversation flow is specified in the chat service configuration:

```yaml
chat_service:
  type: "multi_agent"  # Enables multi-agent conversation flows
```

Each conversation flow has its own directory structure under:
- `ingenious/services/chat_services/multi_agent/conversation_flows/`
- `ingenious/services/chat_services/multi_agent/conversation_patterns/`

### Custom Conversation Flows

You can create custom conversation flows by:

1. Creating a new directory under `conversation_flows/`
2. Implementing the `ConversationFlow` class with a `get_conversation_response()` method
3. Creating corresponding conversation patterns that define agent interactions
4. Registering the flow in your configuration

## Environment Variables
