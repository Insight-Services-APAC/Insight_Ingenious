# Insight Ingenious

![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![uv](https://img.shields.io/badge/managed%20by-uv-blue.svg)

**Insight Ingenious** is a modern GenAI accelerator built with Domain-Driven Design principles, providing a comprehensive platform for AI agent interactions, file management, and configuration handling. The application features both a powerful CLI tool and a REST API server, designed to streamline AI-powered workflows.

## Features

### 🚀 Core Capabilities

- **AI Agent Integration**: Built-in support for Azure OpenAI and other LLM services
- **Chat Management**: Advanced conversation handling with message feedback and thread management
- **File Management**: Comprehensive file operations including upload, download, and directory management
- **Configuration Management**: Flexible configuration system with secret management
- **Security**: Authentication, authorization, and user management
- **Content Moderation**: Integrated content filtering and safety checks
- **Prompt Management**: Template-based prompt handling and version control
- **Health Monitoring**: System diagnostics and service health checking

### 🏗️ Architecture

Built using **Domain-Driven Design (DDD)** principles with clear separation of concerns:

- **Bounded Contexts**: Modular design with independent domains
- **Clean Architecture**: Separation between domain, application, infrastructure, and interface layers  
- **REST API**: Comprehensive FastAPI-based API with automatic documentation
- **CLI Interface**: Rich command-line interface for project management

### 📦 Bounded Contexts

- **Chat**: Conversation management and AI interactions
- **Configuration**: System settings and secret management
- **Diagnostics**: Health monitoring and system diagnostics
- **External Integrations**: LLM services and third-party API integration
- **File Management**: File operations and storage management
- **Prompt Management**: Template handling and prompt versioning
- **Security**: Authentication, authorization, and user management
- **Shared**: Cross-cutting concerns and common utilities

## Quick Start

### Prerequisites

- **Python 3.13+**
- **uv** package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Insight_Ingenious
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Initialize a new project:**
   ```bash
   uv run ingen init
   ```

4. **Configure your environment:**
   
   Edit the generated `profiles.yml` file and add your Azure OpenAI API credentials:
   ```yaml
   - name: dev
     models:
       - model: gpt-4o
         api_key: "YOUR_AZURE_OPENAI_API_KEY"
         base_url: "https://YOUR_RESOURCE_NAME.openai.azure.com/"
         api_version: "2023-05-15"
   ```

5. **Start the server:**
   ```bash
   uv run ingen run
   ```

6. **Access the application:**
   - **API Documentation**: http://localhost:8000/docs
   - **Interactive API**: http://localhost:8000/redoc

## CLI Usage

The `ingen` command provides powerful project management capabilities:

### Available Commands

```bash
# Initialize a new project
uv run ingen init

# Start the server
uv run ingen run [OPTIONS]

# Quick development mode
uv run ingen dev
```

### Command Options

**`ingen run`** - Start the Insight Ingenious server

- `--project-dir TEXT`: Path to config.yml file (default: ./config.yml)
- `--profile-dir TEXT`: Path to profiles.yml file (default: ./profiles.yml)  
- `--host TEXT`: Host to bind to (default: 127.0.0.1)
- `--port INTEGER`: Port to run the server on (default: 8000)

**`ingen init`** - Initialize a new project

Creates essential configuration files:
- `config.yml` - Main application configuration
- `profiles.yml` - API keys and secrets
- `.gitignore` - Git ignore rules
- `SETUP.md` - Detailed setup instructions

**`ingen dev`** - Quick development mode

Starts the server with default settings for the current directory.

## API Endpoints

The REST API provides comprehensive functionality across all bounded contexts:

### Chat Management
- `POST /api/v1/chat` - Process chat messages
- `GET /api/v1/conversations/{thread_id}` - Retrieve conversation history
- `PUT /api/v1/messages/{message_id}/feedback` - Submit message feedback

### File Management
- `POST /api/v1/files` - Create files
- `POST /api/v1/files/upload` - Upload files
- `GET /api/v1/files/{file_id}` - Retrieve file details
- `GET /api/v1/files/{file_id}/download` - Download files
- `DELETE /api/v1/files/{file_id}` - Delete files
- `POST /api/v1/directories` - Create directories

### Configuration
- `GET /api/v1/configuration` - Get current configuration
- `POST /api/v1/configuration` - Update configuration
- `GET /api/v1/secrets/{secret_name}` - Retrieve secrets
- `POST /api/v1/secrets` - Store secrets

### External Integrations
- `POST /api/v1/llm/completions` - Text completions
- `POST /api/v1/llm/chat` - Chat completions
- `POST /api/v1/moderation` - Content moderation
- `GET /api/v1/health` - Service health status

### Security
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/users` - Create users
- `GET /api/v1/users` - List users

### Prompt Management
- `GET /api/v1/prompts/list/{revision_id}` - List prompts
- `GET /api/v1/prompts/view/{revision_id}/{filename}` - View prompt
- `POST /api/v1/prompts/update/{revision_id}/{filename}` - Update prompt

## Configuration

### Main Configuration (`config.yml`)

```yaml
application:
  name: "my-project"
  environment: "dev"
  
server:
  host: "127.0.0.1"
  port: 8000
  
llm:
  default_model: "gpt-4o"
  max_tokens: 4000
  temperature: 0.7
```

### Profiles Configuration (`profiles.yml`)

```yaml
- name: dev
  models:
    - model: gpt-4o
      api_key: "${AZURE_OPENAI_API_KEY}"
      base_url: "${AZURE_OPENAI_ENDPOINT}"
      api_version: "2023-05-15"
```

### Environment Variables

- `INGENIOUS_WORKING_DIR`: Working directory for the application
- `INGENIOUS_PROJECT_PATH`: Path to config.yml
- `INGENIOUS_PROFILE_PATH`: Path to profiles.yml
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL

## Development

### Project Structure

```
ingenious/
├── __init__.py           # Main package initialization
├── cli.py               # CLI entry point
├── dependencies.py      # Dependency injection
├── main.py             # FastAPI application
├── chat/               # Chat bounded context
├── cli/                # CLI bounded context
├── configuration/      # Configuration bounded context
├── core/               # Core infrastructure
├── diagnostics/        # Diagnostics bounded context
├── external_integrations/ # External services integration
├── file_management/    # File operations
├── prompt_management/  # Prompt templates
├── security/           # Authentication & authorization
└── shared/             # Cross-cutting concerns
```

### Layer Architecture

Each bounded context follows clean architecture principles:

```
bounded_context/
├── domain/             # Business logic and rules
│   ├── entities.py     # Domain entities
│   ├── services.py     # Domain services  
│   └── models.py       # Domain models
├── application/        # Use cases and application services
│   ├── services.py     # Application services
│   └── use_cases.py    # Specific use cases
├── infrastructure/     # External concerns
│   ├── repositories.py # Data persistence
│   └── services.py     # External service implementations
└── interfaces/         # API and UI adapters
    └── rest_controllers.py # REST API endpoints
```

### Testing

Run tests using pytest:

```bash
uv run pytest
```

### Code Quality

The project uses several tools for code quality:

- **Ruff**: Fast Python linter and formatter
- **Pre-commit**: Git hooks for code quality
- **Type hints**: Full type annotation coverage

Run code quality checks:

```bash
# Format code
uv run ruff format

# Lint code  
uv run ruff check

# Run pre-commit hooks
uv run pre-commit run --all-files
```

## Deployment

### Docker (Coming Soon)

Docker support is planned for easy deployment and containerization.

### Production Considerations

- Configure proper secret management for production environments
- Set up monitoring and logging for production workloads
- Use environment-specific configuration files
- Implement proper backup strategies for file storage

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up the development environment
- Code standards and conventions
- Testing requirements
- Pull request process

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

1. Check the [documentation](docs/) for detailed guides
2. Review existing [issues](../../issues) for known problems
3. Create a new issue for bug reports or feature requests

## Acknowledgments

Built with modern Python tools and frameworks:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Pydantic](https://pydantic.dev/) - Data validation
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
