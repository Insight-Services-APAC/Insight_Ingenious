# API Documentation

This document provides a detailed reference for the Insight Ingenious REST API.

## Base URL

The base URL for all API endpoints is:

```
http://<host>:<port>/api/v1
```

By default, the API server runs on `127.0.0.1:8000`, making the base URL:

```
http://127.0.0.1:8000/api/v1
```

## Authentication

The API supports HTTP Basic Authentication. You can configure authentication credentials in the `config.yml` file:

```yaml
web_configuration:
  authentication:
    enabled: true
    username: "your_username"
    password: "your_password"
```

To authenticate, include the `Authorization` header with a Base64-encoded "username:password" string:

```
Authorization: Basic <base64-encoded-credentials>
```

## Common Headers

All API requests should include the following headers:

- `Content-Type: application/json` (for POST and PUT requests)
- `Accept: application/json`
- `Authorization: Basic <credentials>` (if authentication is enabled)

## Endpoints

### Chat Endpoint

#### POST /chat

Create a new chat message or continue an existing conversation.

**Request Body:**

```json
{
  "conversation_id": "unique-conversation-id",
  "message": "User message here",
  "conversation_flow": "default",
  "metadata": {
    "key1": "value1",
    "key2": "value2"
  }
}
```

**Response:**

```json
{
  "conversation_id": "unique-conversation-id",
  "message_id": "message-id",
  "response": "AI response here",
  "created_at": "2023-05-01T12:34:56.789Z",
  "metadata": {
    "model": "gpt-4o",
    "prompt_tokens": 123,
    "completion_tokens": 456,
    "total_tokens": 579
  }
}
```

#### GET /chat/{conversation_id}

Get the history of a conversation.

**Response:**

```json
{
  "conversation_id": "unique-conversation-id",
  "messages": [
    {
      "message_id": "message-id-1",
      "role": "user",
      "content": "User message here",
      "created_at": "2023-05-01T12:34:56.789Z"
    },
    {
      "message_id": "message-id-2",
      "role": "assistant",
      "content": "AI response here",
      "created_at": "2023-05-01T12:35:00.123Z"
    }
  ]
}
```

### Message Feedback Endpoint

#### POST /message_feedback

Submit feedback for a message.

**Request Body:**

```json
{
  "conversation_id": "unique-conversation-id",
  "message_id": "message-id",
  "feedback_type": "thumbs_up",
  "comment": "Optional user comment"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Feedback recorded"
}
```

### Diagnostic Endpoint

#### GET /diagnostic/health

Check the health of the API.

**Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "components": {
    "database": "ok",
    "openai": "ok"
  }
}
```

### Prompts Endpoint

#### GET /prompts

Get a list of available prompts.

**Response:**

```json
{
  "prompts": [
    {
      "id": "prompt-id-1",
      "name": "Customer Service",
      "description": "Prompt for customer service agent"
    },
    {
      "id": "prompt-id-2",
      "name": "Technical Support",
      "description": "Prompt for technical support agent"
    }
  ]
}
```

#### GET /prompts/{prompt_id}

Get a specific prompt.

**Response:**

```json
{
  "id": "prompt-id-1",
  "name": "Customer Service",
  "description": "Prompt for customer service agent",
  "content": "You are a helpful customer service agent...",
  "metadata": {
    "author": "John Doe",
    "created_at": "2023-05-01T12:34:56.789Z",
    "last_updated": "2023-05-02T12:34:56.789Z"
  }
}
```

## Error Handling

The API returns standard HTTP status codes to indicate the success or failure of a request:

- `200 OK`: The request was successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

Error responses include a JSON object with details:

```json
{
  "error": {
    "code": "error_code",
    "message": "Error message",
    "details": {
      "field": "Error details"
    }
  }
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Rate limits are configurable in the `config.yml` file:

```yaml
web_configuration:
  rate_limit:
    enabled: true
    requests_per_minute: 60
```

When a rate limit is exceeded, the API returns a `429 Too Many Requests` status code.

## Extensions

You can extend the API with custom endpoints by creating a custom API routes class in your extension:

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

Enable custom routes in your configuration:

```yaml
extensions:
  enabled: true
  custom_routes: true
```

## API Versioning

The API uses a version prefix in the URL (`/api/v1/`) for versioning. Future versions of the API may be released under different prefixes (e.g., `/api/v2/`).
