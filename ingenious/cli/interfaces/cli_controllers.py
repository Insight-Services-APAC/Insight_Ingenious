"""
CLI controllers.

This module contains the interface controllers that handle CLI command interactions
and coordinate with the application layer.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.theme import Theme
from typing_extensions import Annotated

from ..application.services import CLIApplicationService

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


class CLIController:
    """Controller for handling CLI commands."""

    def __init__(self, cli_service: CLIApplicationService):
        self._cli_service = cli_service
        self.app = typer.Typer(
            no_args_is_help=True, pretty_exceptions_show_locals=False
        )
        self._register_commands()

    def _register_commands(self) -> None:
        """Register all CLI commands."""
        # Commands are registered in main.py with async wrapper
        pass

    async def run(
        self,
        project_dir: Annotated[
            Optional[str],
            typer.Option(
                "--project-dir",
                help="Path to config.yml file. Defaults to ./config.yml",
            ),
        ] = None,
        profile_dir: Annotated[
            Optional[str],
            typer.Option(
                "--profile-dir",
                help="Path to profiles.yml file. Defaults to ./profiles.yml",
            ),
        ] = None,
        host: Annotated[
            str,
            typer.Option(
                "--host", help="Host to bind to. Use 127.0.0.1 for local development"
            ),
        ] = "127.0.0.1",
        port: Annotated[
            int,
            typer.Option("--port", help="Port to run the server on"),
        ] = 8000,
    ) -> None:
        """
        Start the Insight Ingenious server.

        This command starts the REST API server that provides the core functionality
        for AI agent interactions and file management.
        """
        try:
            await self._cli_service.start_rest_api_server(
                project_dir=project_dir,
                profile_dir=profile_dir,
                host=host,
                port=port,
            )
        except Exception as e:
            console.print(f"[error]❌ Failed to start server: {e}[/error]")
            raise typer.Exit(1)

    async def dev(self) -> None:
        """
        Quick development mode - run the project in the current directory.

        This is a simplified command that starts the server with default settings
        for the current project directory.
        """
        try:
            await self._cli_service.run_project()
        except Exception as e:
            console.print(f"[error]❌ Failed to run project: {e}[/error]")
            raise typer.Exit(1)

    async def init(self) -> None:
        """
        Initialize a new Insight Ingenious project.

        This command creates the necessary configuration files and directory
        structure for a new project in the current directory.
        """
        try:
            await self._cli_service.initialize_new_project()

            current_dir = Path.cwd()
            project_name = current_dir.name

            self._print_completion_message(current_dir, project_name)

        except Exception as e:
            console.print(f"[error]❌ Failed to initialize project: {e}[/error]")
            raise typer.Exit(1)

    def _print_completion_message(self, current_dir: Path, project_name: str) -> None:
        """Print completion message after project initialization."""
        console.print()
        console.print("🎉 [bold green]Project initialization complete![/bold green]")
        console.print()
        console.print(f"📁 Project: [bold]{project_name}[/bold]")
        console.print(f"📂 Location: [dim]{current_dir}[/dim]")
        console.print()
        console.print("📋 [bold]Files created:[/bold]")
        console.print("   ✅ config.yml - Main configuration")
        console.print("   ✅ profiles.yml - API keys and secrets")
        console.print("   ✅ .gitignore - Git ignore rules")
        console.print("   ✅ SETUP.md - Setup instructions")
        console.print()
        console.print("🚀 [bold]Next steps:[/bold]")
        console.print(
            "   1️⃣ Edit [bold]profiles.yml[/bold] and add your Azure OpenAI API key"
        )
        console.print("   2️⃣ Run: [bold]ingen run[/bold]")
        console.print("   3️⃣ Visit: [link]http://127.0.0.1:8000/docs[/link]")
        console.print()
        console.print("📖 For detailed setup instructions, see [bold]SETUP.md[/bold]")
        console.print()
        console.print(
            "⚠️  [bold yellow]Remember:[/bold yellow] Keep [bold]profiles.yml[/bold] secure (contains API keys)"
        )
        console.print()
