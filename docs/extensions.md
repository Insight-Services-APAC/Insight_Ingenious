# Extending Insight Ingenious

This document explains how to extend and customize Insight Ingenious to fit your specific needs.

## Extension Structure

Insight Ingenious provides a template for creating extensions in the `ingenious_extensions_template` directory. This template includes the following structure:

```
ingenious_extensions_template/
  ├── __init__.py
  ├── config.template.yml
  ├── profiles.template.yml
  ├── readme.md
  ├── api/
  │   └── routes/
  │       └── custom.py
  ├── models/
  ├── sample_data/
  ├── services/
  ├── templates/
  └── tests/
```

To create your own extension:

1. Copy the `ingenious_extensions_template` directory
2. Rename it to `ingenious_extensions`
3. Customize the code to fit your needs

## Extension Points

Insight Ingenious offers several extension points:

### 1. Custom API Routes

Create custom API endpoints by extending the API routes:

```python
# ingenious_extensions/api/routes/custom.py
from fastapi import APIRouter, Depends
from ingenious.models.api_routes import IApiRoutes
from ingenious.config.config import Config

class Api_Routes(IApiRoutes):
    def __init__(self, config: Config, app: "FastAPI"):
        self.router = APIRouter()
        self.config = config
        self.app = app

    def add_custom_routes(self):
        @self.router.get("/custom-endpoint")
        async def custom_endpoint():
            return {"message": "This is a custom endpoint"}

        # Include your router
        self.app.include_router(self.router, prefix="/api/v1", tags=["Custom"])
```

### 2. Custom Agents

Create custom agent implementations:

```python
# ingenious_extensions/models/custom_agent.py
from ingenious.models.agent import Agent
from ingenious.models.chat import ChatRequest, ChatResponse
from datetime import datetime

class CustomAgent(Agent):
    def __init__(self, name: str, config):
        super().__init__(name, config)
        # Custom initialization

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        # Custom processing logic
        return ChatResponse(
            conversation_id=request.conversation_id,
            message_id="custom-message-id",
            response="Custom agent response",
            created_at=datetime.now().isoformat()
        )
```

Register your agent in your configuration:

```yaml
agents:
  - name: "custom_agent"
    type: "custom_agent"
    model_config:
      model: "gpt-4o"
      temperature: 0.7
    system_prompt: "You are a custom agent."
```

### 3. Custom Chat Services

Create custom chat service implementations:

```python
# ingenious_extensions/services/chat_services/custom/service.py
from ingenious.services.chat_service import IChatService
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.config.config import Config

class custom_chat_service(IChatService):
    def __init__(self, config: Config, chat_history_repository: ChatHistoryRepository, conversation_flow: str):
        self.config = config
        self.chat_history_repository = chat_history_repository
        self.conversation_flow = conversation_flow

    async def get_chat_response(self, chat_request: ChatRequest) -> ChatResponse:
        # Custom chat service implementation
        return ChatResponse(
            conversation_id=chat_request.conversation_id,
            message_id="custom-message-id",
            response="Custom response from service",
            created_at=datetime.now().isoformat()
        )
```

Enable your custom chat service in the configuration:

```yaml
conversation_flows:
  - name: "custom_flow"
    description: "Custom conversation flow"
    chat_service: "custom"
    agents:
      - "custom_agent"
```

### 4. Custom Templates

Create custom prompt templates:

```
# ingenious_extensions/templates/prompts/custom_prompt.j2
You are a {{ agent_type }} designed to help with {{ task }}.

User query: {{ query }}

Please provide a detailed response.
```

Use your template in code:

```python
from ingenious.utils.template_utils import render_template

prompt = render_template(
    "custom_prompt.j2",
    {"agent_type": "research assistant", "task": "academic research", "query": user_query}
)
```

### 5. Custom Data Models

Create custom data models:

```python
# ingenious_extensions/models/custom_data.py
from pydantic import BaseModel
from typing import List, Optional

class CustomData(BaseModel):
    id: str
    name: str
    attributes: List[str]
    metadata: Optional[dict] = None
```

### 6. Database Extensions

Extend database functionality:

```python
# ingenious_extensions/db/custom_repository.py
from ingenious.db import BaseRepository

class CustomRepository(BaseRepository):
    def __init__(self, db_client):
        super().__init__(db_client)

    async def custom_query(self, query_params):
        # Implementation
        pass
```

## Configuring Extensions

Extensions are configured through the main `config.yml` file:

```yaml
extensions:
  enabled: true
  custom_routes: true
  custom_agents: true
  custom_services: true
```

## Packaging Extensions

You can package your extensions for distribution:

1. Create a `setup.py` file in your extension directory:

```python
from setuptools import setup, find_packages

setup(
    name="ingenious-extension-name",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "insight-ingenious>=0.1.0",
    ],
    include_package_data=True,
)
```

2. Package your extension:

```bash
python setup.py sdist bdist_wheel
```

3. Install in another project:

```bash
pip install path/to/ingenious-extension-name-0.1.0.whl
```

## Extension Best Practices

1. **Maintain Compatibility**: Ensure your extensions are compatible with the core Insight Ingenious version
2. **Follow Naming Conventions**: Use consistent naming patterns for your extension components
3. **Write Tests**: Include tests for your extension functionality
4. **Document**: Add README and documentation for your extension
5. **Keep Dependencies Minimal**: Avoid introducing unnecessary dependencies
6. **Error Handling**: Implement proper error handling in your extension code
7. **Versioning**: Version your extensions to track changes and compatibility

## Example: Creating a Simple Extension

Here's a simple example of creating a custom extension that adds a calculator agent:

1. **Create the extension structure**:

```bash
cp -r ingenious/ingenious_extensions_template ingenious_extensions
```

2. **Create a custom calculator agent**:

```python
# ingenious_extensions/models/calculator_agent.py
from ingenious.models.agent import Agent
from ingenious.models.chat import ChatRequest, ChatResponse
from datetime import datetime
import re

class CalculatorAgent(Agent):
    def __init__(self, name: str, config):
        super().__init__(name, config)

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        # Extract mathematical expression using regex
        match = re.search(r'calculate\s+([\d\+\-\*\/\(\)\s]+)', request.message, re.IGNORECASE)

        if match:
            expression = match.group(1).strip()
            try:
                result = eval(expression)
                response = f"The result of {expression} is {result}"
            except Exception as e:
                response = f"Error calculating {expression}: {str(e)}"
        else:
            response = "Please provide a mathematical expression to calculate, e.g., 'calculate 2 + 2'"

        return ChatResponse(
            conversation_id=request.conversation_id,
            message_id=f"calc-{datetime.now().timestamp()}",
            response=response,
            created_at=datetime.now().isoformat()
        )
```

3. **Register the agent factory**:

```python
# ingenious_extensions/models/factory.py
from ingenious.models.agent import AgentFactory
from ingenious_extensions.models.calculator_agent import CalculatorAgent

class CustomAgentFactory(AgentFactory):
    def create_agent(self, agent_type: str, name: str, config, **kwargs):
        if agent_type == "calculator":
            return CalculatorAgent(name, config)
        # Fall back to default agent creation
        return super().create_agent(agent_type, name, config, **kwargs)
```

4. **Update the configuration**:

```yaml
# config.yml
agents:
  - name: "calculator"
    type: "calculator"
    system_prompt: "You are a calculator agent that can perform mathematical calculations."

conversation_flows:
  - name: "calculator_flow"
    description: "Calculator conversation flow"
    chat_service: "basic"
    agents:
      - "calculator"
```

5. **Use the calculator agent**:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "calc-test",
    "message": "calculate 2 + 2 * 3",
    "conversation_flow": "calculator_flow"
  }'
```

The agent will respond with: "The result of 2 + 2 * 3 is 8"

## Debugging Extensions

When debugging extensions, you can enable debug logging:

```yaml
log_level: "DEBUG"
```

You can also use the built-in test tools to test your extensions:

```bash
ingen_cli run-test-batch
```

## Conclusion

Extending Insight Ingenious allows you to customize the framework to your specific needs. By leveraging the extension points and following best practices, you can create powerful custom implementations while maintaining compatibility with the core framework.

For more examples, refer to the documentation in the `ingenious_extensions_template` directory.
