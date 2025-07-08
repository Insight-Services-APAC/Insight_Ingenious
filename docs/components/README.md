---
title: "Components Reference"
layout: single
permalink: /components/
sidebar:
  nav: "docs"
toc: true
toc_label: "Components"
toc_icon: "cogs"
---

# Components Reference

This document provides detailed information about the key components of the Insight Ingenious library - an enterprise-grade Python library for building AI agent APIs with Microsoft Azure integrations and comprehensive debugging utilities.

## Multi-Agent Framework

### ConversationPattern

The `ConversationPattern` class is the foundation for defining how agents interact with each other.

#### Core Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| `classification-agent` | Classifies input and routes to topic-specific agents | Content classification, intent detection |
| `knowledge-base-agent` | Searches and retrieves information from knowledge bases | Question answering, information retrieval |
| `sql-manipulation-agent` | Generates and executes SQL queries | Database interactions, data querying |
| `bike-insights` | Multi-agent bike sales analysis | Template workflow example |

#### Key Methods

- `__init__(default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str, thread_memory: str)`: Initializes the pattern
- `get_conversation_response(input_message: str) -> [str, str]`: Core method that processes input and returns agent response

### ConversationFlow

The `ConversationFlow` class implements specific use cases using conversation patterns.

#### Core Flows

| Flow | Description | Pattern Used |
|------|-------------|--------------|
| `classification-agent` | Routes inputs to specialized agents | `classification-agent` |
| `knowledge-base-agent` | Answers questions using knowledge bases | `knowledge-base-agent` |
| `sql-manipulation-agent` | Executes SQL queries based on natural language | `sql-manipulation-agent` |

#### Key Methods

- `get_conversation_response(message: str, topics: list, thread_memory: str, memory_record_switch: bool, thread_chat_history: list) -> ChatResponse`: Processes input and returns response

### Agents

Agents are specialized AI entities that perform specific tasks in the conversation.

#### Core Agent Types

| Agent Type | Description | Used In |
|------------|-------------|---------|
| `AssistantAgent` | Standard agent for task completion | All patterns |
| `UserProxyAgent` | Represents the user in agent conversations | All patterns |
| `RetrieveUserProxyAgent` | User proxy with document retrieval capabilities | Knowledge-based patterns |

#### Agent Definition

Agents are defined in markdown files with the following sections:

- **Name and Persona**: Agent identity
- **System Message**: Core instructions
- **Backstory**: Context and background
- **Instructions**: Detailed behavior guidelines
- **Examples**: Sample interactions

## Data Models

### Chat Models

These models define the structure of chat interactions:

- `IChatRequest`: Represents a user request
  - `thread_id`: Conversation thread identifier
  - `user_prompt`: User's input message
  - `event_type`: Type of event
  - `conversation_flow`: Which conversation flow to use
  - `user_id`: User identifier (optional)
  - `user_name`: User display name (optional)
  - `topic`: Conversation topic (optional)
  - `memory_record`: Whether to record in memory (default: True)
  - `thread_chat_history`: Previous conversation history
  - `thread_memory`: Thread-specific memory context

- `IChatResponse`: Represents an agent response
  - `thread_id`: Conversation thread identifier
  - `message_id`: Unique message identifier
  - `agent_response`: The content returned to the user
  - `followup_questions`: Suggested follow-up questions
  - `token_count`: Number of tokens used
  - `max_token_count`: Maximum tokens available
  - `topic`: Response topic
  - `memory_summary`: Summary for memory storage
  - `event_type`: Type of response event

### Configuration Models

These models define the structure of configuration:

- `Config`: Top-level configuration model
  - `chat_history`: Chat history configuration
  - `models`: LLM model configurations
  - `logging`: Logging configuration
  - `tool_service`: Tool service configuration
  - `chat_service`: Chat service configuration
  - `chainlit_configuration`: Web UI configuration
  - `azure_search_services`: Search service configurations
  - `azure_sql_services`: SQL service configuration
  - `file_storage`: File storage configuration

- `Profile`: Contains sensitive configuration
  - `name`: Profile identifier
  - `models`: Model-specific API keys and endpoints
  - `azure_search_services`: Search service API keys
  - `web_configuration`: Authentication credentials

## Services

### ChatService

The `IChatService` interface defines the chat interaction API:

- `get_chat_response(chat_request: ChatRequest) -> ChatResponse`: Processes a chat request and returns a response

#### ChatService

Implementation of `IChatService` that dynamically loads chat service types:

- `__init__(chat_service_type: str, chat_history_repository: ChatHistoryRepository, conversation_flow: str, config: Config, revision: str)`: Initializes the service
- `get_chat_response(chat_request: ChatRequest) -> ChatResponse`: Processes a chat request using the specified conversation flow

### ToolFunctions

The `ToolFunctions` class provides utility functions for agents:

- `execute_sql_local`: Executes SQL queries against local databases
- `execute_sql_azure`: Executes SQL queries against Azure SQL databases
- `search_azure`: Searches Azure Cognitive Search indices

## Storage

### ChatHistoryRepository

The `ChatHistoryRepository` interface defines chat history storage:

- `add_message(message: Message) -> str`: Adds a message to the history
- `get_thread_messages(thread_id: str) -> List[Message]`: Retrieves messages for a thread

#### Implementations

- `SQLiteChatHistoryRepository`: Stores chat history in SQLite
- `AzureSQLChatHistoryRepository`: Stores chat history in Azure SQL Database

### FileStorage

The `FileStorage` class manages file operations:

- `read_file(file_name: str, file_path: str) -> str`: Reads a file
- `write_file(content: str, file_name: str, file_path: str) -> bool`: Writes content to a file
- `get_prompt_template_path(revision_id: str) -> str`: Gets the path to a prompt template
- `delete_file(file_name: str, file_path: str) -> bool`: Deletes a file
- `list_files(file_path: str) -> List[str]`: Lists files in a directory
- `check_if_file_exists(file_path: str, file_name: str) -> bool`: Checks if a file exists

#### Implementations

- `LocalFileStorage`: Stores files on the local filesystem
- `AzureFileStorage`: Stores files in Azure Blob Storage

### MemoryManager

The `MemoryManager` class provides cloud-aware conversation memory management:

- `__init__(config: Config, memory_path: str = None)`: Initializes the memory manager
- `read_memory(thread_id: str = None, default_content: str = "") -> str`: Reads memory content
- `write_memory(content: str, thread_id: str = None) -> bool`: Writes memory content
- `maintain_memory(new_content: str, max_words: int = 150, thread_id: str = None) -> bool`: Maintains memory with word limits
- `delete_memory(thread_id: str = None) -> bool`: Deletes memory content

#### Features

- **Cloud Storage Support**: Works with both local and Azure Blob Storage backends
- **Thread-Specific Memory**: Support for conversation-specific memory isolation
- **Automatic Truncation**: Maintains memory within specified word limits
- **Async Operations**: Fully asynchronous for better performance
- **Fallback Support**: Graceful degradation to local storage when needed

#### Usage

```python
from ingenious.services.memory_manager import MemoryManager
from ingenious.dependencies import get_config

# Initialize memory manager
config = get_config()
memory_manager = MemoryManager(config)

# Basic memory operations
await memory_manager.write_memory("Conversation context")
context = await memory_manager.read_memory()

# Thread-specific memory
await memory_manager.write_memory("User-specific context", thread_id="user-123")
user_context = await memory_manager.read_memory(thread_id="user-123")

# Memory maintenance with limits
await memory_manager.maintain_memory("New interaction data", max_words=150)
```

## Web Interface

### Chainlit Integration

The Chainlit integration provides a web UI for chat interactions:

- `app.py`: Chainlit application definition
- `datalayer.py`: Data layer for Chainlit
- `index.html`: Landing page

### Prompt Tuner

The prompt tuner provides tools for developing and testing prompts:

- `run_flask_app.py`: Flask app for the prompt tuner
- `event_processor.py`: Processes prompt testing events
- `payload.py`: Handles test payloads

## Command Line Interface

The CLI provides commands for managing the framework:

- `init`: Creates a new project structure with template files
- `serve`: Starts the FastAPI server with REST endpoints
- `test`: Runs tests on agent prompts with configurable options
- `prompt-tuner`: Starts the prompt tuning web application
- `workflows`: Shows available workflows and their requirements
- `status`: Check system status and configuration
- `validate`: Validate system configuration and requirements
- `version`: Show version information
- `help`: Show detailed help and getting started guide

## API Layer

### FastAPI Integration

The API layer is built with FastAPI:

- `main.py`: Main FastAPI application
- `api/routes/`: API route definitions
  - `chat.py`: Chat endpoint for conversation workflows
  - `diagnostic.py`: System diagnostics and workflow status endpoints
  - `message_feedback.py`: Feedback endpoint
  - `prompts.py`: Prompt management endpoints

#### Key API Endpoints

| Endpoint | Purpose | Description |
|----------|---------|-------------|
| `POST /api/v1/chat` | Execute workflows | Send messages to conversation workflows |
| `GET /api/v1/workflows` | List workflows | Get all workflows and their configuration status |
| `GET /api/v1/workflow-status/{workflow}` | Check status | Check if a specific workflow is properly configured |
| `GET /api/v1/diagnostic` | System status | Get system diagnostic information |

#### Workflow Status API

Check configuration requirements and status:

```bash
# List all workflows and their status
curl http://localhost:80/api/v1/workflows

# Check specific workflow configuration
curl http://localhost:80/api/v1/workflow-status/knowledge-base-agent
```

Example response:
```json
{
  "workflow": "knowledge-base-agent",
  "configured": false,
  "missing_config": ["azure_search_services.key: Missing in profiles.yml"],
  "required_config": ["models", "chat_service", "azure_search_services"],
  "external_services": ["Azure OpenAI", "Azure Cognitive Search"],
  "ready": false,
  "test_command": "curl -X POST http://localhost:80/api/v1/chat...",
  "documentation": "See docs/workflows/README.md for setup instructions"
}
```

## Extension Points

### Custom Agents

Create custom agents by adding:

- `agent.md`: Agent definition
- `tasks/task.md`: Task description

### Custom Conversation Patterns

Create custom patterns by implementing:

- `ConversationPattern` class with required methods
- `ConversationFlow` class that uses the pattern

### Custom API Routes

Create custom routes by implementing:

- `Api_Routes` class with `add_custom_routes` method

### Custom Templates

Create custom prompt templates:

- Jinja2 templates in `templates/prompts/`
