# Insight Ingenious

[![Version](https://img.shields.io/badge/version-0.2.1-blue.svg)](https://github.com/Insight-Services-APAC/ingenious)
[![Python](https://img.shields.io/badge/python-3.13+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An enterprise-grade Python framework for building AI agent workflows using Azure OpenAI and Microsoft's Autogen. Features multi-agent conversation flows, JWT authentication, and comprehensive Azure service integrations.

## Quick Start

Get up and running in 5 minutes with Azure OpenAI!

### Prerequisites
- Python 3.13 or higher (Note: Python 3.13+ requirement is strict due to dependency constraints)
- Azure OpenAI API credentials
- [uv package manager](https://docs.astral.sh/uv/)

### 5-Minute Setup

1. **Install and Initialize**:
    ```bash
    # Navigate to your desired project directory first
    cd /path/to/your/project

    # Choose installation based on features needed
    uv add ingenious[standard] # Most common: includes SQL agent support
    # OR
    uv add ingenious[azure-full] # Full Azure integration
    # OR
    uv add ingenious # Minimal installation

    # Dependencies are already included in the base package

    # Initialize project in the current directory
    uv run ingen init
    ```

2. **Configure Credentials**:
    Copy the example template and add your Azure OpenAI credentials:
    ```bash
    # Copy environment template (choose based on your needs)
    cp .env.example .env # Full configuration options
    # OR
    cp .env.development .env # Minimal development setup
    # OR
    cp .env.azure-full .env # Full Azure integration

    # Edit .env file with your actual credentials
    ```

    **Required configuration (add to .env file)**:
    ```bash
    # Model Configuration (only INGENIOUS_* variables are used by the system)
    INGENIOUS_MODELS__0__MODEL=gpt-4
    INGENIOUS_MODELS__0__API_TYPE=rest
    INGENIOUS_MODELS__0__API_VERSION=2024-12-01-preview
    INGENIOUS_MODELS__0__DEPLOYMENT=your-gpt4-deployment-name
    INGENIOUS_MODELS__0__API_KEY=your-actual-api-key-here
    INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/

    # Basic required settings
    INGENIOUS_CHAT_SERVICE__TYPE=multi_agent
    INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=sqlite
    INGENIOUS_CHAT_HISTORY__DATABASE_PATH=./.tmp/chat_history.db
    INGENIOUS_CHAT_HISTORY__MEMORY_PATH=./.tmp
    ```

3. **Validate Configuration**:
    ```bash
    uv run ingen validate  # Check configuration before starting
    ```

    > **⚠️ BREAKING CHANGE**: Ingenious now uses **pydantic-settings** for configuration via environment variables. Legacy YAML configuration files (`config.yml`, `profiles.yml`) are **no longer supported** and must be migrated to environment variables with `INGENIOUS_` prefixes. Use the migration script:
    > ```bash
    > python scripts/migrate_config.py --config config.yml --profile profiles.yml --output .env
    > ```

4. **Start the Server**:
    ```bash
    # Start server (default port 80, use --port to override)
    uv run ingen serve --port 8000

    # Additional options:
    # --host 0.0.0.0  # Bind host (default: 0.0.0.0)
    ```

5. **Verify Health**:
    ```bash
    # Check server health
    curl http://localhost:8000/api/v1/health
    ```

6. **Test with Core Workflows**:

    Create test files to avoid JSON escaping issues:
    ```bash
    # Create test files for each workflow
    echo '{"user_prompt": "Analyze this customer feedback: Great product", "conversation_flow": "classification-agent"}' > test_classification.json
    echo '{"user_prompt": "Search for documentation about setup", "conversation_flow": "knowledge-base-agent"}' > test_knowledge.json
    echo '{"user_prompt": "Show me all tables in the database", "conversation_flow": "sql-manipulation-agent"}' > test_sql.json

    # Test each workflow
    curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d @test_classification.json
    curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d @test_knowledge.json
    curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d @test_sql.json
    ```

That's it! You should see a JSON response with AI analysis of the input.

**Next Steps - Test Additional Workflows**:

7. **Test bike-insights Workflow (Requires `ingen init` first)**:

    The `bike-insights` workflow is part of the project template and must be initialized first:
    ```bash
    # First initialize project to get bike-insights workflow
    uv run ingen init

    # Create bike-insights test data file
    # Note: bike-insights requires JSON data in the user_prompt field (double-encoded JSON)
    cat > test_bike_insights.json << 'EOF'
    {
      "user_prompt": "{\"revision_id\": \"test-v1\", \"identifier\": \"test-001\", \"stores\": [{\"name\": \"Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"MB-TREK-2021-XC\", \"quantity_sold\": 2, \"sale_date\": \"2023-04-01\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 4.5, \"comment\": \"Great bike\"}}], \"bike_stock\": []}]}",
      "conversation_flow": "bike-insights"
    }
    EOF

    # Test bike-insights workflow
    curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d @test_bike_insights.json
    ```

**Important Notes**:
- **Core Library Workflows** (`classification-agent`, `knowledge-base-agent`, `sql-manipulation-agent`) are always available and accept simple text prompts
- **Template Workflows** like `bike-insights` require JSON-formatted data with specific fields and are only available after running `ingen init`
- The `bike-insights` workflow is the recommended "Hello World" example for new users

## Workflow Categories

Insight Ingenious provides multiple conversation workflows with different configuration requirements:

### Core Library Workflows (Always Available)
These workflows are built into the Ingenious library and available immediately:

- `classification-agent` - Route input to specialized agents based on content (Azure OpenAI only)
- `knowledge-base-agent` - Search knowledge bases using local ChromaDB (STABLE - recently fixed)
- `sql-manipulation-agent` - Execute SQL queries using local SQLite (STABLE - recently fixed)

> **Note**: Core workflows support both hyphenated (`classification-agent`) and underscored (`classification_agent`) naming formats for backward compatibility.

### Template Workflows (Created by `ingen init`)
These workflows are provided as examples in the project template when you run `ingen init`:

- `bike-insights` - Comprehensive bike sales analysis showcasing multi-agent coordination (**ONLY available after `ingen init`** - not included in the core library)

> **Important**: The `bike-insights` workflow is NOT part of the core library. It's a template example that's created when you initialize a new project with `ingen init`. This is the recommended "Hello World" example for learning how to build custom workflows.

### Configuration Requirements by Workflow
- **Minimal setup** (Azure OpenAI only): `classification-agent`, `bike-insights`
- **Local implementations** (STABLE): `knowledge-base-agent` (ChromaDB), `sql-manipulation-agent` (SQLite)
- **Azure integrations** (EXPERIMENTAL): Azure Search for knowledge base, Azure SQL for database queries

> **Important**: Local implementations (ChromaDB, SQLite) are stable and work out-of-the-box. Azure integrations are experimental and contain known bugs. For production use, stick with local implementations. Use `ingen workflows` to check configuration requirements for each workflow.

## Documentation

For detailed documentation, see the [docs](https://insight-services-apac.github.io/ingenious/).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](https://github.com/Insight-Services-APAC/ingenious/blob/main/CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms specified in the [LICENSE](https://github.com/Insight-Services-APAC/ingenious/blob/main/LICENSE) file.
