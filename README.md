# Insight Ingenious

Insight Ingenious is a flexible, extensible AI framework for building, managing, and deploying intelligent agent-based conversations. It provides a robust infrastructure for creating multi-agent conversations with LLM-based agents, enabling complex workflows and sophisticated AI interactions.

## Overview

Insight Ingenious serves as a comprehensive platform for developing AI solutions with the following key capabilities:

- **Multi-agent orchestration**: Enables the coordination of multiple specialized AI agents in a collaborative conversation flow
- **Flexible deployment**: Supports both web API and command-line interfaces
- **Database integration**: Connects with various databases (SQLite, Cosmos DB) for conversation history and data persistence
- **Template-based prompting**: Uses Jinja templates to create consistent prompting patterns
- **Extensibility**: Allows custom conversation flows through a plugin architecture
- **Visualization**: Includes tools for data visualization and analysis

The framework is designed to facilitate complex interactions between AI components, making it suitable for applications in education, analytics, knowledge management, and more.

## Key Components

### Core Framework

- **`ingenious/main.py`**: The main entry point for the FastAPI application, responsible for setting up API routes and middleware
- **`ingenious/cli.py`**: Command-line interface for various operations including launching the REST API server
- **`ingenious/dependencies.py`**: Dependency injection system for service registration and configuration

### Configuration

- **`ingenious/config/`**: Configuration management including profile handling and environment-based settings
- **`ingenious/models/config.py`**: Configuration models (Pydantic) for type-safe configuration

### Data Layer

- **`ingenious/db/`**: Database abstractions with implementations for SQLite and Cosmos DB
- **`ingenious/files/`**: Storage abstractions for file operations with local and Azure implementations

### Chat Services

- **`ingenious/services/chat_service.py`**: Core service for managing chat interactions
- **`ingenious/services/chat_services/multi_agent/`**: Multi-agent conversation management
- **`ingenious/services/chat_services/multi_agent/conversation_flows/`**: Specialized conversation flow implementations

### Agent Patterns

- **`ingenious/services/chat_services/multi_agent/conversation_patterns/`**: Reusable conversation patterns for different use cases
- **`ingenious/services/chat_services/multi_agent/agents/`**: Agent definitions and implementations

### API

- **`ingenious/api/routes/`**: API route definitions for the REST interface
- **`ingenious/models/chat.py`**: Data models for chat requests and responses

### Utilities

- **`ingenious/utils/`**: Various utilities including namespace handling, token counting, and templating
- **`ingenious/templates/`**: Template files for agent prompts and responses

## Available Conversation Flows

The framework comes with several pre-built conversation flows:

- **Classification Agent**: For classifying content in a conversational context
- **Knowledge Base Agent**: For retrieving information from knowledge bases
- **SQL Manipulation Agent**: For generating and executing SQL queries
- **Web Critic Agent**: For analyzing and critiquing web content
- **Pandas Agent**: For data analysis and visualization using pandas

## Extension Points

Insight Ingenious is designed to be extended through:

1. **Custom conversation flows**: Add new flows in `ingenious_extensions/services/chat_services/multi_agent/conversation_flows/`
2. **Custom agent implementations**: Define new agents in `ingenious_extensions/services/chat_services/multi_agent/agents/`
3. **Custom API routes**: Add new API endpoints in `ingenious_extensions/api/routes/`
4. **Custom prompt templates**: Create new templates in `ingenious_extensions/templates/prompts/`

## Setup Development Environment

To set up the development environment, follow these steps:

1. **Deactivate and Remove Existing Virtual Environment (if applicable)**:

   ```bash
   deactivate
   rm -rf .venv
   ```

2. **Create and Activate a New Virtual Environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the Base Ingenious Package**:
   Run the following command to install the `ingenious` package without dependencies:

   ```bash
   pip install git+https://github.com/Insight-Services-APAC/Insight_Ingenious.git#egg=ingenious --force-reinstall
   ```

   This installs the base framework which is extended by custom extensions such as models, services, and templates.

4. **Create a `.gitignore` File**:
   Generate a `.gitignore` file to exclude unnecessary files and directories from version control:

   ```bash
   echo "
   .DS_Store
   /.venv
   /.chainlit
   /.idea
   /.cache
   /env_mkdocs/
   /tmp/context.md
   /tmp/*.db
   /dist/
   /functional_test_outputs/
   __pycache__" > .gitignore
   ```

5. **Create Profile and Configure Environment Variables**:
   Set up the `APPSETTING_INGENIOUS_CONFIG` and `APPSETTING_INGENIOUS_PROFILE` environment variables.

6. **Add/Create Template Folders**:

   ```bash
   ingen_cli initialize_new_project
   ```

   Check the `ingenious_extensions` and `tmp` folder in your project root directory. Ensure it contains the following structure:

   ```
   tmp/
   ├── context.md
   ingenious_extensions/
   ├── local_files/
   ├── models/
   ├── services/
   ├── templates/
   └── tests/
   ```

7. **Run Tests**:
   Execute the test batch using the following command:

   ```bash
   ingen_cli run-test-batch
   ```

8. **AI Test Harness**:

   ```bash
   python ingenious_extensions/tests/run_flask_app.py
   ```

9. **CLI Test Harness**:
   ```bash
   python ingenious_extensions/tests/run_ingen_cli.py
   ```

## Getting Started (For New Projects)

To set up a new project:

1. Run `ingen_cli initialize-new-project` to create the necessary folder structure
2. Configure your application in `config.yml` and profiles in `~/.ingenious/profiles.yml`
3. Develop your extensions in the `ingenious_extensions` directory
4. Run your application with `ingen_cli run-rest-api-server`

The framework includes templates and examples to help you get started quickly with your own AI applications.
