---
title: "API Workflow Documentation"
layout: single
permalink: /api/workflows/
sidebar:
  nav: "docs"
toc: true
toc_label: "API Workflows"
toc_icon: "api"
---

# Ingenious API Workflow Documentation

This document provides detailed API usage examples for all available workflows in the Insight Ingenious framework.

## Base API Information

- **Base URL**: `http://localhost:80` (or your configured port)
- **Endpoint**: `POST /api/v1/chat`
- **Content-Type**: `application/json`

## Available Workflows

### 1. bike-insights - **"Hello World" Workflow (START HERE!)**

**Purpose**: The recommended first workflow - showcases multi-agent coordination through comprehensive bike sales analysis. This is the "Hello World" of Ingenious!

**Availability**: Created when you run `ingen init` (part of project template)

**Required Input Format**:
```json
{
  "user_prompt": "{\"stores\": [...], \"revision_id\": \"unique-id\", \"identifier\": \"identifier\"}",
  "conversation_flow": "bike-insights"
}
```

**Hello World Example**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Hello Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"HELLO-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-01\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect introduction to Ingenious!\"}}], \"bike_stock\": []}], \"revision_id\": \"hello-1\", \"identifier\": \"world\"}",
    "conversation_flow": "bike-insights"
  }'
```

**Data Structure**:
```json
{
  "stores": [
    {
      "name": "Store Name",
      "location": "Location",
      "bike_sales": [
        {
          "product_code": "PRODUCT-CODE",
          "quantity_sold": 1,
          "sale_date": "YYYY-MM-DD",
          "year": 2023,
          "month": "Month Name",
          "customer_review": {
            "rating": 4.5,
            "comment": "Customer feedback"
          }
        }
      ],
      "bike_stock": []
    }
  ],
  "revision_id": "unique-revision-id",
  "identifier": "unique-identifier"
}
```

**Agents Involved**:
- � **classification_agent**: Classifies and routes user queries
- 🎓 **education_expert**: Handles educational content queries
- � **knowledge_base_agent**: Searches knowledge bases
- �️ **sql_manipulation_agent**: Processes database queries

**Response Format**:
```json
{
  "thread_id": "uuid",
  "message_id": "identifier",
  "agent_response": "[{agent1_response}, {agent2_response}, ...]",
  "token_count": 1234,
  "followup_questions": {},
  "topic": null,
  "memory_summary": "",
  "event_type": null
}
```

---

### 2. ✅ classification-agent - Simple Text Processing

**Purpose**: Basic text classification and routing

**Availability**: Core library workflow

**Required Configuration**: Azure OpenAI only

**Required Input Format**:
```json
{
  "user_prompt": "Your question or input text here",
  "conversation_flow": "classification-agent"
}
```

**Example Request**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Analyze this customer feedback: The bike was excellent!",
    "conversation_flow": "classification-agent"
  }'
```

**Use Cases**:
- General text classification
- Routing complex queries to specialized agents
- Sentiment analysis of user input
- Topic categorization

---

### 3. 🔍 knowledge-base-agent - Knowledge Search

**Purpose**: Search and retrieve information from configured knowledge bases

**Availability**: Core library (always available)

**Requirements**:
- Azure Search Service configured
- Knowledge base indexed

**Example Request**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Find information about bike maintenance",
    "conversation_flow": "knowledge-base-agent"
  }'
```

---

### 4. 📊 sql-manipulation-agent - Database Queries

**Purpose**: Execute SQL queries based on natural language input

**Availability**: Core library (always available)

**Requirements**:
- Database connection configured
- SQL database accessible

**Example Request**:
```bash
curl -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "Show me the top selling bikes in the last month",
    "conversation_flow": "sql-manipulation-agent"
  }'
```

---

## 🛠️ Testing Your Workflows

### Quick Test Script

Save this as `test_workflows.sh`:

```bash
#!/bin/bash

echo "🧪 Testing Ingenious Workflows..."

# Test 1: bike-insights (Hello World)
echo "⭐ Testing bike-insights workflow (Hello World)..."
curl -s -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "{\"stores\": [{\"name\": \"Hello Store\", \"location\": \"NSW\", \"bike_sales\": [{\"product_code\": \"HELLO-001\", \"quantity_sold\": 1, \"sale_date\": \"2023-04-01\", \"year\": 2023, \"month\": \"April\", \"customer_review\": {\"rating\": 5.0, \"comment\": \"Perfect introduction to Ingenious!\"}}], \"bike_stock\": []}], \"revision_id\": \"hello-1\", \"identifier\": \"world\"}",
    "conversation_flow": "bike-insights"
  }' | jq '.message_id, .token_count'

# Test 2: classification-agent (Simple Alternative)
echo "✅ Testing classification-agent workflow (Simple Alternative)..."
curl -s -X POST http://localhost:80/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_prompt": "This is a test message for classification",
    "conversation_flow": "classification-agent"
  }' | jq '.message_id, .token_count'

echo "✅ Tests completed!"
```

Make it executable: `chmod +x test_workflows.sh`

---

## 🚨 Common Issues & Solutions

### 1. "Expecting value: line 1 column 1 (char 0)"
**Problem**: bike-insights workflow expects JSON data in user_prompt
**Solution**: Ensure user_prompt contains properly escaped JSON string

### 2. "Class ConversationFlow not found"
**Problem**: Workflow name incorrect or workflow not available
**Solution**: Use correct workflow names (prefer hyphens: `bike-insights`, `classification-agent`)

### 3. "Validation error in field"
**Problem**: Missing or invalid configuration
**Solution**: Check profiles.yml and .env files for required values

### 4. Server runs on wrong port
**Problem**: Port parameter not working
**Solution**: Check WEB_PORT environment variable or config.yml

---

## 🔧 Configuration Requirements

### Hello World Setup (bike-insights + classification-agent)
```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_BASE_URL=your-endpoint
INGENIOUS_PROJECT_PATH=./config.yml
INGENIOUS_PROFILE_PATH=./profiles.yml
```

### Advanced Setup (all workflows)
- Azure Search Service (knowledge-base-agent)
- Database connection (sql-manipulation-agent)
- Additional authentication settings

---

## 📚 Additional Resources

- 📖 **Configuration Guide**: `/docs/configuration/README.md`
- 🏗️ **Custom Workflows**: `/docs/extensions/README.md`
- 🐛 **Troubleshooting**: `/docs/troubleshooting/README.md`
- 🧪 **Testing Guide**: `/docs/testing/README.md`

For more help: `ingen workflows <workflow-name>` or `ingen --help`
