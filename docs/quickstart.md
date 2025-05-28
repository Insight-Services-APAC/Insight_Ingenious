# Quickstart Guide

This quickstart guide will help you get up and running with Insight Ingenious in just a few minutes.

## Quick Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
   cd Insight_Ingenious
   ```

2. **Install dependencies** (using uv):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh # If you don't have uv installed
   uv venv
   uv pip install -e .
   ```

3. **(Recommended for development) Install pre-commit hooks**:
   ```bash
   uv add pre-commit --dev
   uv run pre-commit install
   ```

4. **Initialize a new project**:
   ```bash
   ingen init
   ```

## Your First Conversation

### 1. Configure Your API Keys

Before you can use the agents, you need to configure your API credentials. Edit the profiles file at `~/.ingenious/profiles.yml`:

```yaml
profiles:
  - name: default
    openai:
      api_key: your_openai_api_key
```

### 2. Start the API Server

```bash
ingen run
```

### 3. Send a Test Request

Using curl or any API client, send a request to the chat endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test-conversation",
    "message": "Hello, can you help me understand what Insight Ingenious does?",
    "conversation_flow": "default"
  }'
```

### 4. View the Response

You should receive a response from the AI agent explaining Insight Ingenious!

## Web Interface

Insight Ingenious includes a web interface built on Chainlit:

1. **Access the interface** by navigating to:
   ```
   http://127.0.0.1:8000/chainlit
   ```

2. **Start a new chat** by typing your message in the input box.

## Prompt Tuner Interface

For tuning and managing prompts, access the Prompt Tuner interface:

```
http://127.0.0.1:8000/prompt-tuner
```

## Quick Configuration

### Basic Configuration (config.yml)

```yaml
api_key: ""
profile: "default"
log_level: "INFO"
agents:
  - name: "customer_service"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a helpful customer service agent."
```

### Chat Service Types

Insight Ingenious supports different chat service types:

- **Basic**: Simple single-agent chat
- **MultiAgent**: Conversations between multiple agents
- **Router**: Routing messages to different agents

## Creating Extensions

To create your own extension:

1. **Copy the template**:
   ```bash
   cp -r ingenious/ingenious_extensions_template ingenious_extensions
   ```

2. **Customize the code** to fit your needs.

3. **Update the configuration** to use your extension.

## Using pre-commit

To ensure code quality and consistent formatting, pre-commit hooks are used in this project. After installing pre-commit, you can manually run all hooks on your codebase:

```bash
pre-commit run --all-files
```

This will check and auto-fix issues such as trailing whitespace, end-of-file fixes, and code formatting (e.g., with Black for Python).

## Next Steps

Now that you have Insight Ingenious running, you might want to:

1. Read the [Configuration Guide](./configuration.md) to customize your setup
2. Explore the [Agent System](./agents.md) to create custom agents
3. Check the [API Documentation](./api.md) for more advanced API usage
4. Learn about [Extensions](./extensions.md) to extend the framework
