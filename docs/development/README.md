# Development Guide

This guide provides detailed information for developers who want to extend, modify, or contribute to Insight Ingenious.

## Development Environment Setup

### Prerequisites

- Python 3.10 or higher
- Git
- [uv](https://docs.astral.sh/uv/) for Python package management

### Setting Up for Development

1. Clone the repository:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -e .
   uv add pytest --dev
   uv add pre-commit --dev
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Initialize the project:
   ```bash
   ingen_cli initialize-new-project
   ```

## Project Structure

### Core Framework

- `ingenious/`: Core framework code
  - `api/`: API endpoints and routes
  - `chainlit/`: Web UI components
  - `config/`: Configuration management
  - `db/`: Database integration
  - `files/`: File storage utilities
  - `models/`: Data models and schemas
  - `services/`: Core services including chat and agent services
  - `templates/`: Prompt templates and HTML templates
  - `utils/`: Utility functions

### Extensions Template

- `ingenious_extensions_template/`: Template for custom extensions
  - `api/`: Custom API routes
  - `models/`: Custom data models
  - `sample_data/`: Sample data for testing
  - `services/`: Custom agent services
  - `templates/`: Custom prompt templates
  - `tests/`: Test harness for agent prompts

### Prompt Tuner

- `ingenious_prompt_tuner/`: Tool for tuning and testing prompts

## Core Components

### Multi-Agent Framework

The multi-agent framework is the heart of Insight Ingenious. It consists of:

#### Interfaces

- `IConversationPattern`: Abstract base class for conversation patterns
- `IConversationFlow`: Interface for implementing conversation flows

#### Services

- `multi_agent_chat_service`: Service managing agent conversations

#### Patterns

Conversation patterns define how agents interact:

- `conversation_patterns/`: Contains different conversation pattern implementations
  - `classification_agent/`: Pattern for classifying inputs and routing to specialized agents
  - `knowledge_base_agent/`: Pattern for knowledge retrieval and question answering
  - `pandas_agent/`: Pattern for data analysis
  - `sql_manipulation_agent/`: Pattern for SQL query generation and execution
  - `web_critic_agent/`: Pattern for web search and fact-checking

#### Flows

Conversation flows implement specific use cases:

- `conversation_flows/`: Contains flow implementations that use the patterns
  - `classification_agent/`: Flow for classification
  - `knowledge_base_agent/`: Flow for knowledge base interactions
  - `pandas_agent/`: Flow for data analysis
  - `sql_manipulation_agent/`: Flow for SQL queries
  - `web_critic_agent/`: Flow for web search

### Configuration System

The configuration system uses:

- `config.yml`: Project-specific, non-sensitive configuration
- `profiles.yml`: Environment-specific, sensitive configuration

Configuration is handled by:

- `ingenious/config/config.py`: Loads and validates configuration
- `ingenious/config/profile.py`: Manages profile configuration

Models:

- `ingenious/models/config.py`: Configuration data models
- `ingenious/models/config_ns.py`: Non-sensitive configuration models
- `ingenious/models/profile.py`: Profile data models

## Adding New Components

### Adding a New Agent

1. Create a new folder in `ingenious/services/chat_services/multi_agent/agents/your_agent_name/`
2. Create the agent definition file:
   - `agent.md`: Contains agent persona and system prompt
3. Add task description:
   - `tasks/task.md`: Describes the agent's tasks

### Adding a New Conversation Pattern

1. Create a new folder in `ingenious/services/chat_services/multi_agent/conversation_patterns/your_pattern_name/`
2. Create an `__init__.py` file:
   ```python
   from pkgutil import extend_path
   __path__ = extend_path(__path__, __name__)
   ```
3. Create the pattern implementation:
   ```python
   # your_pattern_name.py
   import autogen
   import logging

   class ConversationPattern:
       def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str, thread_memory: str):
           # Initialize parameters

       async def get_conversation_response(self, input_message: str) -> [str, str]:
           # Implement conversation logic
   ```

### Adding a New Conversation Flow

1. Create a new folder in `ingenious/services/chat_services/multi_agent/conversation_flows/your_flow_name/`
2. Create an `__init__.py` file:
   ```python
   from pkgutil import extend_path
   __path__ = extend_path(__path__, __name__)
   ```
3. Create the flow implementation:
   ```python
   # your_flow_name.py
   import ingenious.config.config as config
   from ingenious.models.chat import ChatResponse
   from ingenious.services.chat_services.multi_agent.conversation_patterns.your_pattern_name.your_pattern_name import ConversationPattern

   class ConversationFlow:
       @staticmethod
       async def get_conversation_response(message: str, topics: list = [], thread_memory: str='', memory_record_switch = True, thread_chat_history: list = []) -> ChatResponse:
           # Initialize and use your conversation pattern
   ```

### Adding a Custom API Route

1. Create a module in `ingenious_extensions_template/api/routes/custom.py`
2. Implement the `Api_Routes` class:
   ```python
   from fastapi import APIRouter, Depends, FastAPI
   from ingenious.models.api_routes import IApiRoutes
   from ingenious.models.config import Config

   class Api_Routes(IApiRoutes):
       def __init__(self, config: Config, app: FastAPI):
           self.config = config
           self.app = app
           self.router = APIRouter()

       def add_custom_routes(self):
           # Define your custom routes
   ```

## Testing

### Unit Tests

Run unit tests using pytest:

```bash
uv run pytest
```

### Testing Agents

Use the test harness to test agent behavior:

```bash
ingen_cli run-test-batch
```

### Testing Prompts

Use the prompt tuner for interactive testing:

1. Start the server:
   ```bash
   ingen_cli run-project
   ```
2. Navigate to http://localhost:8000/prompt-tuner
3. Select a prompt to test
4. Provide sample inputs and evaluate responses

## Debugging

### Logging

Configure logging in `config.yml`:

```yaml
logging:
  root_log_level: "DEBUG"
  log_level: "DEBUG"
```

Logs are printed to the console and can be redirected to files.

### Using the Debug Interface

When running in development mode, you can access:

- http://localhost:8000/docs - API documentation
- http://localhost:8000/prompt-tuner - Prompt tuning interface

### Common Issues

- **Missing Configuration**: Ensure environment variables are set correctly
- **Agent Not Found**: Check module naming and imports
- **Pattern Registration**: Ensure conversation patterns are properly registered
- **API Key Issues**: Verify profiles.yml contains valid API keys

## Best Practices

### Code Style

This project follows these conventions:

- PEP 8 for Python code style
- Use Ruff for linting and formatting
- Use type hints for better IDE support

### Documentation

Document your code:

- Add docstrings to all functions and classes
- Update markdown documentation for user-facing features
- Include examples for complex functionality

### Versioning

Follow semantic versioning:

- Major version: Breaking API changes
- Minor version: New features, non-breaking changes
- Patch version: Bug fixes and minor improvements

### Commits

Write clear commit messages:

- Start with a verb (Add, Fix, Update, etc.)
- Keep first line under 50 characters
- Provide more detail in the body if needed

### Pull Requests

Create focused pull requests:

- Address one feature or fix per PR
- Include tests for new functionality
- Update documentation
- Pass all CI checks
