# API Reference

Complete API reference for the Ingenious framework, organized by bounded context and module.

## Core Modules

### ingenious.prompt_management

#### EnsembleManagementUseCase

Main use case class for managing prompt ensembles.

```python
from ingenious.prompt_management.application.ensemble_use_cases import EnsembleManagementUseCase
```

##### Constructor

```python
def __init__(
    self,
    llm_service: ILLMService,
    storage_service: AzureBlobStorageService
)
```

**Parameters:**
- `llm_service`: LLM service implementation (e.g., AzureOpenAIService)
- `storage_service`: Storage service for persisting results

##### Methods

**create_ensemble_configuration**

Create a new ensemble configuration.

```python
async def create_ensemble_configuration(
    self,
    name: str,
    description: str,
    main_prompt_template: str,
    sub_prompt_templates: List[Dict[str, Any]],
    reduce_prompt_template: str,
    strategy: str = "parallel",
    max_concurrent_agents: int = 5,
    timeout_seconds: int = 300,
    retry_count: int = 3,
    variables: Dict[str, Any] = None
) -> EnsembleConfiguration
```

**Parameters:**
- `name`: Unique name for the ensemble configuration
- `description`: Human-readable description
- `main_prompt_template`: Jinja2 template for the main prompt
- `sub_prompt_templates`: List of sub-prompt template definitions
- `reduce_prompt_template`: Template for aggregating results
- `strategy`: Execution strategy ("parallel", "sequential", "hierarchical")
- `max_concurrent_agents`: Maximum concurrent agents
- `timeout_seconds`: Timeout for execution
- `retry_count`: Number of retries for failed agents
- `variables`: Default variables for templates

**Returns:** `EnsembleConfiguration` object

**execute_ensemble**

Execute an ensemble with given variables.

```python
async def execute_ensemble(
    self,
    config_id: str,
    variables: Dict[str, Any],
    strategy_override: Optional[str] = None,
    timeout_override: Optional[int] = None
) -> EnsembleResult
```

**Parameters:**
- `config_id`: ID of the ensemble configuration to execute
- `variables`: Variables to substitute in templates
- `strategy_override`: Override the default execution strategy
- `timeout_override`: Override the default timeout

**Returns:** `EnsembleResult` object with execution results

**list_configurations**

List all ensemble configurations.

```python
async def list_configurations(
    self,
    filter_by_strategy: Optional[str] = None,
    limit: Optional[int] = None
) -> List[EnsembleConfiguration]
```

**get_configuration**

Get a specific ensemble configuration.

```python
async def get_configuration(self, config_id: str) -> EnsembleConfiguration
```

**update_configuration**

Update an existing ensemble configuration.

```python
async def update_configuration(
    self,
    config_id: str,
    updates: Dict[str, Any]
) -> EnsembleConfiguration
```

**delete_configuration**

Delete an ensemble configuration.

```python
async def delete_configuration(self, config_id: str) -> bool
```

#### Domain Models

**EnsembleConfiguration**

```python
from ingenious.prompt_management.domain.ensemble import EnsembleConfiguration

class EnsembleConfiguration(BaseModel):
    config_id: str
    name: str
    description: Optional[str]
    strategy: EnsembleStrategy
    main_prompt_template: str
    sub_prompt_templates: List[EnsemblePromptTemplate]
    reduce_prompt_template: str
    max_concurrent_agents: int = 5
    timeout_seconds: int = 300
    retry_count: int = 3
    variables: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
```

**EnsemblePromptTemplate**

```python
class EnsemblePromptTemplate(BaseModel):
    template_id: str
    name: str
    content: str  # Jinja2 template
    role: AgentRole
    priority: int = 1
    dependencies: List[str] = []
    variables: Dict[str, Any] = {}
    created_at: datetime
```

**EnsembleResult**

```python
class EnsembleResult(BaseModel):
    execution_id: str
    config_id: str
    variables: Dict[str, Any]
    strategy: EnsembleStrategy
    agent_executions: List[AgentExecution]
    final_result: Optional[str]
    executed_at: datetime
    completed_at: Optional[datetime]
    total_duration_seconds: Optional[float]
    success_rate: float
    total_token_usage: Dict[str, int]
    error: Optional[str]
```

**AgentExecution**

```python
class AgentExecution(BaseModel):
    execution_id: str
    agent_role: AgentRole
    template_id: str
    prompt: str
    response: Optional[str]
    metadata: Dict[str, Any]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]
    token_usage: Dict[str, int]

    @property
    def duration_seconds(self) -> Optional[float]

    @property
    def is_successful(self) -> bool
```

**Enums**

```python
from ingenious.prompt_management.domain.ensemble import EnsembleStrategy, AgentRole

class EnsembleStrategy(str, Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"

class AgentRole(str, Enum):
    ANALYZER = "analyzer"
    CRITIC = "critic"
    SYNTHESIZER = "synthesizer"
    SPECIALIST = "specialist"
    REVIEWER = "reviewer"
```

### ingenious.external_integrations

#### AzureOpenAIService

Azure OpenAI service implementation.

```python
from ingenious.external_integrations.infrastructure.openai_service import AzureOpenAIService
```

##### Constructor

```python
def __init__(
    self,
    azure_endpoint: str,
    api_key: str,
    api_version: str,
    model: str
)
```

##### Methods

**generate_response**

Generate a response using Azure OpenAI.

```python
async def generate_response(
    self,
    messages: List[ChatCompletionMessageParam],
    tools: Optional[List[ChatCompletionToolParam]] = None,
    tool_choice: Optional[str | Dict] = None,
    json_mode: bool = False,
    **kwargs
) -> ChatCompletionMessage
```

**Parameters:**
- `messages`: List of chat messages
- `tools`: Optional function tools
- `tool_choice`: Tool choice strategy
- `json_mode`: Enable JSON response format
- `**kwargs`: Additional OpenAI parameters (temperature, max_tokens, etc.)

**chat_completion**

Direct chat completion interface.

```python
async def chat_completion(
    self,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    **kwargs
) -> str
```

#### AzureBlobStorageService

Azure Blob Storage service implementation.

```python
from ingenious.external_integrations.infrastructure.blob_storage_service import AzureBlobStorageService
```

##### Constructor

```python
def __init__(
    self,
    account_url: str,
    credential: str | Any,
    container_name: str = "ingenious-data"
)
```

##### Methods

**store_ensemble_result**

Store ensemble execution result.

```python
async def store_ensemble_result(
    self,
    result: EnsembleResult
) -> str
```

**get_ensemble_result**

Retrieve ensemble execution result.

```python
async def get_ensemble_result(
    self,
    execution_id: str
) -> EnsembleResult
```

**list_ensemble_results**

List ensemble results with optional filtering.

```python
async def list_ensemble_results(
    self,
    config_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: Optional[int] = None
) -> List[EnsembleResult]
```

**store_blob**

Store arbitrary data as blob.

```python
async def store_blob(
    self,
    blob_name: str,
    data: bytes | str,
    metadata: Optional[Dict[str, str]] = None
) -> str
```

**get_blob**

Retrieve blob data.

```python
async def get_blob(
    self,
    blob_name: str
) -> bytes
```

### ingenious.configuration

#### ConfigurationService

Service for managing application configuration.

```python
from ingenious.configuration.application.services import ConfigurationService
```

##### Class Methods

**from_file**

Load configuration from file.

```python
@classmethod
def from_file(cls, file_path: str) -> ConfigurationService
```

**from_environment**

Load configuration from environment variables.

```python
@classmethod
def from_environment(cls) -> ConfigurationService
```

##### Methods

**get_setting**

Get a configuration setting.

```python
def get_setting(
    self,
    key: str,
    default: Any = None
) -> Any
```

**set_setting**

Set a configuration setting.

```python
async def set_setting(
    self,
    key: str,
    value: Any
) -> None
```

**validate**

Validate current configuration.

```python
async def validate(self) -> bool
```

**get_azure_openai_config**

Get Azure OpenAI configuration.

```python
def get_azure_openai_config(self) -> Dict[str, Any]
```

**get_azure_storage_config**

Get Azure Storage configuration.

```python
def get_azure_storage_config(self) -> Dict[str, Any]
```

#### AppConfiguration

Main configuration model.

```python
from ingenious.configuration.domain.models import AppConfiguration

class AppConfiguration(BaseModel):
    name: str
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    description: Optional[str] = None
    items: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
```

### ingenious.chat

#### ChatService

Service for managing chat conversations.

```python
from ingenious.chat.application.services import ChatService
```

##### Methods

**create_conversation**

Create a new conversation.

```python
async def create_conversation(
    self,
    title: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Conversation
```

**send_message**

Send a message in a conversation.

```python
async def send_message(
    self,
    conversation_id: str,
    content: str,
    role: str = "user",
    metadata: Optional[Dict[str, Any]] = None
) -> Message
```

**get_conversation**

Get conversation by ID.

```python
async def get_conversation(
    self,
    conversation_id: str
) -> Conversation
```

**list_conversations**

List conversations.

```python
async def list_conversations(
    self,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Conversation]
```

#### Domain Models

**Conversation**

```python
from ingenious.chat.domain.models import Conversation

class Conversation(BaseModel):
    conversation_id: str
    title: Optional[str]
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
```

**Message**

```python
class Message(BaseModel):
    message_id: str
    conversation_id: str
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
```

### ingenious.file_management

#### FileService

Service for file operations.

```python
from ingenious.file_management.application.services import FileService
```

##### Methods

**upload_file**

Upload a file.

```python
async def upload_file(
    self,
    file_data: bytes,
    filename: str,
    content_type: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None
) -> FileInfo
```

**download_file**

Download a file.

```python
async def download_file(
    self,
    file_id: str
) -> bytes
```

**list_files**

List files.

```python
async def list_files(
    self,
    prefix: Optional[str] = None,
    limit: Optional[int] = None
) -> List[FileInfo]
```

**delete_file**

Delete a file.

```python
async def delete_file(
    self,
    file_id: str
) -> bool
```

### ingenious.diagnostics

#### HealthService

Service for health checks and diagnostics.

```python
from ingenious.diagnostics.application.services import HealthService
```

##### Methods

**check_health**

Perform comprehensive health check.

```python
async def check_health(
    self,
    include_external: bool = True
) -> HealthStatus
```

**check_azure_services**

Check Azure service connectivity.

```python
async def check_azure_services(self) -> Dict[str, ServiceHealth]
```

**get_metrics**

Get system metrics.

```python
async def get_metrics(self) -> SystemMetrics
```

#### Domain Models

**HealthStatus**

```python
from ingenious.diagnostics.domain.models import HealthStatus

class HealthStatus(BaseModel):
    status: str  # "healthy", "degraded", "unhealthy"
    timestamp: datetime
    services: Dict[str, ServiceHealth]
    metrics: SystemMetrics
```

**ServiceHealth**

```python
class ServiceHealth(BaseModel):
    name: str
    status: str
    response_time_ms: Optional[float]
    error: Optional[str]
    last_check: datetime
```

## CLI API

### Command Structure

The CLI follows this pattern:
```bash
ingen [global-options] <command> [command-options] [arguments]
```

### Global Options

- `--verbose, -v`: Enable verbose output
- `--quiet, -q`: Suppress non-essential output
- `--config`: Specify configuration file
- `--workdir`: Set working directory
- `--format`: Output format (json, yaml, table)

### Main Commands

**init**: Initialize a new project
```bash
ingen init
```

**run**: Start production server
```bash
ingen run [--host HOST] [--port PORT] [--project-dir DIR] [--profile-dir DIR]
```

**dev**: Start development server
```bash
ingen dev
```

### Ensemble Commands

**ensemble create**: Create new ensemble configuration
```bash
ingen ensemble create NAME --config CONFIG_FILE [--strategy STRATEGY] [--max-agents N] [--timeout SECONDS]
```

**ensemble create-predefined**: Create predefined ensemble
```bash
ingen ensemble create-predefined TYPE NAME [--description DESC]
```

**ensemble execute**: Execute ensemble
```bash
ingen ensemble execute CONFIG_ID --input FILE|--text TEXT [--output FILE]
```

**ensemble list**: List configurations
```bash
ingen ensemble list [--limit N] [--prefix PREFIX]
```

**ensemble get**: Get ensemble details
```bash
ingen ensemble get CONFIG_ID [--templates]
```

**ensemble executions**: List executions
```bash
ingen ensemble executions [--config-id ID] [--status STATUS] [--limit N]
```

**ensemble result**: Get execution result
```bash
ingen ensemble result EXECUTION_ID [--agents] [--output FILE]
```

**ensemble sample-config**: Generate sample config
```bash
ingen ensemble sample-config OUTPUT_FILE [--ensemble-type TYPE]
```

## Error Handling

### Exception Classes

```python
from ingenious.shared.exceptions import (
    IngeniousError,           # Base exception
    ValidationError,          # Validation failures
    BusinessLogicError,       # Business rule violations
    ExternalServiceError,     # External service failures
    ConfigurationError,       # Configuration issues
    AuthenticationError,      # Authentication failures
    AuthorizationError        # Authorization failures
)
```

### Error Response Format

All API errors follow this format:

```python
{
    "error": {
        "type": "ValidationError",
        "message": "Human-readable error message",
        "details": {
            "field": "specific field that failed",
            "value": "invalid value",
            "constraint": "validation rule that was violated"
        },
        "timestamp": "2024-01-01T12:00:00Z",
        "request_id": "unique-request-identifier"
    }
}
```

## Response Formats

### Success Response

```python
{
    "data": {
        # Response payload
    },
    "meta": {
        "timestamp": "2024-01-01T12:00:00Z",
        "request_id": "unique-request-identifier",
        "version": "1.0.0"
    }
}
```

### Paginated Response

```python
{
    "data": [
        # Array of items
    ],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "pages": 5,
        "has_next": true,
        "has_prev": false
    },
    "meta": {
        "timestamp": "2024-01-01T12:00:00Z",
        "request_id": "unique-request-identifier"
    }
}
```

## Type Definitions

### Common Types

```python
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from uuid import UUID

# Type aliases
ConfigDict = Dict[str, Any]
VariableDict = Dict[str, Any]
MetadataDict = Dict[str, str]
TokenUsage = Dict[str, int]

# Common ID types
EntityId = Union[str, UUID]
ConfigId = str
ExecutionId = str
ConversationId = str
MessageId = str
```

### API Response Types

```python
# Generic API response
class APIResponse(BaseModel):
    data: Any
    meta: Dict[str, Any]

# Error response
class ErrorResponse(BaseModel):
    error: Dict[str, Any]

# Paginated response
class PaginatedResponse(BaseModel):
    data: List[Any]
    pagination: Dict[str, Any]
    meta: Dict[str, Any]
```

This API reference provides comprehensive coverage of all public interfaces in the Ingenious framework. For implementation examples, see the [Examples](examples/) directory and [Getting Started Guide](getting-started.md).
