# Using the New DDD API Structure

This document shows how to use the new Domain-Driven Design API structure after the migration.

## For API Consumers (No Changes Required)

If you're consuming the APIs, **nothing changes**. All existing imports continue to work:

```python
# These imports still work exactly as before
from ingenious.api.routes.chat import router as chat_router
from ingenious.api.routes.diagnostic import router as diagnostic_router
from ingenious.api.routes.prompts import router as prompts_router
```

## For Developers (New DDD Structure)

### Using New Bounded Context Interfaces

```python
# New way - import directly from bounded contexts
from ingenious.chat.interfaces.rest_controllers import ChatController
from ingenious.diagnostics.interfaces.rest_controllers import DiagnosticsController
from ingenious.prompt_management.interfaces.rest_controllers import PromptManagementController

# Create controller instances
chat_controller = ChatController()
diagnostics_controller = DiagnosticsController()
prompts_controller = PromptManagementController()

# Access the FastAPI routers
chat_router = chat_controller.router
diagnostic_router = diagnostics_controller.router
prompts_router = prompts_controller.router
```

### Using in FastAPI Applications

```python
from fastapi import FastAPI
from ingenious.chat.interfaces.rest_controllers import router as chat_router
from ingenious.diagnostics.interfaces.rest_controllers import router as diagnostic_router

app = FastAPI()

# Include routers with prefixes
app.include_router(chat_router, prefix="/api/v1")
app.include_router(diagnostic_router, prefix="/api/v1")
```

### Working with Bounded Contexts

```python
# Chat bounded context
from ingenious.chat import (
    ChatRequest,
    ChatResponse,
    ChatController,
    ChatApplicationService
)

# Diagnostics bounded context
from ingenious.diagnostics import (
    DiagnosticCheck,
    SystemHealth,
    DiagnosticsController,
    DiagnosticsApplicationService
)

# Prompt Management bounded context
from ingenious.prompt_management import (
    PromptTemplate,
    PromptManagementController,
    UpdatePromptRequest
)
```

### Testing Bounded Context Controllers

```python
import pytest
from fastapi.testclient import TestClient
from ingenious.chat.interfaces.rest_controllers import ChatController

def test_chat_controller():
    controller = ChatController()
    client = TestClient(controller.router)

    response = client.post("/chat", json={
        "conversation_flow": "test_flow",
        "messages": []
    })
    assert response.status_code == 200
```

## Benefits of New Structure

1. **Clear Boundaries**: Each bounded context has its own API controllers
2. **Independent Testing**: Test each bounded context separately
3. **Team Scalability**: Different teams can own different bounded contexts
4. **Domain Alignment**: API structure matches business domains
5. **Gradual Migration**: Old imports still work during transition

## Migration Timeline

- **Phase 1** (Current): Legacy imports work, new structure available
- **Phase 2** (Future): Gradually update code to use new imports
- **Phase 3** (Future): Remove legacy compatibility layer

## Configuration Notes

The new controllers integrate with existing dependency injection and configuration systems. Ensure your environment has:

- Required Azure dependencies installed
- Proper configuration files or environment variables set
- Authentication and security dependencies configured

See the main configuration documentation for setup details.
