"""
CLI infrastructure services.

This module contains the infrastructure implementations of domain services
for the CLI bounded context.
"""

import os
from pathlib import Path
from typing import List

from rich.console import Console
from rich.theme import Theme

from ..domain.entities import ProjectConfig, ServerConfig
from ..domain.services import IProjectService, IServerService, ITemplateService

# Configure rich console
custom_theme = Theme(
    {
        "info": "dim cyan",
        "warning": "dark_orange",
        "danger": "bold red",
        "error": "bold red",
        "debug": "khaki1",
    }
)
console = Console(theme=custom_theme)


class FileSystemProjectService(IProjectService):
    """File system implementation of project service."""

    async def create_project(self, config: ProjectConfig) -> None:
        """Create a new project directory structure."""
        project_path = Path(config.path)

        # Create project directory if it doesn't exist
        project_path.mkdir(parents=True, exist_ok=True)

        # Create basic project structure
        (project_path / "data").mkdir(exist_ok=True)
        (project_path / "files").mkdir(exist_ok=True)
        (project_path / ".tmp").mkdir(exist_ok=True)

        console.print(
            f"[info]✅ Created project directory structure for '{config.name}'[/info]"
        )

    async def project_exists(self, project_path: Path) -> bool:
        """Check if a project exists at the given path."""
        return project_path.exists() and project_path.is_dir()

    async def get_project_config(self, project_path: Path) -> ProjectConfig:
        """Get project configuration from the given path."""
        # For now, return a basic config based on path
        project_name = project_path.name
        return ProjectConfig(
            name=project_name,
            path=str(project_path),
        )

    async def validate_project(self, project_path: Path) -> bool:
        """Validate if a project exists and is properly configured."""
        config_file = project_path / "config.yml"
        profiles_file = project_path / "profiles.yml"

        if not config_file.exists():
            console.print(f"[error]❌ config.yml not found in {project_path}[/error]")
            console.print(
                "[info]Run 'ingen init' to create configuration files.[/info]"
            )
            return False

        if not profiles_file.exists():
            console.print(f"[error]❌ profiles.yml not found in {project_path}[/error]")
            console.print(
                "[info]Run 'ingen init' to create configuration files.[/info]"
            )
            return False

        return True


class UvicornServerService(IServerService):
    """Uvicorn implementation of server service."""

    async def start_server(self, config: ServerConfig) -> None:
        """Start the server using uvicorn."""
        try:
            # Set environment variables
            if config.project_dir:
                os.environ["INGENIOUS_WORKING_DIR"] = config.project_dir
            else:
                os.environ["INGENIOUS_WORKING_DIR"] = os.getcwd()

            if config.profile_dir:
                os.environ["INGENIOUS_PROFILES_DIR"] = config.profile_dir
            else:
                os.environ["INGENIOUS_PROFILES_DIR"] = os.getcwd()

            # Check for required config files
            working_dir = Path(os.environ["INGENIOUS_WORKING_DIR"])
            config_file = working_dir / "config.yml"
            profiles_file = working_dir / "profiles.yml"

            if not config_file.exists():
                console.print("[error]❌ config.yml not found![/error]")
                console.print(f"[info]Looking in: {config_file}[/info]")
                console.print("[info]Run 'ingen init' to create config files.[/info]")
                raise FileNotFoundError("config.yml not found")

            if not profiles_file.exists():
                console.print("[error]❌ profiles.yml not found![/error]")
                console.print(f"[info]Looking in: {profiles_file}[/info]")
                console.print("[info]Run 'ingen init' to create config files.[/info]")
                raise FileNotFoundError("profiles.yml not found")

            console.print(
                f"[info]🚀 Starting Insight Ingenious server on {config.host}:{config.port}[/info]"
            )
            console.print(f"[info]📁 Project directory: {working_dir}[/info]")
            console.print(f"[info]📄 Using config file: {config_file}[/info]")
            console.print(f"[info]🔐 Using profiles file: {profiles_file}[/info]")

            # Start server message
            console.print("[info]🎯 Server starting up...[/info]")
            console.print("[info]💡 Press Ctrl+C to stop the server[/info]")
            console.print()

            # Import FastAPI app after setting environment variables
            from ingenious.configuration.domain.models import MinimalConfig
            from ingenious.main import FastAgentAPI

            # Initialize app
            minimal_config = MinimalConfig()
            app_instance = FastAgentAPI(minimal_config)

            # Run uvicorn server
            import uvicorn

            uvicorn.run(
                app_instance.app, host=config.host, port=config.port, log_level="info"
            )

        except ImportError as e:
            console.print(f"[error]❌ Import error: {e}[/error]")
            raise
        except Exception as e:
            console.print(f"[error]❌ Server startup failed: {e}[/error]")
            raise

    async def stop_server(self) -> bool:
        """Stop the running server."""
        # For now, just return True as we don't track server processes
        return True

    async def is_running(self) -> bool:
        """Check if the server is currently running."""
        # For now, just return False as we don't track server processes
        return False

    async def validate_server_config(self, config: ServerConfig) -> bool:
        """Validate server configuration."""
        # Check port range
        if not (1 <= config.port <= 65535):
            return False

        # Check host format (basic validation)
        if not config.host:
            return False

        return True


class TemplateGenerationService(ITemplateService):
    """Service for generating project template files."""

    async def generate_config_template(
        self, project_name: str, output_path: Path
    ) -> None:
        """Generate configuration template files."""
        await self._create_config_yml(project_name, output_path)
        await self._create_profiles_yml(project_name, output_path)

    async def generate_gitignore(self, output_path: Path) -> None:
        """Generate .gitignore file."""
        gitignore_path = output_path / ".gitignore"
        if not gitignore_path.exists():
            gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Project specific
profiles.yml
.tmp/
files/
data/
*.log

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""
            with open(gitignore_path, "w") as f:
                f.write(gitignore_content)
            console.print("[info]✅ Created .gitignore file.[/info]")

    async def generate_readme(self, project_name: str, output_path: Path) -> None:
        """Generate README file."""
        readme_path = output_path / "SETUP.md"
        readme_content = f"""# {project_name} - Setup Guide

Welcome to your new Insight Ingenious project! This guide will help you get started.

## 🚀 Quick Start

1. **Configure your API keys** (Required):
   ```bash
   # Edit profiles.yml and add your Azure OpenAI API key
   # Replace REPLACE_WITH_YOUR_AZURE_OPENAI_API_KEY with your actual key
   ```

2. **Start the server**:
   ```bash
   ingen run
   ```

3. **Access the API**:
   - API Documentation: http://127.0.0.1:8000/docs
   - Interactive API: http://127.0.0.1:8000/redoc

## 📋 Configuration Files

### config.yml
Contains non-sensitive configuration settings:
- Model configurations
- Logging settings
- Database settings
- Web interface settings

### profiles.yml
Contains sensitive information (API keys, passwords):
- **⚠️ Keep this file secure**
- **⚠️ Do not commit to version control**
- Contains API keys and authentication credentials

## 🔧 Available Commands

```bash
# Start the REST API server
ingen run

# Start with custom host/port
ingen run --host 0.0.0.0 --port 9000

# Quick development mode (same as run but simpler)
ingen dev

# Initialize a new project (if needed)
ingen init
```

## 📁 Project Structure

```
{project_name}/
├── config.yml          # Main configuration (non-sensitive settings)
├── profiles.yml        # Sensitive credentials (API keys, not in git)
├── .gitignore          # Git ignore rules (excludes profiles.yml)
├── SETUP.md            # This setup guide
├── data/               # Data files and datasets
├── files/              # Project files and documents
└── .tmp/              # Temporary files (auto-created)
```

## 🛠️ Troubleshooting

### Server won't start
1. **Check configuration files exist:**
   - `config.yml` should exist in your project directory
   - `profiles.yml` should exist in your project directory
   - If missing, run `ingen init` to create them

2. **Verify API keys:**
   - Open `profiles.yml` and check your Azure OpenAI API key
   - Ensure the `base_url` points to your Azure OpenAI resource

3. **Check port availability:**
   - Default port is 8000
   - Try a different port: `ingen run --port 8001`
   - Check if another service is using the port

### API key issues
1. **Get your Azure OpenAI credentials:**
   - API key: Azure Portal > Your OpenAI Resource > Keys and Endpoint
   - Endpoint: Format should be `https://YOUR_RESOURCE.openai.azure.com/openai/deployments/MODEL_NAME/chat/completions?api-version=2024-08-01-preview`

2. **Update profiles.yml:**
   - Replace `REPLACE_WITH_YOUR_AZURE_OPENAI_API_KEY` with your actual key
   - Replace `REPLACE_WITH_YOUR_RESOURCE_NAME` with your Azure resource name
   - Restart the server after making changes

### File permission issues
- Ensure the current user has read/write access to the project directory
- Check that `.tmp/`, `data/`, and `files/` directories are writable

### Need help?
- Check the API documentation at `/docs`
- Review the configuration files
- Ensure all required dependencies are installed

## 🎯 Next Steps

1. **Update your API keys** in `profiles.yml`
2. **Customize your configuration** in `config.yml`
3. **Start building** with the AI agents!

Happy coding! 🎉
"""
        with open(readme_path, "w") as f:
            f.write(readme_content)
        console.print("[info]✅ Created SETUP.md with project documentation.[/info]")

    async def generate_template(self, template_name: str, output_path: Path) -> bool:
        """Generate a project template."""
        try:
            # For now, just call the config template method
            await self.generate_config_template(template_name, output_path)
            return True
        except Exception:
            return False

    async def list_templates(self) -> List[str]:
        """List available project templates."""
        return ["basic", "react", "vue", "angular"]

    async def _create_config_yml(self, project_name: str, output_path: Path) -> None:
        """Create config.yml file."""
        config_path = output_path / "config.yml"
        config_content = f"""# Insight Ingenious Configuration File
# Project: {project_name}
#
# This file contains non-sensitive configuration settings.
# For sensitive data (API keys, passwords), see profiles.yml

# ================================
# PROFILE SELECTION
# ================================
# Specify which profile to use from profiles.yml
# Common values: dev, staging, prod
profile: dev

# ================================
# AI MODELS CONFIGURATION
# ================================
# Configure the AI models your agents will use
models:
  - model: gpt-4o  # Model name in your Azure OpenAI deployment
    api_type: azure  # Use 'azure' for Azure OpenAI, 'openai' for OpenAI directly
    api_version: "2024-08-01-preview"  # Azure OpenAI API version

# ================================
# LOGGING SETTINGS
# ================================
logging:
  root_log_level: info     # Global log level: debug, info, warning, error
  log_level: debug         # Application-specific log level

# ================================
# CHAT HISTORY STORAGE
# ================================
# Choose how to store conversation history
chat_history:
  database_type: sqlite               # Options: sqlite, cosmos
  database_path: ./.tmp/chat_history.db  # Path for SQLite database
  database_name: {project_name}_chats    # Database name (for Cosmos DB)
  memory_path: ./.tmp                 # Temporary memory files location

# ================================
# CHAT SERVICE TYPE
# ================================
# Defines the conversation engine
chat_service:
  type: multi_agent  # Use multi-agent conversation system

# ================================
# TOOL SERVICES
# ================================
# Enable/disable additional agent tools
tool_service:
  enable: true  # Set to false to disable tool usage

# ================================
# WEB INTERFACE SETTINGS
# ================================
web_configuration:
  type: fastapi          # Web framework (currently only FastAPI supported)
  ip_address: "127.0.0.1"  # IP address to bind to (127.0.0.1 for local only)
  port: 8000            # Port to run the web server on

# ================================
# CHAINLIT UI (Optional)
# ================================
# Enable the Chainlit chat interface
chainlit_configuration:
  enable: true  # Set to true to enable the web chat UI

# ================================
# PROMPT TUNER (Optional)
# ================================
# Tool for developing and testing prompts
prompt_tuner:
  mode: "fast_api"  # Options: fast_api, flask

# ================================
# AZURE SEARCH (Optional)
# ================================
# Configure Azure Cognitive Search for knowledge bases
azure_search_services:
  - service: knowledge-base
    endpoint: https://YOUR_SEARCH_SERVICE.search.windows.net

# ================================
# DATABASE CONNECTIONS (Optional)
# ================================
# Local SQLite database for SQL agents
local_sql_db:
  database_path: /tmp/sample.db
  sample_csv_path: ./sample_data/data.csv
  sample_database_name: sample_data

# Azure SQL Database configuration
azure_sql_services:
  database_name: your_database
  table_name: your_table

# ================================
# FILE STORAGE
# ================================
# Configure where files are stored
file_storage:
  revisions:
    enable: true
    storage_type: local        # Options: local, azure
    container_name: revisions  # For Azure storage
    path: ./files             # Local storage path
    add_sub_folders: true
  data:
    enable: true
    storage_type: local
    container_name: data
    path: ./files
    add_sub_folders: true
"""
        with open(config_path, "w") as f:
            f.write(config_content)
        console.print("[info]✅ Created config.yml with helpful documentation.[/info]")

    async def _create_profiles_yml(self, project_name: str, output_path: Path) -> None:
        """Create profiles.yml file."""
        profiles_path = output_path / "profiles.yml"
        profiles_content = f"""# Insight Ingenious Profiles Configuration
# Project: {project_name}
#
# 🚨 IMPORTANT: This file contains sensitive information (API keys, passwords)
# - Keep this file secure and do not commit it to version control
# - The .gitignore file excludes this file by default
# - Copy this to a secure location for production deployments

# ================================
# DEVELOPMENT PROFILE
# ================================
- name: dev
  # ================================
  # AI MODEL CREDENTIALS
  # ================================
  models:
    - model: gpt-4o
      # 🔑 Your Azure OpenAI API key - REQUIRED
      # Get this from Azure Portal > Your OpenAI Resource > Keys and Endpoint
      api_key: "REPLACE_WITH_YOUR_AZURE_OPENAI_API_KEY"

      # 🌐 Your Azure OpenAI endpoint - REQUIRED
      # Format: https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview
      # Replace YOUR_RESOURCE_NAME with your actual Azure OpenAI resource name
      base_url: "https://REPLACE_WITH_YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

  # ================================
  # CHAT HISTORY DATABASE
  # ================================
  chat_history:
    # For Cosmos DB (optional), provide connection string
    database_connection_string: ""

  # ================================
  # AZURE SEARCH CREDENTIALS (Optional)
  # ================================
  azure_search_services:
    - service: knowledge-base
      # 🔑 Azure Search admin key - OPTIONAL
      key: "YOUR_AZURE_SEARCH_ADMIN_KEY_HERE"

  # ================================
  # AZURE SQL CREDENTIALS (Optional)
  # ================================
  azure_sql_services:
    # SQL Server connection string - OPTIONAL
    database_connection_string: "Server=tcp:your-server.database.windows.net,1433;Database=your-db;User ID=your-user;Password=your-password;Encrypt=true;TrustServerCertificate=false;Connection Timeout=30;"

  # ================================
  # WEB AUTHENTICATION
  # ================================
  web_configuration:
    authentication:
      enable: true
      type: basic
      # 🔑 Basic auth credentials for API access
      # Change these default credentials!
      username: "admin"
      password: "CHANGE_THIS_PASSWORD_FOR_SECURITY"

  # ================================
  # CHAINLIT AUTHENTICATION (Optional)
  # ================================
  chainlit_configuration:
    enable: true
    authentication:
      enable: false  # Set to true to require GitHub OAuth
      # For GitHub OAuth (optional):
      github_client_id: "YOUR_GITHUB_CLIENT_ID"
      github_secret: "YOUR_GITHUB_SECRET"

  # ================================
  # AZURE BLOB STORAGE (Optional)
  # ================================
  file_storage:
    revisions:
      url: https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/
      authentication_method: default_credential  # Options: msi, default_credential
    data:
      url: https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net/
      authentication_method: default_credential

  # ================================
  # EXTERNAL INTEGRATIONS (Optional)
  # ================================
  receiver_configuration:
    enable: false
    api_url: "https://your-webhook-endpoint.com/api/ai-response/publish"
    api_key: "YOUR_WEBHOOK_API_KEY"

# ================================
# PRODUCTION PROFILE TEMPLATE
# ================================
# Uncomment and configure for production:
# - name: prod
#   models:
#     - model: gpt-4o
#       api_key: "PRODUCTION_API_KEY"
#       base_url: "https://prod-resource.openai.azure.com/..."
#   web_configuration:
#     authentication:
#       enable: true
#       username: "prod_admin"
#       password: "STRONG_PRODUCTION_PASSWORD"
#   # ... other production settings
"""
        with open(profiles_path, "w") as f:
            f.write(profiles_content)
        console.print(
            "[info]✅ Created profiles.yml with example configuration.[/info]"
        )
        console.print(
            "[warning]⚠️  Remember to update API keys and passwords in profiles.yml![/warning]"
        )
