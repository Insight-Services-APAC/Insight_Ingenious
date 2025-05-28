# Working with Agents

This document provides detailed information about working with agents in Insight Ingenious.

## What are Agents?

In Insight Ingenious, an agent is an AI entity designed to perform specific tasks and engage in conversations. Agents are configured with specific models, prompts, and behaviors to serve different purposes in your application.

## Agent Architecture

The agent system in Insight Ingenious is built around the following components:

1. **Agent Model**: The core definition of an agent, including its configuration and behavior
2. **Agent Chat**: Represents a conversation between agents or between an agent and a user
3. **Chat Service**: Manages the flow of messages between agents and users

## Built-in Agent Types

Insight Ingenious includes several built-in agent types:

### 1. Basic Assistant Agent

A simple agent that responds to user messages using a language model.

```yaml
agents:
  - name: "assistant"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a helpful assistant."
```

### 2. Function-enabled Agent

An agent that can call functions to interact with external systems or retrieve information.

```yaml
agents:
  - name: "function_agent"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a helpful assistant that can retrieve information."
    functions:
      - name: "get_weather"
        description: "Get the current weather for a location"
        parameters:
          type: "object"
          properties:
            location:
              type: "string"
              description: "The city and state, e.g. San Francisco, CA"
          required: ["location"]
```

### 3. Router Agent

An agent that routes messages to other agents based on message content or routing rules.

```yaml
agents:
  - name: "router"
    model_config:
      model: "gpt-4o"
      temperature: 0.3
    system_prompt: "You are a router agent that directs user queries to the appropriate agent."
    routing:
      default: "general_assistant"
      rules:
        - pattern: "weather|temperature|forecast"
          agent: "weather_agent"
        - pattern: "code|programming|function"
          agent: "coding_assistant"
```

## Creating Custom Agents

You can create custom agents by extending the base Agent class and implementing your own behavior:

```python
# ingenious_extensions/models/custom_agent.py
from ingenious.models.agent import Agent
from ingenious.models.chat import ChatRequest, ChatResponse
from pydantic import BaseModel

class CustomAgentParams(BaseModel):
    custom_param: str

class CustomAgent(Agent):
    def __init__(self, name: str, config, params: CustomAgentParams):
        super().__init__(name, config)
        self.custom_param = params.custom_param

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        # Custom message processing logic
        return ChatResponse(
            conversation_id=request.conversation_id,
            message_id="custom-message-id",
            response=f"Custom response using {self.custom_param}",
            created_at=datetime.now().isoformat()
        )
```

Register your custom agent in the configuration:

```yaml
agents:
  - name: "my_custom_agent"
    type: "custom_agent"  # This should match your agent class
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a custom agent."
    custom_params:
      custom_param: "custom value"
```

## Agent Conversation Flows

Conversation flows define how agents interact with each other and with users. Insight Ingenious supports several types of conversation flows:

### 1. Basic Flow

A simple conversation between a user and a single agent.

```yaml
conversation_flows:
  - name: "basic_flow"
    description: "Basic conversation with a single agent"
    chat_service: "basic"
    agents:
      - "assistant"
```

### 2. Multi-Agent Flow

A conversation involving multiple agents that can interact with each other.

```yaml
conversation_flows:
  - name: "multi_agent_flow"
    description: "Multi-agent conversation"
    chat_service: "multi_agent"
    agents:
      - "customer_service"
      - "technical_support"
    orchestration:
      type: "sequential"  # or "parallel", "round_robin"
```

### 3. Router Flow

A flow that routes messages to different agents based on content.

```yaml
conversation_flows:
  - name: "router_flow"
    description: "Router-based conversation flow"
    chat_service: "router"
    agents:
      - "router"
      - "general_assistant"
      - "weather_agent"
      - "coding_assistant"
    router:
      agent: "router"
```

## Agent System Prompts

System prompts define the behavior and capabilities of an agent. Here are some examples of effective system prompts:

### Customer Service Agent

```
You are a customer service agent for Acme Corporation. Your goal is to help customers with their inquiries about our products and services. Be polite, empathetic, and informative. If you don't know the answer to a question, acknowledge that and offer to connect the customer with a specialist who can help.

Products:
- Widget Pro: A professional-grade widget for industrial use
- Widget Lite: A consumer-grade widget for home use
- Widget Cloud: A subscription service for widget management

Services:
- Installation: Professional installation of widgets
- Maintenance: Regular maintenance of widgets
- Support: 24/7 customer support for widget issues

When helping customers, ask clarifying questions if needed, and always confirm whether you've resolved their issue before concluding the conversation.
```

### Technical Support Agent

```
You are a technical support agent specializing in software troubleshooting. Your goal is to help users diagnose and fix problems with their software applications.

Follow these steps when helping users:
1. Understand the problem by asking clarifying questions
2. Identify the likely causes of the problem
3. Suggest troubleshooting steps in a clear, step-by-step manner
4. Verify whether the steps resolved the issue
5. If not, escalate to more advanced troubleshooting or suggest contacting specialized support

Common troubleshooting steps you can suggest:
- Restarting the application or device
- Checking for updates
- Clearing cache or temporary files
- Checking system requirements
- Looking for error logs

Be patient, precise, and avoid technical jargon unless necessary. If you use technical terms, explain them clearly.
```

## Agent Memory and State

Agents can maintain state and memory across multiple turns in a conversation:

```python
# Implementing memory in a custom agent
class MemoryAgent(Agent):
    def __init__(self, name: str, config):
        super().__init__(name, config)
        self.memory = {}  # Simple memory store

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        # Retrieve conversation memory
        conversation_memory = self.memory.get(request.conversation_id, [])

        # Process the message with memory context
        response = await self._generate_response(request, conversation_memory)

        # Update memory
        conversation_memory.append({
            "user": request.message,
            "assistant": response.response
        })
        self.memory[request.conversation_id] = conversation_memory

        return response
```

## Using Agent Tools (Function Calling)

Agents can use tools (functions) to interact with external systems or perform specific actions:

```yaml
agents:
  - name: "tool_agent"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are an assistant that uses tools to help users."
    functions:
      - name: "search_database"
        description: "Search the database for information"
        parameters:
          type: "object"
          properties:
            query:
              type: "string"
              description: "The search query"
            limit:
              type: "integer"
              description: "Maximum number of results to return"
          required: ["query"]
      - name: "create_ticket"
        description: "Create a support ticket"
        parameters:
          type: "object"
          properties:
            title:
              type: "string"
              description: "Ticket title"
            description:
              type: "string"
              description: "Ticket description"
            priority:
              type: "string"
              enum: ["low", "medium", "high"]
              description: "Ticket priority"
          required: ["title", "description"]
```

Implement the function handlers in your code:

```python
# ingenious_extensions/services/functions/tools.py
async def search_database(query: str, limit: int = 10):
    # Implementation of database search
    return {"results": [...]}

async def create_ticket(title: str, description: str, priority: str = "medium"):
    # Implementation of ticket creation
    return {"ticket_id": "T12345", "status": "created"}
```

Register the function handlers:

```python
# ingenious_extensions/models/function_registry.py
from ingenious.models.function_registry import FunctionRegistry
from ingenious_extensions.services.functions.tools import search_database, create_ticket

function_registry = FunctionRegistry()
function_registry.register("search_database", search_database)
function_registry.register("create_ticket", create_ticket)
```

## Agent Events and Callbacks

You can register callbacks to monitor and respond to agent events:

```python
# ingenious_extensions/services/event_handlers.py
from ingenious.models.events import EventHandler, MessageEvent

class CustomEventHandler(EventHandler):
    async def on_message_received(self, event: MessageEvent):
        # Handle message received event
        print(f"Message received: {event.message}")

    async def on_message_processed(self, event: MessageEvent):
        # Handle message processed event
        print(f"Message processed: {event.response}")

    async def on_error(self, event: ErrorEvent):
        # Handle error event
        print(f"Error: {event.error}")
```

Register the event handler:

```python
# ingenious_extensions/app_startup.py
from ingenious.models.events import EventManager
from ingenious_extensions.services.event_handlers import CustomEventHandler

event_manager = EventManager()
event_manager.register_handler(CustomEventHandler())
```

## Testing Agents

Insight Ingenious provides tools for testing agents:

```python
# tests/test_custom_agent.py
import pytest
from ingenious.tests.utils import MockConfig, MockChatRequest
from ingenious_extensions.models.custom_agent import CustomAgent, CustomAgentParams

@pytest.mark.asyncio
async def test_custom_agent():
    # Arrange
    config = MockConfig()
    params = CustomAgentParams(custom_param="test value")
    agent = CustomAgent("test_agent", config, params)
    request = MockChatRequest(message="Hello")

    # Act
    response = await agent.process_message(request)

    # Assert
    assert "Custom response using test value" in response.response
```

## Debugging Agents

To debug agent behavior, you can enable debug logging:

```yaml
log_level: "DEBUG"
```

You can also use the prompt tuner interface to test and refine agent prompts:

```
http://127.0.0.1:8000/prompt-tuner
```

## Best Practices

1. **Clear System Prompts**: Write clear, detailed system prompts that define the agent's role and behavior.

2. **Appropriate Temperature**: Use lower temperature (0.3-0.5) for more deterministic tasks and higher temperature (0.7-0.9) for more creative tasks.

3. **Function Definitions**: Define functions with clear descriptions and parameter definitions.

4. **Conversation Memory**: Maintain conversation memory for context awareness.

5. **Error Handling**: Implement proper error handling for agent failures.

6. **Testing**: Test agents with various inputs to ensure they behave as expected.

7. **Monitoring**: Monitor agent behavior and performance in production.

8. **Iterative Refinement**: Continuously refine agent prompts and behavior based on real-world usage.
