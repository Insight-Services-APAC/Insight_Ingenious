"""
Project management CLI commands for Insight Ingenious.

This module contains commands for initializing projects and managing project structure.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from ingenious.cli.base import BaseCommand, CommandError, ExitCode
from ingenious.cli.utilities import FileOperations, OutputFormatters


class InitCommand(BaseCommand):
    """Initialize a new Insight Ingenious project."""

    def execute(self, **kwargs: Any) -> None:
        """
        Initialize a new Insight Ingenious project in the current directory.

        Creates a complete project structure with:
        • .env.example - Example environment variables for pydantic-settings configuration
        • ingenious_extensions/ - Your custom agents and workflows
        • templates/prompts/quickstart-1/ - Ready-to-use bike-insights workflow templates
        • Dockerfile - Docker containerization setup
        • .dockerignore - Docker build exclusions
        • tmp/ - Temporary files and memory storage

        🎯 INCLUDES: Pre-configured quickstart-1 templates for immediate bike-insights testing!
        """
        self.start_progress("Initializing project structure...")

        try:
            self._create_project_structure()
            self.stop_progress()

            self.print_success("Project initialization completed!")
            self._show_next_steps()

        except Exception as e:
            self.stop_progress()
            raise CommandError(
                f"Project initialization failed: {e}", ExitCode.GENERAL_ERROR
            )

    def _create_project_structure(self) -> None:
        """Create the project directory structure."""
        base_path = Path(__file__).parent.parent.parent
        templates_paths = {
            "ingenious_extensions": base_path / "ingenious_extensions_template",
            "tmp": None,  # No template, just create the folder
        }

        # Create directories from templates
        for folder_name, template_path in templates_paths.items():
            destination = Path.cwd() / folder_name

            # Skip if the destination folder already exists
            if destination.exists():
                self.print_warning(
                    f"Folder '{folder_name}' already exists. Skipping..."
                )
                continue

            # Check if a template path exists (if applicable)
            if template_path and not template_path.exists():
                self.print_warning(
                    f"Template directory '{template_path}' not found. Skipping..."
                )
                continue

            try:
                if template_path:
                    # Copy from template
                    if not FileOperations.copy_tree_safe(template_path, destination):
                        raise OSError(f"Failed to copy template for {folder_name}")
                    self.print_success(f"Created '{folder_name}/' from template")
                else:
                    # Just create the directory
                    FileOperations.ensure_directory(destination, folder_name)
                    self.print_success(f"Created '{folder_name}/' directory")

            except Exception as e:
                raise CommandError(
                    f"Failed to create {folder_name}: {e}", ExitCode.GENERAL_ERROR
                )

        # Create environment configuration files
        self._create_env_files(base_path)

        # Create Docker files
        self._create_docker_files(base_path)

    def _create_env_files(self, base_path: Path) -> None:
        """Create environment configuration files in the project root."""
        env_files = {
            ".env.example": base_path / "config_templates" / ".env.example",
        }

        for filename, template_path in env_files.items():
            destination = Path.cwd() / filename

            if destination.exists():
                self.print_warning(f"File '{filename}' already exists. Skipping...")
                continue

            try:
                if template_path.exists():
                    shutil.copy2(template_path, destination)
                    self.print_success(f"Created '{filename}' from template")
                else:
                    # Create a default file if template doesn't exist
                    self._create_default_env_file(filename, destination)
                    self.print_success(f"Created default '{filename}'")

            except Exception as e:
                self.logger.error(f"Failed to create {filename}: {e}")
                # Don't fail the entire operation for config files

    def _create_docker_files(self, base_path: Path) -> None:
        """Create Docker-related files."""
        docker_files = {
            "Dockerfile": base_path / "docker_templates" / "Dockerfile",
            ".dockerignore": base_path / "docker_templates" / ".dockerignore",
        }

        for filename, template_path in docker_files.items():
            destination = Path.cwd() / filename

            if destination.exists():
                self.print_warning(f"File '{filename}' already exists. Skipping...")
                continue

            try:
                if template_path.exists():
                    shutil.copy2(template_path, destination)
                    self.print_success(f"Created '{filename}' from template")
                else:
                    # Create a basic file if template doesn't exist
                    self._create_default_docker_file(filename, destination)
                    self.print_success(f"Created default '{filename}'")

            except Exception as e:
                self.logger.error(f"Failed to create {filename}: {e}")
                # Don't fail the entire operation for Docker files

    def _create_default_env_file(self, filename: str, destination: Path) -> None:
        """Create a default environment configuration file if template is missing."""
        if filename == ".env.example":
            content = """# Insight Ingenious Configuration
# Environment variables for pydantic-settings configuration
# Copy this file to .env and update with your actual values

# Core AI Model Configuration (REQUIRED)
# API key for your OpenAI or Azure OpenAI service
INGENIOUS_MODELS__0__API_KEY=your-api-key-here
# Base URL for Azure OpenAI (e.g., https://your-resource.openai.azure.com/)
INGENIOUS_MODELS__0__BASE_URL=https://your-resource.openai.azure.com/
# Model name (e.g., gpt-4o-mini, gpt-4, gpt-3.5-turbo)
INGENIOUS_MODELS__0__MODEL=gpt-4o-mini
# Azure OpenAI API version
INGENIOUS_MODELS__0__API_VERSION=2024-02-01
# Azure OpenAI deployment name (usually same as model)
INGENIOUS_MODELS__0__DEPLOYMENT=gpt-4o-mini
# API type for Azure OpenAI
INGENIOUS_MODELS__0__API_TYPE=rest

# Web Server Configuration (OPTIONAL)
# Port for the web server (default: 80)
INGENIOUS_WEB_CONFIGURATION__PORT=80
# IP address to bind (default: 0.0.0.0)
INGENIOUS_WEB_CONFIGURATION__IP_ADDRESS=0.0.0.0
# Enable authentication (default: false)
INGENIOUS_WEB_CONFIGURATION__AUTHENTICATION__ENABLE=false

# Chat History Database (OPTIONAL)
# Database type: sqlite (local) or azuresql (cloud)
INGENIOUS_CHAT_HISTORY__DATABASE_TYPE=sqlite
# Path for local SQLite database
INGENIOUS_CHAT_HISTORY__DATABASE_PATH=./.tmp/chat_history.db
# Memory storage path
INGENIOUS_CHAT_HISTORY__MEMORY_PATH=./.tmp

# Chat Service Configuration (REQUIRED)
# Chat service type for multi-agent workflows
INGENIOUS_CHAT_SERVICE__TYPE=multi_agent

# Logging Configuration (OPTIONAL)
# Log levels: debug, info, warning, error
INGENIOUS_LOGGING__ROOT_LOG_LEVEL=info
INGENIOUS_LOGGING__LOG_LEVEL=info

# Optional: Azure SQL Database (for Azure SQL workflows)
# Change INGENIOUS_CHAT_HISTORY__DATABASE_TYPE to 'azuresql' to enable Azure SQL
# INGENIOUS_AZURE_SQL_SERVICES__DATABASE_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:YOUR_SERVER.database.windows.net,1433;Database=YOUR_DATABASE;Uid=YOUR_USERNAME;Pwd=YOUR_PASSWORD;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;
# INGENIOUS_AZURE_SQL_SERVICES__DATABASE_NAME=your_database_name
# INGENIOUS_AZURE_SQL_SERVICES__TABLE_NAME=chat_history

# Optional: Azure Search (for knowledge-base workflows)
# INGENIOUS_AZURE_SEARCH_SERVICES__0__KEY=your-search-api-key
# INGENIOUS_AZURE_SEARCH_SERVICES__0__ENDPOINT=https://your-search-service.search.windows.net

# Optional: Local SQL Database path for sql-manipulation workflows
# INGENIOUS_LOCAL_SQL_DB__DATABASE_PATH=/tmp/sample_sql.db

# Optional: Scrapfly API for dataprep commands
# SCRAPFLY_API_KEY=your-scrapfly-api-key

# Optional: Azure Blob Storage (for cloud-based file storage)
# Change INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE to 'azure' to enable
# INGENIOUS_FILE_STORAGE__REVISIONS__ENABLE=true
# INGENIOUS_FILE_STORAGE__REVISIONS__STORAGE_TYPE=azure
# INGENIOUS_FILE_STORAGE__REVISIONS__CONTAINER_NAME=prompts
# INGENIOUS_FILE_STORAGE__REVISIONS__PATH=./
# INGENIOUS_FILE_STORAGE__REVISIONS__URL=https://YOUR_STORAGE_ACCOUNT.blob.core.windows.net
# INGENIOUS_FILE_STORAGE__REVISIONS__TOKEN=DefaultEndpointsProtocol=https;AccountName=YOUR_ACCOUNT;AccountKey=YOUR_KEY;EndpointSuffix=core.windows.net

# Legacy Configuration Migration
# If you have existing config.yml and profiles.yml files, you can migrate them using:
# uv run python scripts/migrate_config.py --yaml-file config.yml --output .env
"""
        else:
            content = f"# {filename} - Created by Insight Ingenious\n"

        with open(destination, "w") as f:
            f.write(content)

    def _create_default_docker_file(self, filename: str, destination: Path) -> None:
        """Create a default Docker file if template is missing."""
        if filename == "Dockerfile":
            content = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 80

# Run the application
CMD ["python", "-m", "ingenious.cli", "serve"]
"""
        elif filename == ".dockerignore":
            content = """.git
.gitignore
README.md
.env
.env.*
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.venv
.pytest_cache
.mypy_cache
"""
        else:
            content = f"# {filename} - Created by Insight Ingenious\n"

        with open(destination, "w") as f:
            f.write(content)

    def _show_next_steps(self) -> None:
        """Show next steps after project initialization."""
        next_steps = [
            "1. Copy .env.example to .env and add your credentials:",
            "   cp .env.example .env",
            "2. Edit .env file with your API keys and configuration",
            "3. Validate your configuration:",
            "   ingen validate",
            "4. Start the server:",
            "   ingen serve",
            "5. Test the sample bike-insights workflow:",
            "   curl -X POST http://localhost:80/api/v1/chat \\",
            "     -H 'Content-Type: application/json' \\",
            '     -d \'{"user_prompt": "Analyze bike sales", "conversation_flow": "bike-insights"}\'',
        ]

        panel = OutputFormatters.create_info_panel(
            "\n".join(next_steps), "🚀 Next Steps", "green"
        )
        self.console.print(panel)

        self.console.print(
            "\n[bold yellow]💡 Migration from YAML configuration:[/bold yellow]"
        )
        self.console.print("   If you have existing config.yml and profiles.yml files:")
        self.console.print(
            "   uv run python scripts/migrate_config.py --yaml-file config.yml --output .env"
        )

        self.console.print(
            "\n[bold yellow]💡 For detailed configuration help:[/bold yellow]"
        )
        self.console.print("   ingen workflows --help")


# Backward compatibility functions
def register_commands(app: Any, console: Any) -> None:
    """Register project-related commands with the typer app."""

    @app.command(name="init", help="Initialize a new Insight Ingenious project")  # type: ignore[misc]
    def init() -> None:
        """
        🏗️  Initialize a new Insight Ingenious project in the current directory.

        Creates a complete project structure with:
        • .env.example - Example environment variables for pydantic-settings configuration
        • ingenious_extensions/ - Your custom agents and workflows
        • templates/prompts/quickstart-1/ - Ready-to-use bike-insights workflow templates
        • Dockerfile - Docker containerization setup
        • .dockerignore - Docker build exclusions
        • tmp/ - Temporary files and memory storage

        🎯 INCLUDES: Pre-configured quickstart-1 templates for immediate bike-insights testing!

        NEXT STEPS after running this command:
        1. Copy .env.example to .env and add your credentials
        2. Edit .env file with your API keys and configuration
        3. Validate your configuration: ingen validate
        4. Start the server: ingen serve

        For detailed configuration help: ingen workflows --help
        """
        cmd = InitCommand(console)
        cmd.run()

    # Keep old command for backward compatibility
    @app.command(hidden=True)  # type: ignore[misc]
    def initialize_new_project() -> None:
        """Legacy command that delegates to the new init command."""
        cmd = InitCommand(console)
        cmd.run()
