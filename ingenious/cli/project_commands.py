"""
Project management CLI commands for Insight Ingenious.

This module provides backward compatibility while delegating to the new command architecture.
"""

from __future__ import annotations

import typer
from rich.console import Console

from ingenious.cli.commands.project import InitCommand


def register_commands(app: typer.Typer, console: Console) -> None:
    """Register project-related commands with the typer app."""

    @app.command(name="init", help="Initialize a new Insight Ingenious project")
    def init():
        """
        🏗️  Initialize a new Insight Ingenious project in the current directory.

        Creates a complete project structure with:
        • config.yml - Project configuration (non-sensitive settings)
        • profiles.yml - Environment profiles (API keys, secrets)
        • .env.example - Example environment variables
        • ingenious_extensions/ - Your custom agents and workflows
        • templates/prompts/quickstart-1/ - Ready-to-use bike-insights workflow templates
        • Dockerfile - Docker containerization setup
        • .dockerignore - Docker build exclusions
        • tmp/ - Temporary files and memory storage

        🎯 INCLUDES: Pre-configured quickstart-1 templates for immediate bike-insights testing!

        NEXT STEPS after running this command:
        1. Copy .env.example to .env and add your credentials
        2. Update config.yml and profiles.yml for your environment
        3. Set environment variables:
           export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
           export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
        4. Start the server: ingen serve

        For detailed configuration help: igen workflows --help
        """
        cmd = InitCommand(console)
        cmd.run()

    # Keep old command for backward compatibility
    @app.command(hidden=True)
    def initialize_new_project():
        """
        Generate template folders for a new project using the Ingenious framework.

        Creates the following structure:
        • config.yml - Project configuration (non-sensitive settings) in project directory
        • profiles.yml - Environment profiles (API keys, secrets) in project directory
        • .env.example - Example environment variables file
        • ingenious_extensions/ - Your custom agents and workflows
        • templates/prompts/quickstart-1/ - Pre-configured bike-insights workflow templates
        • Dockerfile - Docker containerization setup at project root
        • .dockerignore - Docker build exclusions at project root
        • tmp/ - Temporary files and memory

        NEXT STEPS after running this command:
        1. Copy .env.example to .env and fill in your credentials
        2. Update config.yml and profiles.yml as needed for your project
        3. Set environment variables:
           export INGENIOUS_PROJECT_PATH=$(pwd)/config.yml
           export INGENIOUS_PROFILE_PATH=$(pwd)/profiles.yml
        4. Start the server: ingen serve

        For workflow-specific configuration requirements, see:
        docs/workflows/README.md
        """
        cmd = InitCommand(console)
        cmd.run()
