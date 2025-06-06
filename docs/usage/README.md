# Usage Guide

This guide shows how to use Insight Ingenious for various tasks.

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/Insight-Services-APAC/Insight_Ingenious.git
cd Insight_Ingenious

# Install dependencies
uv venv
uv pip install -e .

# Initialize project
ingen_cli initialize-new-project
```

### Basic Configuration

1. Edit `config.yml` in your project directory
2. Create or edit `profiles.yml` in `~/.ingenious/`
3. Set environment variables:
   ```bash
   export INGENIOUS_PROJECT_PATH=/path/to/your/project/config.yml
   export INGENIOUS_PROFILE_PATH=~/.ingenious/profiles.yml
   ```

## Using the CLI

Insight Ingenious provides a command-line interface with various utilities:

### Initialize a New Project

```bash
ingen_cli initialize-new-project
```

This creates the folder structure and configuration files needed for your project.

### Run Tests

```bash
ingen_cli run-test-batch
```

Runs tests against your agent prompts.

### Start the Application

```bash
ingen_cli run-project
```

Starts the FastAPI server with Chainlit UI.

## Using the Web UI

### Accessing the UI

Once the application is running, access the web UI at:
- http://localhost:8000 - Main application
- http://localhost:8000/chainlit - Chainlit chat interface
- http://localhost:8000/prompt-tuner - Prompt tuning interface

### Chatting with Agents

1. Navigate to http://localhost:8000/chainlit
2. Start a new conversation
3. Type your message
4. The appropriate agents will process your request and respond

### Tuning Prompts

1. Navigate to http://localhost:8000/prompt-tuner
2. Log in with credentials from your `profiles.yml`
3. Select the prompt template you want to edit
4. Make changes and test with sample data
5. Save revisions for version control

## Creating Custom Agents

### Custom Agent Structure

1. Create a new agent folder in `ingenious/services/chat_services/multi_agent/agents/your_agent_name/`
2. Create these files:
   - `agent.md`: Agent definition and persona
   - `tasks/task.md`: Task description for the agent

### Agent Definition Example

```markdown
# Your Agent Name

## Name and Persona

* Name: Your name is Ingenious and you are a [Specialty] Expert
* Description: You are a [specialty] expert assistant. Your role is to [description of responsibilities].

## System Message

### Backstory

[Background information about the agent's role and knowledge]

### Instructions

[Detailed instructions on how the agent should operate]

### Examples

[Example interactions or outputs]
```

## Creating Custom Conversation Patterns

### Pattern Structure

1. Create a new pattern module in `ingenious/services/chat_services/multi_agent/conversation_patterns/your_pattern_name/`
2. Implement the `ConversationPattern` class following the interface
3. Create a corresponding flow in `ingenious/services/chat_services/multi_agent/conversation_flows/your_pattern_name/`

### Pattern Implementation Example

```python
# conversation_patterns/your_pattern_name/your_pattern_name.py
import autogen
import logging

class ConversationPattern:
    def __init__(self, default_llm_config: dict, topics: list, memory_record_switch: bool, memory_path: str, thread_memory: str):
        self.default_llm_config = default_llm_config
        self.topics = topics
        self.memory_record_switch = memory_record_switch
        self.memory_path = memory_path
        self.thread_memory = thread_memory

        # Initialize agents
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            system_message="I represent the user's request"
        )

        self.your_agent = autogen.AssistantAgent(
            name="your_agent",
            system_message="Your agent's system message",
            llm_config=self.default_llm_config
        )

    async def get_conversation_response(self, input_message: str) -> [str, str]:
        # Set up agent interactions
        result = await self.user_proxy.a_initiate_chat(
            self.your_agent,
            message=input_message
        )

        return result.summary, ""
```

### Flow Implementation Example

```python
# conversation_flows/your_pattern_name/your_pattern_name.py
from ingenious.models.chat import ChatResponse
from ingenious.services.chat_services.multi_agent.conversation_patterns.your_pattern_name.your_pattern_name import ConversationPattern

class ConversationFlow:
    @staticmethod
    async def get_conversation_response(message: str, topics: list = [], thread_memory: str='', memory_record_switch = True, thread_chat_history: list = []) -> ChatResponse:
        # Get configuration
        import ingenious.config.config as config
        _config = config.get_config()
        llm_config = _config.models[0].__dict__
        memory_path = _config.chat_history.memory_path

        # Initialize the conversation pattern
        agent_pattern = ConversationPattern(
            default_llm_config=llm_config,
            topics=topics,
            memory_record_switch=memory_record_switch,
            memory_path=memory_path,
            thread_memory=thread_memory
        )

        # Get the conversation response
        res, memory_summary = await agent_pattern.get_conversation_response(message)

        return res, memory_summary
```

## Using Custom Templates

### Creating Custom Prompts

1. Create a new template in `templates/prompts/your_prompt_name.jinja`
2. Use Jinja2 syntax for dynamic content

Example:
```jinja
I am an agent tasked with providing insights about {{ topic }} based on the input payload.

User input: {{ user_input }}

Please provide a detailed analysis focusing on:
1. Key facts
2. Relevant context
3. Potential implications

Response format:
{
  "analysis": {
    "key_facts": [],
    "context": "",
    "implications": []
  },
  "recommendation": ""
}
```

### Using Templates in Agents

```python
async def get_conversation_response(self, chat_request: ChatRequest) -> ChatResponse:
    # Load the template
    template_content = await self.Get_Template(file_name="your_prompt_name.jinja")

    # Render the template with dynamic values
    env = Environment()
    template = env.from_string(template_content)
    rendered_prompt = template.render(
        topic="example topic",
        user_input=chat_request.user_prompt
    )

    # Use the rendered prompt
    your_agent.system_prompt = rendered_prompt
```

## API Integration

### Using the REST API

You can interact with Insight Ingenious through its REST API:

```bash
# Start a conversation
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n username:password | base64)" \
  -d '{
    "user_prompt": "Your message here",
    "conversation_flow": "your_conversation_flow"
  }'
```

### Creating Custom API Routes

1. Create a new route module in `ingenious_extensions_template/api/routes/custom.py`
2. Implement the `Api_Routes` class

Example:
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
        @self.router.get("/api/v1/custom-endpoint")
        async def custom_endpoint():
            return {"message": "Custom endpoint response"}

        self.app.include_router(self.router)
```
