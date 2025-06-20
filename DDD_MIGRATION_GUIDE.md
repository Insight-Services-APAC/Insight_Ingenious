# Domain-Driven Design Migration Guide

This document outlines the migration from the legacy module structure to the new Domain-Driven Design (DDD) architecture.

## New Architecture Overview

The application is now organized into bounded contexts, each following DDD layered architecture:

```
ingenious/
├── chat/                    # Chat bounded context
│   ├── domain/             # Core business logic
│   ├── application/        # Use cases and app services
│   ├── infrastructure/     # External adapters
│   └── interfaces/         # REST API controllers
├── configuration/          # Configuration management
├── diagnostics/           # System health and monitoring
├── external_integrations/ # Third-party integrations
├── file_management/       # File operations
├── prompt_management/     # Prompt templates
├── security/              # Authentication/authorization
├── shared/                # Cross-cutting concerns
└── legacy/                # Backward compatibility
```

## Migration Strategy

### Phase 1: Backward Compatibility (Current)
- All existing imports continue to work
- Legacy modules provide aliases to new locations
- No breaking changes to existing code

### Phase 2: Gradual Migration
- Update imports to use new bounded context modules
- Migrate one bounded context at a time
- Update tests to use new structure

### Phase 3: Legacy Cleanup
- Remove legacy compatibility layer
- Clean up old module structure
- Update documentation

## Import Migration Examples

### Before (Legacy)
```python
from ingenious.models.chat import ChatRequest, ChatResponse
from ingenious.services.chat_service import ChatService
from ingenious.external_services.openai_service import OpenAIService
```

### After (New DDD Structure)
```python
from ingenious.chat.domain.models import ChatRequest, ChatResponse
from ingenious.chat.application.services import ChatApplicationService
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService
```

## Bounded Context Details

### Chat Bounded Context
- **Domain**: Message, Thread, ChatSession entities
- **Application**: ChatUseCase, ConversationUseCase
- **Infrastructure**: LegacyChatServiceAdapter, repositories
- **Interfaces**: ChatController (REST API)

### Configuration Bounded Context
- **Domain**: Configuration services and repositories
- **Infrastructure**: FileSystemConfigurationRepository, AzureKeyVaultSecretService

### External Integrations Bounded Context
- **Domain**: ILLMService, IContentModerationService interfaces
- **Infrastructure**: AzureOpenAIService, OpenAIContentModerationService

### File Management Bounded Context
- **Domain**: File, Directory entities and storage services
- **Infrastructure**: File system and cloud storage adapters

### Prompt Management Bounded Context
- **Domain**: PromptTemplate, PromptLibrary entities
- **Infrastructure**: Jinja2RenderingService, file-based repositories

### Diagnostics Bounded Context
- **Domain**: DiagnosticCheck, SystemHealth entities
- **Infrastructure**: Health check implementations

### Security Bounded Context
- **Domain**: User, AuthenticationToken entities
- **Infrastructure**: Authentication and authorization services

### Shared Kernel
- **Common**: DomainException, DomainEvent, utilities
- **Cross-cutting**: Logging, validation, event handling

## Benefits of New Architecture

1. **Clear Separation of Concerns**: Each layer has specific responsibilities
2. **Testability**: Easy to unit test domain logic in isolation
3. **Maintainability**: Changes are localized to specific contexts
4. **Scalability**: Bounded contexts can evolve independently
5. **Domain Focus**: Business logic is clearly separated from infrastructure

## Migration Checklist

- [ ] Review new bounded context structure
- [ ] Identify dependencies between contexts
- [ ] Update imports gradually
- [ ] Migrate tests to new structure
- [ ] Update documentation
- [ ] Remove legacy compatibility layer (final phase)

## Support

For questions about the migration, please refer to:
- This migration guide
- Individual bounded context documentation
- Legacy compatibility module for current aliases
