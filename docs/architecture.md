# Insight Ingenious Architecture

This document outlines the architectural design of Insight Ingenious, explaining the key components, their interactions, and the design principles behind the system.

## System Overview

Insight Ingenious is a framework for building, managing, and deploying multi-agent AI conversations. The system is structured as a modular, extensible application with several key components:

```
           ┌───────────────┐
           │   Client      │
           │ Interfaces    │
           └──────┬────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │   FastAgentAPI      │
        │ ┌───────────────┐   │
        │ │   Routes      │   │
        │ └──────┬────────┘   │
        │        │            │
        │ ┌──────▼────────┐   │
        │ │   Services    │   │
        │ └──────┬────────┘   │
        │        │            │
        │ ┌──────▼────────┐   │
        │ │  Config       │   │
        │ └───────────────┘   │
        └─────────┬───────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │      Agents         │
        └─────────┬───────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │  Data Storage Layer │
        │ ┌───────────────┐   │
        │ │  Databases    │   │
        │ ├───────────────┤   │
        │ │ File Storage  │   │
        │ └───────────────┘   │
        └─────────────────────┘
```

## Key Components

### 1. Client Interfaces

- **FastAPI REST Interface**: The primary way to interact with the system programmatically
- **CLI Interface**: Command-line tools for administration, testing, and initialization
- **ChainLit UI**: Web-based user interface for interactive conversations
- **Prompt Tuner**: Web interface for managing and tuning prompts

### 2. Core Components

- **FastAgentAPI**: The main application class that initializes the system and routes
- **Configuration System**: Manages application settings and profiles
- **Services**: Business logic implementation
  - **ChatService**: Handles chat interactions and agent orchestration
  - **MessageFeedbackService**: Manages user feedback on messages
  - **External Services**: Integrations with external systems like OpenAI

### 3. Agents System

- **Agent Model**: Base models for defining agent behaviors
- **AgentChat**: Represents chat interactions between agents
- **Agent Orchestration**: Manages the flow of conversations between multiple agents

### 4. Data Storage

- **Chat History**: Stores conversation history
- **File Storage**: Manages file attachments and document storage
- **Database Backends**: Multiple database support
  - SQLite
  - Azure Cosmos DB

## Design Principles

Insight Ingenious follows several key design principles:

1. **Modularity**: The system is divided into loosely coupled components that can be developed and tested independently.

2. **Extensibility**: The framework is designed to be extended with custom agents, templates, and APIs.

3. **Configuration-Driven**: Much of the system behavior is driven by configuration files rather than code changes.

4. **Abstraction Layers**: Abstract interfaces are used to ensure components depend on abstractions rather than concrete implementations.

## Extension Points

Insight Ingenious provides several extension points:

1. **Custom Agent Types**: Create custom agents by extending the base Agent class.

2. **API Extensions**: Add custom API routes to extend the system's functionality.

3. **Storage Backends**: Implement custom storage backends for chat history and files.

4. **Templates**: Define custom prompt templates and conversation flows.

## Data Flow

1. User requests enter through the API or CLI interface.
2. Requests are routed to the appropriate service.
3. Services use agents to process the request.
4. Agents interact with external services (like LLMs) and data storage.
5. Responses flow back through the service and are returned to the user.

## Security Model

Insight Ingenious supports multiple security features:

1. **API Authentication**: Configure API keys or OAuth for API access.
2. **Azure Key Vault Integration**: Secret management with Azure Key Vault.
3. **Content Filtering**: Filter inappropriate content in conversations.

## Deployment Options

The system supports multiple deployment options:

1. **Local Development**: Run locally for development and testing.
2. **Docker Containers**: Containerized deployment for production.
3. **Cloud Deployment**: Deploy to cloud platforms like Azure.

## Directory Structure

The Insight Ingenious codebase follows a structured organization:

```
ingenious/
├── __init__.py
├── cli.py                      # Command-line interface
├── main.py                     # FastAPI application
├── application/                # Application logic
│   ├── factory.py
│   ├── repository/             # Repository implementations
│   └── service/                # Service implementations
├── common/                     # Common utilities
│   ├── config/                 # Configuration handling
│   ├── di/                     # Dependency injection
│   ├── errors/                 # Error handling
│   ├── logging/                # Logging utilities
│   └── utils/                  # General utilities
├── domain/                     # Domain models and interfaces
│   ├── interfaces/
│   └── model/
├── extensions/                 # Extension loader and templates
│   ├── loader.py
│   └── template/
├── infrastructure/             # Infrastructure services
│   └── storage/                # Storage implementations
└── presentation/               # Presentation layer
    ├── api/                    # API routes
    ├── chainlit/               # ChainLit UI
    └── templates/              # Jinja2 templates
```

This architecture provides a clean separation of concerns and makes the system easy to understand, extend, and maintain.
