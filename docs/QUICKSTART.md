---
title: "⚡ Quick Start Guide"
layout: single
permalink: /quickstart/
sidebar:
  nav: "docs"
toc: true
toc_label: "Quick Start Steps"
toc_icon: "bolt"
---

## Quick Start

Get up and running in 5 minutes with Azure OpenAI!

### Prerequisites
- Python 3.13+
- Azure OpenAI API credentials
- [uv package manager](https://docs.astral.sh/uv/)

### 5-Minute Setup

1. **Install and Initialize**:
    ```bash
    # From your project directory
    uv add ingenious
    uv run ingen init
    ```

2. **Configure Credentials**:
    ```bash
    # Edit .env with your Azure OpenAI credentials
    cp .env.example .env
    nano .env  # Add AZURE_OPENAI_API_KEY and AZURE_OPENAI_BASE_URL
    ```

3. **Validate Setup** (Recommended):
    #### For Linux-based Environments
    ```bash
    export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
    export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
    uv run ingen validate  # Check configuration before starting
    ```

    #### For Windows-based Environments
    ```powershell
    $env:INGENIOUS_PROJECT_PATH = "{your_project_folder}/config.yml"
    $env:INGENIOUS_PROFILE_PATH = "{profile_folder_location}/profiles.yml"                        
    uv run ingen validate  # Check configuration before starting
    ```

4. **Start the Server**:
    ```bash
    uv run ingen serve
    ```

5. **Verify Health**:
    ```bash
    # Check server health
    curl http://localhost:80/api/v1/health
    ```

6. **Test the API**:
    ```bash
    # Test bike insights workflow (the "Hello World" of Ingenious)
    curl -X POST http://localhost:80/api/v1/chat \
      -H "Content-Type: application/json" \
      -d '{
        "user_prompt": "{\"stores\": [{\"name\": \"QuickStart Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"QS-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-15\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect bike for getting started!\"}}], \"bike_stock\": []}], \"revision_id\": \"quickstart-1\", \"identifier\": \"hello-world\"}",
        "conversation_flow": "bike-insights"
      }'
    ```

🎉 **That's it!** You should see a comprehensive JSON response with insights from multiple AI agents analyzing the bike sales data.

**Note**: The `bike-insights` workflow is created when you run `ingen init` - it's part of the project template setup, not included in the core library. This makes it the perfect "Hello World" example to understand how Ingenious works. You can now build on `bike-insights` as a template for your specific use case.

## Workflow Categories

Insight Ingenious provides multiple conversation workflows with different availability and configuration requirements:

### **Core Library Workflows (Always Available)**
- `classification-agent` - Route input to specialized agents based on content (Azure OpenAI only)
- `knowledge-base-agent` - Search knowledge bases (stable with local ChromaDB, experimental with Azure Search)
- `sql-manipulation-agent` - Execute SQL queries (stable with local SQLite, experimental with Azure SQL)

### **Project Template Workflows (Created with `ingen init`)**
- `bike-insights` - **The recommended starting point** - Comprehensive bike sales analysis showcasing multi-agent coordination

> **Note**:
> - `bike-insights` is created when you run `ingen init` as part of the project template setup, not included in the core library
> - Local implementations (ChromaDB, SQLite) are stable; Azure integrations are experimental and may contain bugs
> - You can build on `bike-insights` as a template for your specific use case

## Azure SQL Database Setup (Optional)

For production deployments with persistent chat history storage in Azure SQL Database:

### Prerequisites
- ✅ Azure SQL Database instance with credentials
- ✅ ODBC Driver 18 for SQL Server installed

### Setup Steps

1. **Install ODBC Driver** (if not already installed):
    ```bash
    # macOS
    brew tap microsoft/mssql-release
    brew install msodbcsql18

    # Verify installation
    odbcinst -q -d | grep "ODBC Driver 18"
    ```

2. **Add Azure SQL credentials to .env**:
    ```bash
    # Add to your existing .env file
    echo 'AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net,1433;Database=your-database;Uid=your-username;Pwd=your-password;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;' >> .env
    ```

3. **Update config.yml for Azure SQL**:
    ```bash
    # Update chat_history section in config.yml
    sed -i.bak 's/database_type: "sqlite"/database_type: "azuresql"/' config.yml
    ```

4. **Update profiles.yml for environment variable**:
    ```yaml
    # Edit profiles.yml - update the chat_history section
    chat_history:
      database_connection_string: ${AZURE_SQL_CONNECTION_STRING}
    ```

5. **Validate Azure SQL setup**:
    ```bash
    uv run ingen validate
    ```

6. **Test with Azure SQL**:
    ```bash
    # Start server and test - chat history will now be stored in Azure SQL
    uv run ingen serve --port 8080
    ```

**Benefits of Azure SQL:**
- ✅ Production-grade chat history persistence
- ✅ Multi-user conversation management
- ✅ Enterprise security and compliance
- ✅ Automatic table creation and management

**Note:** Azure SQL integration is experimental and may contain bugs. For stable database functionality, use the default SQLite configuration.

## 📊 Data Format Examples

### Simple bike-insights Request (Basic)
```json
{
  "user_prompt": "{\"stores\": [{\"name\": \"Test Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"B-001\", \"quantity_sold\": 1, \"sale_date\": \"2024-01-15\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Great bike!\"}}], \"bike_stock\": []}], \"revision_id\": \"test-1\", \"identifier\": \"example\"}",
  "conversation_flow": "bike-insights"
}
```

### Advanced bike-insights Request (With Stock Data)
```json
{
  "user_prompt": "{\"stores\": [{\"name\": \"Premium Bikes\", \"location\": \"Sydney\", \"bike_sales\": [{\"product_code\": \"PB-2024-001\", \"quantity_sold\": 3, \"sale_date\": \"2024-01-15\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 4.8, \"comment\": \"Excellent quality!\"}}], \"bike_stock\": [{\"bike\": {\"brand\": \"Specialized\", \"model\": \"Turbo Vado\", \"year\": 2024, \"price\": 2899.99, \"battery_capacity\": 0.75, \"motor_power\": 500}, \"quantity\": 5}]}], \"revision_id\": \"advanced-1\", \"identifier\": \"example\"}",
  "conversation_flow": "bike-insights"
}
```

### bike_stock Object Format
The `bike_stock` array requires objects with this structure:
```json
{
  "bike": {
    "brand": "string",      // Required: Bike manufacturer
    "model": "string",      // Required: Bike model name
    "year": 2024,          // Required: Manufacturing year
    "price": 2899.99,      // Required: Price in dollars
    // Optional fields for electric bikes:
    "battery_capacity": 0.75,  // kWh
    "motor_power": 500,        // Watts
    // Optional fields for mountain bikes:
    "suspension": "full",      // Type of suspension
    // Optional fields for road bikes:
    "frame_material": "carbon" // Frame material
  },
  "quantity": 5             // Required: Stock quantity
}
```

### Multiple Stores Example
```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Store A\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"A-001\", \"quantity_sold\": 2, \"sale_date\": \"2024-01-10\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 4.5, \"comment\": \"Good value\"}}], \"bike_stock\": []}, {\"name\": \"Store B\", \"location\": \"VIC\", \"bike_sales\": [{\"product_code\": \"B-001\", \"quantity_sold\": 1, \"sale_date\": \"2024-01-12\", \"year\": 2024, \"month\": \"January\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect!\"}}], \"bike_stock\": []}], \"revision_id\": \"multi-store-1\", \"identifier\": \"comparison\"}",
    "conversation_flow": "bike-insights"
  }'
```

### Quick SQL Agent Setup (Local SQLite - Stable)

If you want to try database queries with natural language using the stable local implementation:

```bash
# Set up SQLite database
uv run python -c "
from ingenious.utils.load_sample_data import sqlite_sample_db
sqlite_sample_db()
print('✅ Sample database created')
"

# Test SQL queries
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me all tables in the database",
    "conversation_flow": "sql-manipulation-agent"
  }'
```
